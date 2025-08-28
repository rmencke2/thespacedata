# name_generator/services.py
import json, re
from typing import List
from django.conf import settings

try:
    from openai import OpenAI
except Exception:  # older SDKs
    OpenAI = None  # type: ignore

_client = OpenAI(api_key=settings.OPENAI_API_KEY) if (OpenAI and settings.OPENAI_API_KEY) else None


def _postprocess(raw: str, count: int) -> List[str]:
    """Extract a clean list of names from either JSON or plain text."""
    # Try JSON array first (allow extra text around it)
    try:
        m = re.search(r"\[.*\]", raw, re.S)
        if m:
            arr = json.loads(m.group(0))
            cand = [str(x).strip() for x in arr if str(x).strip()]
        else:
            cand = []
    except Exception:
        cand = []

    if not cand:
        # Fallback: split lines & strip bullets/numbers
        cand = []
        for line in raw.splitlines():
            line = line.strip()
            line = re.sub(r"^[\s\-•\u2022]*\d{0,3}[.)\-\s]*", "", line)  # remove leading "1. ", "- ", etc.
            if line:
                cand.append(line)

    # Deduplicate, keep order, cap count
    seen, out = set(), []
    for n in cand:
        if n not in seen:
            seen.add(n)
            out.append(n)
            if len(out) >= count:
                break
    return out


def openai_generate(prompt: str, count: int = 10) -> List[str]:
    """
    Generate business names. Uses Responses API if present; otherwise falls back
    to Chat Completions. Returns a list (may be empty on error).
    """
    if not _client:
        return []

    try:
        sys = (
            "You are a creative brand naming assistant. "
            f"Return exactly {count} strong, brandable business names. "
            "Avoid long names, awkward puns, existing well-known brands, and domain hacks. "
            "Prefer 1–3 words, easy to pronounce. Output a JSON array of strings only."
        )

        if hasattr(_client, "responses"):
            # Newer SDKs
            resp = _client.responses.create(
                #model="gpt-4o-mini",
                model="gpt-5-nano",
                input=[
                    {"role": "system", "content": sys},
                    {"role": "user", "content": prompt},
                ],
            )
            # Most SDKs expose a convenience accessor:
            text = getattr(resp, "output_text", None)
            if not text:
                # Robust extraction if output_text isn't present
                # (pick the first text item we can find)
                text = ""
                if getattr(resp, "output", None):
                    parts = getattr(resp, "output", [])
                    for p in parts:
                        if getattr(p, "content", None):
                            for c in p.content:
                                if getattr(c, "text", None):
                                    text = c.text
                                    break
                            if text:
                                break
        else:
            # Older SDKs – Chat Completions
            resp = _client.chat.completions.create(
                #model="gpt-4o-mini",
                model="gpt-5-nano",
                messages=[
                    {"role": "system", "content": sys},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.8,
                max_tokens=400,
            )
            text = resp.choices[0].message.content

        return _postprocess(text or "", count)

    except Exception as e:
        print("OpenAI name generation error:", repr(e))
        return []


def local_generate(prompt: str, count: int = 10) -> List[str]:
    """Very simple local fallback so the UI still works offline."""
    seed = re.sub(r"[^a-zA-Z0-9 ]+", " ", prompt).strip() or "Nova"
    bases = [w.title() for w in seed.split() if w][:3] or ["Nova"]
    suffixes = ["Lab", "Works", "Foundry", "Forge", "Hub", "Studio", "Peak", "Nest", "Shift", "Spark"]
    out = []
    i = 0
    while len(out) < count:
        out.append(f"{bases[i % len(bases)]} {suffixes[i % len(suffixes)]}".strip())
        i += 1
    return out