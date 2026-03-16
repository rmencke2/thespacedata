# color_picker/utils.py

from io import BytesIO
from typing import Dict, List, Tuple
from PIL import Image
from colorthief import ColorThief
import colorsys
from colorsys import rgb_to_hls

# ---------- helpers ----------

def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """(R,G,B) -> '#RRGGBB'"""
    return "#{:02x}{:02x}{:02x}".format(*rgb).upper()


def rgb_to_hsl(rgb: Tuple[int, int, int]) -> Dict[str, int]:
    """
    (R,G,B) [0..255] -> {'h':0..360, 's':0..100, 'l':0..100}
    Note: colorsys uses HLS order with 0..1 floats.
    """
    r, g, b = [c / 255.0 for c in rgb]
    h, l, s = colorsys.rgb_to_hls(r, g, b)
    return {"h": round(h * 360), "s": round(s * 100), "l": round(l * 100)}


def _pack(rgb: Tuple[int, int, int]) -> Dict:
    """Normalize a color into hex/rgb/hsl dict."""
    return {
        "hex": rgb_to_hex(rgb),
        "rgb": (int(rgb[0]), int(rgb[1]), int(rgb[2])),
        "hsl": rgb_to_hsl(rgb),
    }


def _normalize_image(file_obj, max_edge: int = 1600) -> BytesIO:
    """
    Open an uploaded file as RGB, optionally downscale very large images,
    and return a BytesIO (JPEG) suitable for ColorThief.
    """
    img = Image.open(file_obj).convert("RGB")

    if max(img.size) > max_edge:
        img.thumbnail((max_edge, max_edge), Image.LANCZOS)

    buf = BytesIO()
    # JPEG keeps it small/fast for analysis; 90 is a good balance
    img.save(buf, format="JPEG", quality=90, optimize=True)
    buf.seek(0)
    return buf

# color_picker/utils.py

def clamp(v, lo=0, hi=255): return max(lo, min(hi, v))

def rgb_tuple_to_hex(rgb):
    r, g, b = [clamp(int(x)) for x in rgb]
    return f"#{r:02X}{g:02X}{b:02X}"

def rgb_tuple_to_hsl(rgb):
    r, g, b = [clamp(int(x)) for x in rgb]
    # colorsys uses 0..1; note: HLS in lib; convert to HSL wording
    h, l, s = rgb_to_hls(r/255.0, g/255.0, b/255.0)  # h,l,s in 0..1
    H = round(h * 360)
    S = round(s * 100)
    L = round(l * 100)
    return f"hsl({H}, {S}%, {L}%)"

def to_color_obj(rgb):
    return {
        "rgb_tuple": tuple(rgb),
        "hex": rgb_tuple_to_hex(rgb),
        "rgb": f"rgb({rgb[0]}, {rgb[1]}, {rgb[2]})",
        "hsl": rgb_tuple_to_hsl(rgb),
    }

# ---------- public API ----------

def extract_palette(file_obj, color_count: int = 6, quality: int = 8) -> Dict[str, List[Dict]]:
    """
    Extract a palette + dominant color from an uploaded image.

    Args:
        file_obj: a readable binary file-like (e.g. Django UploadedFile or opened file)
        color_count: number of colors in the palette (3..12 is reasonable)
        quality: ColorThief quality (1..10). Higher => faster, slightly less accurate.

    Returns:
        {
          "palette": [ {hex, rgb, hsl}, ... ],
          "dominant": {hex, rgb, hsl}
        }
    """
    # Clamp color_count to reasonable bounds
    color_count = max(3, min(int(color_count or 6), 12))
    quality = max(1, min(int(quality or 8), 10))

    # Prepare image buffer for ColorThief
    buf = _normalize_image(file_obj)

    # Extract colors
    thief = ColorThief(buf)
    dom_rgb = thief.get_color(quality=quality)
    palette = thief.get_palette(color_count=color_count, quality=quality)

    return {
        "palette": [_pack(rgb) for rgb in palette],
        "dominant": _pack(dom_rgb),
    }


def build_css_vars(palette: List[Dict], dominant: Dict) -> str:
    """
    Produce a block of CSS variable declarations:
      --color-1, --color-2, ... and --primary for dominant.
    """
    lines = []
    for i, c in enumerate(palette, start=1):
        lines.append(f"--color-{i}: {c['hex']};")
    if dominant and "hex" in dominant:
        lines.append(f"--primary: {dominant['hex']};")
    return "\n".join(lines)