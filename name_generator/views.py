# name_generator/views.py
import re
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import NameRequestForm
from .models import NameIdea
from .services import openai_generate, local_generate

_number_prefix = re.compile(r"^\s*\d+[\.)-]\s*")
def _clean_names(names):
    return [_number_prefix.sub("", n).strip() for n in (names or []) if n and n.strip()]

def _coerce_int(val, default):
    try:
        return max(1, min(20, int(val)))
    except Exception:
        return default

def generate(request):
    used_openai = False
    names = []
    description = (request.POST.get("description") or request.GET.get("description") or "").strip()

    if request.method == "POST":
        form = NameRequestForm(request.POST)
        if form.is_valid():
            keywords = form.cleaned_data.get("keywords", "").strip()
            industry = form.cleaned_data.get("industry", "").strip()
            style    = form.cleaned_data.get("style", "").strip()
            count    = form.cleaned_data.get("count") or 6
        else:
            # Fallback: accept description-only posts
            keywords = (request.POST.get("keywords") or "").strip()
            industry = (request.POST.get("industry") or "").strip()
            style    = (request.POST.get("style") or "").strip()
            count    = _coerce_int(request.POST.get("count"), 6)

        # Try OpenAI first (with description)
        names = openai_generate(description, keywords, industry, style, count) or []
        used_openai = bool(names)
        if not names:
            names = local_generate(keywords, industry, style, count) or []
        names = _clean_names(names)

        if names:
            idea = NameIdea.objects.create(
                user=request.user if request.user.is_authenticated else None,
                keywords=keywords, industry=industry, style=style,
                result="\n".join(names),
            )
            src = "ai" if used_openai else "local"
            return redirect(f"{reverse('name_generator:generate')}?id={idea.id}&src={src}")
        # If we got here, generation failed—fall through to render with an empty list
    else:
        form = NameRequestForm()

    # Load specific run (after redirect)
    if (id_param := request.GET.get("id")):
        latest = NameIdea.objects.filter(id=id_param).first()
        if latest and not names:
            names = _clean_names(latest.result.splitlines())

    used_openai = (request.GET.get("src") == "ai")
    recent = NameIdea.objects.order_by("-created_at")[:10]

    return render(
        request,
        "name_generator/generate.html",
        {
            "form": form,
            "description": description,
            "names": names,
            "used_openai": used_openai,
            "recent": recent,
        },
    )