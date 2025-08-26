from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponseBadRequest
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.urls import reverse
from .forms import ImageUploadForm
from .utils import extract_palette

def index(request):
    form = ImageUploadForm()
    return render(request, "color_picker/index.html", {"form": form})

def extract(request):
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    form = ImageUploadForm(request.POST, request.FILES)
    if not form.is_valid():
        return render(request, "color_picker/index.html", {"form": form, "errors": form.errors})

    image_file = form.cleaned_data["image"]
    color_count = form.cleaned_data.get("colors") or 6

    # save upload to MEDIA for preview
    path = default_storage.save(f"uploads/{image_file.name}", ContentFile(image_file.read()))
    file_url = f"{request.build_absolute_uri('/')[:-1]}{request.META.get('SCRIPT_NAME','')}{request.build_absolute_uri('/').split(request.get_host())[-1]}{path}"  # extra-safe build
    # simpler (works in dev): file_url = request.build_absolute_uri(f"/media/{path}") if MEDIA_URL==/media/

    # color_picker/views.py (inside extract)
    with default_storage.open(path, "rb") as f:
        data = extract_palette(f, color_count=color_count)

    palette = data["palette"]
    dominant = data["dominant"]

    css_vars = "\n".join([f"--color-{i+1}: {c['hex']};" for i, c in enumerate(palette)])
    css_vars += f"\n--primary: {dominant['hex']};"    # expose dominant as --primary

    return render(request, "color_picker/result.html", {
        "palette": palette,
        "dominant": dominant,
        "image_path": f"/media/{path}",
        "css_vars": css_vars,
    })

def api_extract(request):
    """
    JSON API: POST multipart/form-data with 'image' and optional 'colors'
    Returns: { image_url, palette: [{hex, rgb, hsl}, ...] }
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    image = request.FILES.get("image")
    if not image:
        return JsonResponse({"error": "image file is required"}, status=400)

    try:
        color_count = int(request.POST.get("colors", 6))
        color_count = max(3, min(color_count, 12))
    except ValueError:
        color_count = 6

    path = default_storage.save(f"uploads/{image.name}", ContentFile(image.read()))
    with default_storage.open(path, "rb") as f:
        palette = extract_palette(f, color_count=color_count)

    return JsonResponse({
        "image_url": f"/media/{path}",
        "palette": palette,
        "dominant": dominant
    })