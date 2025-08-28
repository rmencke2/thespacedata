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

# name_generator/services.py
import os, re, json, logging
from openai import OpenAI
logger = logging.getLogger(__name__)

_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY")) if os.getenv("OPENAI_API_KEY") else None

def openai_generate(description: str, keywords: str, industry: str, style: str, count: int = 6):
    if not _client:
        return None
    try:
        desc = description.strip() or "—"
        kw   = (keywords or "—").strip()
        ind  = (industry or "general").strip()
        sty  = (style or "any").strip()

        prompt = f"""
You are a world-class branding consultant. Generate {count} creative, memorable, high-quality business names.

Guidelines:
- 1–3 words, catchy, easy to pronounce and spell.
- Avoid clichés and overused suffixes (-ify, -ly, -ster).
- Clever wordplay, metaphor, and subtle mashups welcome.
- Suitable for .com and social handles (avoid numbers/hyphens).
- Return ONLY a list of names, one per line. No bullets, no numbering, no explanations.

User description: {desc}
Keywords: {kw}
Industry: {ind}
Style: {sty}
"""

        resp = _client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.9,
        )
        text = resp.choices[0].message.content.strip()

        # Parse as lines (robust even if model adds bullets)
        lines = [re.sub(r"^[•\-\d\)\.]+\s*", "", ln).strip() for ln in text.splitlines() if ln.strip()]
        return lines[:count] or None

    except Exception:
        logger.exception("OpenAI name generation failed")
        return None

def local_generate(keywords: str, industry: str, style: str, count: int = 6):
    # (your existing local fallback)
    base = ["Sip & Savor", "Vin & Bread", "Café Vignette", "Artisan Blend", "The Luxe Bite", "Crust & Cork"]
    return base[:count]