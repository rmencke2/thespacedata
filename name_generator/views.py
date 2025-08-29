# name_generator/views.py
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import NameRequestForm
from .models import NameIdea
from .services import openai_generate, local_generate  # both should accept (prompt, count=6)
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .services import generate_names, NameGenError

def generate(request):
    names = []
    used_openai = None
    latest = None

    if request.method == "POST":
        form = NameRequestForm(request.POST)
        if form.is_valid():
            prompt   = form.cleaned_data["prompt"]
            industry = (form.cleaned_data.get("industry") or "").strip()
            style    = (form.cleaned_data.get("style") or "").strip()
            count    = form.cleaned_data.get("count") or 6

            # Fold optional hints into the single prompt so we can keep a simple generator signature.
            extra_bits = []
            if industry:
                extra_bits.append(f"industry: {industry}")
            if style:
                extra_bits.append(f"style: {style}")
            full_prompt = prompt
            if extra_bits:
                full_prompt = f"{prompt}\n\nHints: " + "; ".join(extra_bits)

            # Call generators with the signature they support: (prompt, count)
            names = openai_generate(full_prompt, count) or []
            used_openai = bool(names)
            if not names:
                names = local_generate(full_prompt, count)
                used_openai = False

            idea = NameIdea.objects.create(
                user=request.user if request.user.is_authenticated else None,
                keywords=prompt,                 # store the free-text prompt here
                industry=industry,
                style=style,
                result="\n".join(names),
            )
            return redirect(reverse("name_generator:generate") + f"?id={idea.id}")
    else:
        form = NameRequestForm()

    # If redirected back with ?id=, hydrate `names` for the Suggestions list
    id_param = request.GET.get("id")
    if id_param:
        latest = NameIdea.objects.filter(id=id_param).first()
        if latest and latest.result:
            names = [n.strip() for n in latest.result.splitlines() if n.strip()]

    recent = NameIdea.objects.order_by("-created_at")[:10]

    return render(
        request,
        "name_generator/generate.html",
        {
            "form": form,
            "names": names,
            "recent": recent,
            "used_openai": used_openai,
            "latest": latest,
        },
    )
@csrf_exempt   # optional: if you call it from JS without CSRF token
@require_http_methods(["POST"])
def generate_view(request):
    topic = request.POST.get("topic", "").strip()
    count = int(request.POST.get("count", 10))
    style = request.POST.get("style") or None
    language = request.POST.get("language") or "English"

    try:
        names = generate_names(topic, count=count, style=style, language=language)
        return JsonResponse({"names": names})
    except NameGenError as e:
        return JsonResponse({"error": str(e)}, status=503)
    except Exception as e:
        return JsonResponse({"error": "Unexpected error"}, status=500)