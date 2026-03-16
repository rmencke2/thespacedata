# name_generator/services.py
"""
Name generation service.

Public API:
    - generate_names(industry: str, vibe: str, count: int = 10) -> list[str]

Contract:
    - Returns a list of up to `count` names.
    - Raises ServiceError on configuration or API failures so the view can decide
      how to surface errors to the user.
"""

from __future__ import annotations

import json
import logging
from typing import List, Optional

from django.conf import settings

log = logging.getLogger(__name__)

__all__ = ["ServiceError", "generate_names"]

# -----------------------------------------------------------------------------
# Exceptions
# -----------------------------------------------------------------------------
class ServiceError(Exception):
    """Raised when the name-generation service cannot complete."""


# -----------------------------------------------------------------------------
# OpenAI client bootstrap (new SDK first, fall back to legacy if needed)
# -----------------------------------------------------------------------------
try:
    from openai import OpenAI  # New SDK (responses API)
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore

def _openai_client() -> Optional["OpenAI"]:
    """
    Initialize the OpenAI client using settings.OPENAI_API_KEY.
    Returns None if unavailable; callers should raise ServiceError.
    """
    key = getattr(settings, "OPENAI_API_KEY", "") or ""
    if not key:
        log.error("OPENAI_API_KEY is missing.")
        return None
    if not OpenAI:
        log.error("OpenAI SDK is not installed or could not be imported.")
        return None
    try:
        return OpenAI(api_key=key)
    except Exception as e:  # pragma: no cover
        log.exception("Failed to init OpenAI client: %s", e)
        return None


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------
def _postprocess(raw: str, count: int) -> List[str]:
    """
    Accept a model response (either JSON array or free text) and extract
    up to `count` names.

    Strategy:
      1) Try to parse a JSON array anywhere within the text.
      2) Fallback to splitting by lines/commas, trimming bullets/dashes.
      3) Dedupe case-insensitively, keep original order.
    """
    # 1) Look for a JSON array
    try:
        start = raw.find("[")
        end = raw.rfind("]")
        if start != -1 and end != -1 and end > start:
            arr = json.loads(raw[start : end + 1])
            if isinstance(arr, list):
                items = [str(x).strip() for x in arr if str(x).strip()]
                return items[:count]
    except Exception:
        # Not JSON or malformed — continue to fallback
        pass

    # 2) Fallback free-text parse
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


# -----------------------------------------------------------------------------
# Public API
# -----------------------------------------------------------------------------
def generate_names(industry: str, vibe: str, count: int = 10) -> List[str]:
    """
    Generate brand names with the configured OpenAI model.

    Raises:
        ServiceError: when configuration is missing or the API request fails.

    Returns:
        List[str]: up to `count` names.
    """
    if count <= 0:
        raise ServiceError("Count must be >= 1")

    client = _openai_client()
    if not client:
        raise ServiceError("OpenAI client unavailable")

    model = getattr(settings, "OPENAI_MODEL", "gpt-5-nano")
    system_msg = (
        "You generate catchy, brandable company names. "
        "Respond with a JSON array of strings if possible; otherwise a short, "
        "comma-separated list. Keep each name 1–3 words."
    )
    user_msg = (
        f"Industry: {industry or 'general'}\n"
        f"Vibe: {vibe or 'modern'}\n"
        f"Count: {count}"
    )

    # Try new Responses API first; if that fails, attempt legacy structures.
    try:
        # New SDK (Responses API). The SDK typically exposes `output_text`.
        resp = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": user_msg},
            ],
        )
        try:
            text = resp.output_text  # type: ignore[attr-defined]
        except Exception:
            # As a fallback, stringify the response (handles SDK variations).
            text = str(resp)

        names = _postprocess(text, count)
        log.info("Generated %d names via %s", len(names), model)
        if not names:
            raise ServiceError("Model returned no parseable names")
        return names

    except Exception as e:
        log.exception("OpenAI call failed: %s", e)
        raise ServiceError("OpenAI call failed") from e


# -----------------------------------------------------------------------------
# Optional: variant that never raises (use in views if you prefer)
# -----------------------------------------------------------------------------
def generate_names_or_empty(industry: str, vibe: str, count: int = 10) -> List[str]:
    """
    Wrapper around `generate_names` that swallows errors and returns [].
    Useful for graceful UI degradation.
    """
    try:
        return generate_names(industry, vibe, count)
    except ServiceError as e:
        log.warning("Name generation failed: %s", e)
        return []