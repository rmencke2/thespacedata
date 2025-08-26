# color_picker/views.py
from io import BytesIO

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render

from .forms import ImageUploadForm
from .utils import to_color_obj  # make sure utils.py has to_color_obj (as shown earlier)
from colorthief import ColorThief


def index(request):
    return render(request, "color_picker/index.html", {"form": ImageUploadForm()})


def _extract_palette_objs(file_like, color_count=9, quality=1):
    """Return (dominant_obj, [palette_objs...]) where each obj has hex/rgb/hsl/rgb_tuple."""
    ct = ColorThief(file_like)
    dom = ct.get_color(quality=quality)
    pal = ct.get_palette(color_count=color_count, quality=quality) or []
    return to_color_obj(dom), [to_color_obj(c) for c in pal]


def extract(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    form = ImageUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, "color_picker/index.html", {"form": form, "errors": form.errors})

    uploaded = form.cleaned_data["image"]
    color_count = form.cleaned_data.get("colors") or 9
    try:
        color_count = max(3, min(int(color_count), 12))
    except Exception:
        color_count = 9

    # Save upload
    path = default_storage.save(f"uploads/{uploaded.name}", ContentFile(uploaded.read()))
    # Build URL to the saved media file
    media_prefix = getattr(settings, "MEDIA_URL", "/media/")
    image_url = request.build_absolute_uri(f"{media_prefix}{path}")

    # Extract palette
    with default_storage.open(path, "rb") as f:
        dominant, palette = _extract_palette_objs(f, color_count=color_count, quality=1)

    ctx = {
        "image_url": image_url,
        "dominant": dominant,   # {hex, rgb, hsl, rgb_tuple}
        "palette": palette,     # list of {hex, rgb, hsl, rgb_tuple}
    }
    return render(request, "color_picker/palette.html", ctx)  # <- new UI template


def api_extract(request):
    """JSON API: POST multipart/form-data with 'image' and optional 'colors'."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    image = request.FILES.get("image")
    if not image:
        return JsonResponse({"error": "image file is required"}, status=400)

    try:
        color_count = max(3, min(int(request.POST.get("colors", 9)), 12))
    except Exception:
        color_count = 9

    path = default_storage.save(f"uploads/{image.name}", ContentFile(image.read()))
    media_prefix = getattr(settings, "MEDIA_URL", "/media/")
    image_url = request.build_absolute_uri(f"{media_prefix}{path}")

    with default_storage.open(path, "rb") as f:
        dominant, palette = _extract_palette_objs(f, color_count=color_count, quality=1)

    return JsonResponse({
        "image_url": image_url,
        "dominant": dominant,
        "palette": palette,
    })