# name_generator/services.py
from __future__ import annotations

import json
import logging
from typing import List, Optional

from django.conf import settings

log = logging.getLogger(__name__)

# Best-effort import across SDK versions
try:
    from openai import OpenAI  # new SDK
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore

def _openai_client() -> Optional["OpenAI"]:
    key = getattr(settings, "OPENAI_API_KEY", "") or ""
    if not key:
        log.error("OPENAI_API_KEY is missing; returning None client.")
        return None
    if not OpenAI:
        log.error("OpenAI SDK not available; returning None client.")
        return None
    try:
        return OpenAI(api_key=key)
    except Exception as e:  # pragma: no cover
        log.exception("Failed to init OpenAI client: %s", e)
        return None

def _postprocess(raw: str, count: int) -> List[str]:
    """
    Accepts either a JSON array of strings or free text and extracts up to 'count' names.
    """
    # Try to locate a JSON array in the text first
    try:
        # Sometimes models wrap the array with extra text; try to find the first '[' ... ']'
        start = raw.find("[")
        end = raw.rfind("]")
        if start != -1 and end != -1 and end > start:
            arr = json.loads(raw[start : end + 1])
            if isinstance(arr, list):
                items = [str(x).strip() for x in arr if str(x).strip()]
                return items[:count]
    except Exception:
        pass

    # Fallback: split lines / commas
    # Grab non-empty parts and dedupe while preserving order
    seen = set()
    out: List[str] = []
    for chunk in raw.replace("\r", "\n").split("\n"):
        for piece in chunk.split(","):
            name = piece.strip(" -•\t ")
            if name and name.lower() not in seen:
                seen.add(name.lower())
                out.append(name)
            if len(out) >= count:
                break
        if len(out) >= count:
            break
    return out[:count]

def generate_names(industry: str, vibe: str, count: int = 10) -> List[str]:
    """
    Generate brand names using the configured OpenAI model.
    Never raises to the view layer; returns [] and logs on error.
    """
    client = _openai_client()
    if not client:
        return []

    model = getattr(settings, "OPENAI_MODEL", "gpt-5-nano")

    system = (
        "You generate catchy, brandable company names. "
        "Return either a JSON array of strings or a short, comma-separated list."
    )
    user = (
        f"Industry: {industry or 'general'}\n"
        f"Vibe: {vibe or 'modern'}\n"
        f"Count: {count}\n"
        "Please keep each name short (1–3 words)."
    )

    try:
        # New SDK (Responses API style)
        resp = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        text = ""
        try:
            # Typical happy-path extraction:
            text = resp.output_text  # property provided by the SDK
        except Exception:
            # Fallback: dig into the structure if output_text is absent
            text = str(resp)
        names = _postprocess(text, count)
        log.info("Generated %d names", len(names))
        return names
    except Exception as e:
        log.exception("OpenAI call failed: %s", e)
        return []