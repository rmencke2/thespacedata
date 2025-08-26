# name_generator/views.py
import re
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import NameRequestForm
from .models import NameIdea
from .services import openai_generate, local_generate

_number_prefix = re.compile(r"^\s*\d+[\.)-]\s*")

def _clean_names(names):
    """Strip any leading numbering/bullets from provider output."""
    return [ _number_prefix.sub("", n).strip() for n in (names or []) if n and n.strip() ]

def generate(request):
    used_openai = False
    if request.method == "POST":
        form = NameRequestForm(request.POST)
        if form.is_valid():
            keywords = form.cleaned_data["keywords"]
            industry = form.cleaned_data["industry"]
            style    = form.cleaned_data["style"]
            count    = form.cleaned_data["count"]

            names = openai_generate(keywords, industry, style, count)
            used_openai = bool(names)
            if not names:
                names = local_generate(keywords, industry, style, count)

            names = _clean_names(names)

            idea = NameIdea.objects.create(
                user=request.user if request.user.is_authenticated else None,
                keywords=keywords, industry=industry, style=style,
                result="\n".join(names),
            )
            src = "ai" if used_openai else "local"
            return redirect(f"{reverse('name_generator:generate')}?id={idea.id}&src={src}")
    else:
        form = NameRequestForm()

    latest = None
    names = []
    if (id_param := request.GET.get("id")):
        latest = NameIdea.objects.filter(id=id_param).first()
        if latest:
            names = _clean_names(latest.result.splitlines())
    used_openai = (request.GET.get("src") == "ai")

    recent = NameIdea.objects.order_by("-created_at")[:10]

    return render(
        request,
        "name_generator/generate.html",
        {
            "form": form,
            "names": names,
            "used_openai": used_openai,
            "recent": recent,
        },
    )