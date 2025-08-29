# name_generator/services.py

from __future__ import annotations

import json
import logging
import re
from typing import List, Optional

from django.conf import settings

logger = logging.getLogger(__name__)

# ---- Configuration from settings -------------------------------------------

OPENAI_API_KEY: str = getattr(settings, "OPENAI_API_KEY", "").strip()
OPENAI_BASE: str = getattr(settings, "OPENAI_BASE", "").strip()  # optional: Azure/OpenRouter, etc.
OPENAI_MODEL: str = getattr(settings, "OPENAI_MODEL", "gpt-4o-mini").strip()  # pick your default


# ---- OpenAI client bootstrap ------------------------------------------------

try:
    from openai import OpenAI  # official Python SDK (>=1.0)
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore


def _build_client():
    """
    Return an OpenAI client instance or raise a RuntimeError with a helpful message.
    We keep this in a function so failures don’t crash module import.
    """
    if OpenAI is None:
        raise RuntimeError(
            "OpenAI SDK is not installed. Add `openai` to your requirements.txt."
        )
    if not OPENAI_API_KEY:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it as an App Runner env var and rebuild."
        )

    kwargs = {"api_key": OPENAI_API_KEY}
    if OPENAI_BASE:
        kwargs["base_url"] = OPENAI_BASE

    return OpenAI(**kwargs)


# Create a module-level client but don’t explode on import.
# If it fails, we log and retry inside the request path.
_client = None
try:
    _client = _build_client()
except Exception as e:  # pragma: no cover
    logger.error("OpenAI client init failed: %s", e)


# ---- Helpers ----------------------------------------------------------------

_JSON_ARRAY_RE = re.compile(r"\[[\s\S]*\]")  # tolerant JSON array capture


def _postprocess(raw: str, count: int) -> List[str]:
    """
    Extract a clean list of names from either JSON or free-form text.

    Strategy:
      1) Prefer a JSON array anywhere in the text
      2) Otherwise parse bullet/numbered/comma-separated lines
      3) De-dupe, trim, filter empties, limit to `count`
    """
    raw = (raw or "").strip()

    # Try to find a JSON array within the text
    m = _JSON_ARRAY_RE.search(raw)
    if m:
        try:
            arr = json.loads(m.group(0))
            if isinstance(arr, list):
                items = [str(x).strip() for x in arr]
                items = [x for x in items if x]
                # de-dupe preserving order
                seen = set()
                uniq = []
                for x in items:
                    if x.lower() not in seen:
                        uniq.append(x)
                        seen.add(x.lower())
                return uniq[:count]
        except Exception:
            pass  # fall back to text parsing

    # Fallback: split by lines or commas, strip list markers
    candidates: List[str] = []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        # remove bullets / numbers like "1. " "- " "* "
        line = re.sub(r"^\s*[-*•]\s*", "", line)
        line = re.sub(r"^\s*\d+\.\s*", "", line)
        # Sometimes lines are comma-separated phrases
        parts = [p.strip() for p in re.split(r",\s*", line) if p.strip()]
        candidates.extend(parts)

    # If still nothing, try one big comma split
    if not candidates and "," in raw:
        candidates = [p.strip() for p in raw.split(",") if p.strip()]

    # De-dupe + trim
    seen2 = set()
    out: List[str] = []
    for x in candidates:
        if not x:
            continue
        key = x.lower()
        if key not in seen2:
            out.append(x)
            seen2.add(key)

    return out[:count]


def _compose_prompt(topic: str, count: int, style: Optional[str], language: str) -> str:
    style_part = f" in the style '{style}'" if style else ""
    return (
        f"Generate {count} distinct brand/startup names for: {topic}."
        f"{style_part} Reply primarily with a JSON array of strings."
        f" If you include any extra commentary, keep it brief."
        f" Language: {language}."
    )


# ---- Public API --------------------------------------------------------------

class NameGenError(RuntimeError):
    """Raised for user-visible name generation errors."""


def generate_names(
    topic: str,
    count: int = 10,
    *,
    style: Optional[str] = None,
    language: str = "English",
    temperature: float = 0.8,
) -> List[str]:
    """
    Generate `count` brand names from a topic.
    Raises NameGenError with a helpful message if LLM is unavailable.
    """
    global _client
    if not topic or not topic.strip():
        raise NameGenError("Please provide a non-empty topic.")

    # Ensure client is ready (support late binding if env changes)
    if _client is None:
        try:
            _client = _build_client()
        except Exception as e:
            logger.error("OpenAI client unavailable: %s", e)
            raise NameGenError(
                "Name generator is temporarily unavailable (LLM credentials/config missing)."
            ) from e

    user_prompt = _compose_prompt(topic.strip(), count, style, language)

    # Prefer chat.completions (modern SDK)
    try:
        resp = _client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a creative but concise brand naming assistant. "
                        "Return short, punchy names. Prefer JSON array output."
                    ),
                },
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
        )
        raw = resp.choices[0].message.content or ""
        names = _postprocess(raw, count)
        if not names:
            # Give one more try with a different instruction style
            resp2 = _client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "Return ONLY a JSON array of strings."},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
            )
            raw2 = resp2.choices[0].message.content or ""
            names = _postprocess(raw2, count)

        if not names:
            raise NameGenError("The model returned no usable names. Try again.")

        return names

    except NameGenError:
        raise
    except Exception as e:
        logger.exception("OpenAI call failed")
        raise NameGenError("Name generator failed while calling the LLM.") from e