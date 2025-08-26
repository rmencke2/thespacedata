import os
import json
import re
import logging

from openai import OpenAI

logger = logging.getLogger(__name__)

_client = None
api_key = os.getenv("OPENAI_API_KEY")
if api_key:
    _client = OpenAI(api_key=api_key)
else:
    logger.warning("OPENAI_API_KEY not set; falling back to local generator.")

def openai_generate(keywords: str, industry: str, style: str, count: int = 6):
    """Return a list of names or None on failure."""
    if not _client:
        return None
    try:
        prompt = (
            "Generate creative, brandable business names as a JSON array of strings only. "
            "Avoid explanations or numbering. "
            f"Keywords: {keywords or '—'}. "
            f"Industry: {industry or '—'}. "
            f"Style: {style or '—'}. "
            f"Count: {count}."
        )

        resp = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a concise brand-naming assistant."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.9,
        )

        text = resp.choices[0].message.content.strip()

        # Try to extract a JSON array if the model returns extra text
        m = re.search(r"\[[\s\S]*\]", text)
        if m:
            text = m.group(0)

        arr = json.loads(text) if text.startswith("[") else []
        names = [s.strip() for s in arr if isinstance(s, str)]
        return names[:count] if names else None

    except Exception:
        logger.exception("OpenAI name generation failed")
        return None

def local_generate(keywords: str, industry: str, style: str, count: int = 6):
    # (your existing local fallback)
    base = ["Sip & Savor", "Vin & Bread", "Café Vignette", "Artisan Blend", "The Luxe Bite", "Crust & Cork"]
    return base[:count]