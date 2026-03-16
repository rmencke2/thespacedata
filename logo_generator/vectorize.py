import logging
import subprocess
import tempfile
import os

from django.core.files.base import ContentFile

log = logging.getLogger(__name__)


def potrace_png_to_svg(png_path: str) -> bytes:
    """
    Convert PNG to SVG via potrace (through PNM).

    Raises:
        FileNotFoundError: If potrace is not installed
        subprocess.CalledProcessError: If conversion fails
    """
    with tempfile.TemporaryDirectory() as td:
        pnm = os.path.join(td, "tmp.pnm")
        svg = os.path.join(td, "out.svg")

        # Convert PNG→PNM (using ImageMagick 'convert' if available) or Pillow
        try:
            subprocess.run(
                ["convert", png_path, pnm],
                check=True,
                capture_output=True,
            )
        except FileNotFoundError:
            log.debug("ImageMagick not found, using Pillow fallback")
            from PIL import Image, ImageOps

            im = Image.open(png_path).convert("L")
            im = ImageOps.autocontrast(im)
            im.save(pnm)
        except subprocess.CalledProcessError as e:
            log.warning("ImageMagick convert failed: %s, using Pillow", e.stderr)
            from PIL import Image, ImageOps

            im = Image.open(png_path).convert("L")
            im = ImageOps.autocontrast(im)
            im.save(pnm)

        # potrace - let exceptions propagate for proper handling upstream
        subprocess.run(
            ["potrace", pnm, "--svg", "-o", svg, "--turdsize", "2", "--flat"],
            check=True,
            capture_output=True,
        )
        with open(svg, "rb") as f:
            data = f.read()
    return data


def attach_svg(concept):
    """Attach SVG vectorization to a LogoConcept."""
    png_path = concept.preview_png.path
    svg_bytes = potrace_png_to_svg(png_path)
    concept.svg_file.save(f"concept_{concept.id}.svg", ContentFile(svg_bytes), save=True)