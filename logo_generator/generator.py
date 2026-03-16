# logo_generator/generator.py
"""
Utilities for generating logo concepts with OpenAI Images API.

- prompt_from_brief(brief) -> str
- generate_logo_pngs(brief, count=4) -> (List[bytes], Optional[str])
    Returns PNG bytes for each concept, and an error code:
      None | "missing_api_key" | "openai_error"

- save_previews(concept_queryset, png_bytes_list)
    Saves generated PNGs to a model FileField/ImageField named `preview_png`.
"""

from __future__ import annotations

import base64
import io
from typing import List, Optional, Tuple

from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image
from openai import OpenAI


# Single shared client; you can also instantiate inside the function if preferred.
_client = OpenAI(api_key=settings.OPENAI_API_KEY)


def _to_png_bytes(img_bytes: bytes) -> bytes:
    """
    Ensure the image is saved as RGBA PNG.
    Most OpenAI image outputs are already PNG, but this safeguards consistency.
    """
    with Image.open(io.BytesIO(img_bytes)) as im:
        if im.mode != "RGBA":
            im = im.convert("RGBA")
        out = io.BytesIO()
        im.save(out, format="PNG")
        return out.getvalue()


def prompt_from_brief(brief: dict) -> str:
    """
    Build a concise, directive prompt for the image model from a user brief.
    Keep it short and specific; image models respond better to succinct directions.
    """
    lines = [
        f"Brand name: {brief.get('brand_name', '').strip()}",
        f"Tagline: {brief.get('tagline', '').strip()}",
        f"Industry: {brief.get('industry', '').strip()}",
        f"Values: {brief.get('values', '').strip()}",
        f"Style keywords: {brief.get('style_keywords', '').strip()}",
        f"Color constraints: {brief.get('colors', '').strip()}",
        f"Icon ideas: {brief.get('icon_ideas', '').strip()}",
    ]

    # Remove empty items (e.g., "X: " with nothing after)
    parts = [s for s in lines if s and not s.endswith(": ") and not s.endswith(":")]
    # Final prompt
    return (
        "Design a clean, modern, professional logo. Avoid photorealism. "
        "Return a centered mark on a transparent or light background. "
        + " ".join(parts)
    )


def generate_logo_pngs(brief: dict, count: int = 4) -> Tuple[List[bytes], Optional[str]]:
    """
    Generate `count` logo concepts as PNG bytes using OpenAI Images API.

    Returns:
        (images, error_code) where error_code is None | "missing_api_key" | "openai_error"
    """
    api_key = settings.OPENAI_API_KEY
    if not api_key:
        return [], "missing_api_key"

    try:
        prompt = prompt_from_brief(brief)

        # Do NOT pass response_format; SDK returns b64_json by default.
        resp = _client.images.generate(
            model="gpt-image-1",
            prompt=prompt,
            size="1024x1024",
            n=count,
        )

        images: List[bytes] = []
        for item in resp.data:
            # New SDK returns objects with .b64_json (preferred) OR sometimes a URL.
            b64 = getattr(item, "b64_json", None)
            if b64:  # happy path
                raw = base64.b64decode(b64)
                images.append(_to_png_bytes(raw))
                continue

            # Fallback if a URL is returned (rare in current SDK).
            url = getattr(item, "url", None)
            if url:
                import requests
                r = requests.get(url, timeout=30)
                r.raise_for_status()
                images.append(_to_png_bytes(r.content))

        return images, None

    except Exception as exc:  # keep a broad guard while iterating
        print("OpenAI image generation failed:", repr(exc))
        return [], "openai_error"


def save_previews(concept_queryset, png_bytes_list: List[bytes]) -> None:
    """
    Save the generated PNG bytes to each concept's `preview_png` field.

    Expects:
      - concept_queryset: iterable of model instances with a File/ImageField
        named `preview_png`
      - png_bytes_list: list of PNG byte blobs, typically from generate_logo_pngs

    Lengths are zipped (shortest wins).
    """
    for concept, png_bytes in zip(concept_queryset, png_bytes_list):
        concept.preview_png.save(
            f"concept_{concept.id}.png",
            ContentFile(png_bytes),
            save=True,
        )