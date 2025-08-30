# name_generator/views.py
from django.shortcuts import render
from django.http import JsonResponse
from .services import generate_names

def generator_page(request):
    return render(request, "name_generator/form.html")

def generate_view(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    industry = request.POST.get("industry", "")
    vibe = request.POST.get("vibe", "")
    try:
        count = int(request.POST.get("count", "10"))
    except ValueError:
        count = 10

    names = generate_names(industry, vibe, count)
    if not names:
        # Don’t 500; tell the user plainly
        return JsonResponse(
            {
                "error": "Could not generate names. Check OpenAI key/model and try again.",
                "names": [],
            },
            status=502,
        )
    return JsonResponse({"names": names})