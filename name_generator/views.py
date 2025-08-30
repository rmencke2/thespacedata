# name_generator/views.py
from django.shortcuts import render
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_http_methods
from .services import generate_names, ServiceError  # your services.py

@require_http_methods(["GET", "POST"])
def generate_view(request):
    if request.method == "GET":
        # show form
        return render(request, "name_generator/form.html")

    # POST: generate names
    seed = (request.POST.get("seed") or "").strip()
    count_raw = request.POST.get("count") or "10"
    try:
        count = max(1, min(50, int(count_raw)))
    except ValueError:
        return HttpResponseBadRequest("Invalid count")

    if not seed:
        return HttpResponseBadRequest("Missing 'seed'")

    try:
        names = generate_names(seed, count=count)
    except ServiceError as e:
        # Show a friendly error page; also logged by your LOGGING config
        return render(
            request,
            "name_generator/error.html",
            {"message": str(e)},
            status=502,
        )

    return render(
        request,
        "name_generator/result.html",
        {"seed": seed, "count": count, "names": names},
    )

# Optional JSON endpoint
def api_generate(request):
    seed = (request.GET.get("seed") or "").strip()
    count_raw = request.GET.get("count") or "10"
    try:
        count = max(1, min(50, int(count_raw)))
    except ValueError:
        return JsonResponse({"error": "Invalid count"}, status=400)
    if not seed:
        return JsonResponse({"error": "Missing 'seed'"}, status=400)
    try:
        names = generate_names(seed, count=count)
    except ServiceError as e:
        return JsonResponse({"error": str(e)}, status=502)
    return JsonResponse({"seed": seed, "count": count, "names": names})

# Keep compatibility with urls that expect views.generate
generate = generate_view