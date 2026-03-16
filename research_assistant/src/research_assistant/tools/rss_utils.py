"""RSS/Atom utilities for pulling recent competitor updates without a search API.

This module is intentionally dependency-free (std-lib + httpx).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
import re
from typing import Iterable
from urllib.parse import urljoin
import xml.etree.ElementTree as ET

import httpx


@dataclass(frozen=True)
class FeedEntry:
    title: str
    url: str
    published_at: datetime | None
    source: str  # feed URL


_RSS_LINK_RE = re.compile(
    r"""<link[^>]+rel=["']alternate["'][^>]+type=["']application/(?:rss\+xml|atom\+xml)["'][^>]*>""",
    re.IGNORECASE,
)
_HREF_RE = re.compile(r"""href=["']([^"']+)["']""", re.IGNORECASE)


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _to_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _parse_datetime(value: str | None) -> datetime | None:
    if not value:
        return None
    value = value.strip()

    # RSS: "Tue, 20 Jan 2026 10:30:00 GMT"
    try:
        dt = parsedate_to_datetime(value)
        return _to_utc(dt)
    except Exception:
        pass

    # Atom: ISO 8601
    try:
        # Handle "Z"
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        dt = datetime.fromisoformat(value)
        return _to_utc(dt)
    except Exception:
        return None


def _extract_feed_candidates(blog_url: str) -> list[str]:
    """Generate likely RSS/Atom feed URLs for a given blog URL."""
    blog_url = blog_url.strip()
    candidates: list[str] = []

    # Common feed endpoints
    common_paths = [
        "feed",
        "feed/",
        "rss",
        "rss/",
        "rss.xml",
        "atom.xml",
        "blog/feed",
        "blog/feed/",
        "blog/rss",
        "blog/rss/",
        "blog/rss.xml",
        "blog/atom.xml",
    ]

    # Prefer joining relative to the blog URL.
    for p in common_paths:
        candidates.append(urljoin(blog_url.rstrip("/") + "/", p))

    # Also try root-level variants.
    try:
        # urljoin with "/" uses scheme+netloc root
        root = urljoin(blog_url, "/")
        for p in common_paths:
            candidates.append(urljoin(root, p))
    except Exception:
        pass

    # De-dupe while preserving order.
    seen: set[str] = set()
    out: list[str] = []
    for u in candidates:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def _discover_feed_urls_from_html(html: str, base_url: str) -> list[str]:
    """Best-effort discovery of RSS/Atom links from a page."""
    urls: list[str] = []
    for m in _RSS_LINK_RE.finditer(html):
        tag = m.group(0)
        href_m = _HREF_RE.search(tag)
        if not href_m:
            continue
        href = href_m.group(1).strip()
        if not href:
            continue
        urls.append(urljoin(base_url, href))

    # De-dupe
    seen: set[str] = set()
    out: list[str] = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def _parse_rss_or_atom(xml_bytes: bytes, feed_url: str) -> list[FeedEntry]:
    """Parse RSS2 or Atom feeds into a list of entries."""
    try:
        root = ET.fromstring(xml_bytes)
    except Exception:
        return []

    # Helper to strip namespaces
    def strip_ns(tag: str) -> str:
        return tag.split("}", 1)[-1] if "}" in tag else tag

    root_tag = strip_ns(root.tag).lower()
    entries: list[FeedEntry] = []

    if root_tag == "rss":
        channel = next((c for c in root if strip_ns(c.tag).lower() == "channel"), None)
        if channel is None:
            return []
        for item in channel:
            if strip_ns(item.tag).lower() != "item":
                continue
            title = ""
            link = ""
            pub = None
            for child in item:
                t = strip_ns(child.tag).lower()
                if t == "title" and child.text:
                    title = child.text.strip()
                elif t == "link" and child.text:
                    link = child.text.strip()
                elif t == "pubdate" and child.text:
                    pub = _parse_datetime(child.text)
            if title and link:
                entries.append(FeedEntry(title=title, url=link, published_at=pub, source=feed_url))

    elif root_tag == "feed":  # Atom
        for entry in root:
            if strip_ns(entry.tag).lower() != "entry":
                continue
            title = ""
            link = ""
            pub = None
            for child in entry:
                t = strip_ns(child.tag).lower()
                if t == "title" and child.text:
                    title = child.text.strip()
                elif t == "link":
                    href = child.attrib.get("href")
                    rel = (child.attrib.get("rel") or "").lower()
                    # Prefer alternate/self links if present
                    if href and (not rel or rel == "alternate"):
                        link = href.strip()
                elif t in ("updated", "published") and child.text and pub is None:
                    pub = _parse_datetime(child.text)
            if title and link:
                entries.append(FeedEntry(title=title, url=link, published_at=pub, source=feed_url))

    return entries


def fetch_recent_feed_entries(
    blog_url: str,
    days_back: int = 14,
    max_items: int = 10,
    *,
    timeout_s: int = 20,
) -> list[FeedEntry]:
    """Fetch and parse recent entries from a competitor blog.

    Tries:
    - Discover RSS/Atom links from the blog page
    - Fall back to common feed endpoints
    """
    if not blog_url:
        return []

    cutoff = _now_utc() - timedelta(days=days_back)

    discovered: list[str] = []
    candidates = _extract_feed_candidates(blog_url)

    with httpx.Client(follow_redirects=True, timeout=timeout_s) as client:
        # Try discovery first (best quality when available)
        try:
            r = client.get(blog_url, headers={"User-Agent": "research-assistant/0.1 (+rss)"})
            if r.status_code < 400 and r.text:
                discovered = _discover_feed_urls_from_html(r.text, blog_url)
        except Exception:
            discovered = []

        feed_urls: list[str] = []
        for u in discovered + candidates:
            if u not in feed_urls:
                feed_urls.append(u)

        all_entries: list[FeedEntry] = []
        for feed_url in feed_urls[:12]:  # avoid too many network calls
            try:
                resp = client.get(feed_url, headers={"User-Agent": "research-assistant/0.1 (+rss)"})
                if resp.status_code >= 400 or not resp.content:
                    continue
                parsed = _parse_rss_or_atom(resp.content, feed_url)
                if parsed:
                    all_entries.extend(parsed)
                    # If we got a usable feed, no need to try many more.
                    break
            except Exception:
                continue

    # Filter + sort
    def entry_dt(e: FeedEntry) -> datetime:
        return e.published_at or datetime.min.replace(tzinfo=timezone.utc)

    recent: list[FeedEntry] = []
    for e in all_entries:
        dt = e.published_at
        if dt is None or dt >= cutoff:
            recent.append(e)

    recent.sort(key=entry_dt, reverse=True)
    return recent[:max_items]


def format_feed_entries(entries: Iterable[FeedEntry], heading: str) -> str:
    items = list(entries)
    if not items:
        return f"{heading}\n\nNo recent feed entries found."

    lines: list[str] = [heading, ""]
    for e in items:
        when = e.published_at.isoformat() if e.published_at else "Unknown date"
        lines.append(f"- **{e.title}**")
        lines.append(f"  - URL: {e.url}")
        lines.append(f"  - Published: {when}")
        lines.append(f"  - Source feed: {e.source}")
    return "\n".join(lines)

