import subprocess
import tempfile
import os
from django.core.files.base import ContentFile

def potrace_png_to_svg(png_path: str) -> bytes:
    """
    Convert PNG to SVG via potrace (through PNM).
    """
    with tempfile.TemporaryDirectory() as td:
        pnm = os.path.join(td, "tmp.pnm")
        svg = os.path.join(td, "out.svg")
        # convert PNG→PNM (using ImageMagick 'convert' if available) or Pillow
        try:
            subprocess.run(["convert", png_path, pnm], check=True)
        except Exception:
            # Pillow fallback
            from PIL import Image
            from PIL import ImageOps
            im = Image.open(png_path).convert("L")
            im = ImageOps.autocontrast(im)
            im.save(pnm)

        # potrace
        subprocess.run(["potrace", pnm, "--svg", "-o", svg, "--turdsize", "2", "--flat"], check=True)
        with open(svg, "rb") as f:
            data = f.read()
    return data

def attach_svg(concept):
    png_path = concept.preview_png.path
    svg_bytes = potrace_png_to_svg(png_path)
    concept.svg_file.save(f"concept_{concept.id}.svg", ContentFile(svg_bytes), save=True)