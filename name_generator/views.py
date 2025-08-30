from __future__ import annotations

import logging
from typing import Any, Dict

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .models import NameIdea
from .services import generate_names, ServiceError  
from .forms import NameRequestForm 

log = logging.getLogger(__name__)


def health(request: HttpRequest) -> HttpResponse:
    return HttpResponse("ok")


@require_http_methods(["GET", "POST"])
def generate(request: HttpRequest) -> HttpResponse:
    """
    GET: render empty form
    POST: validate form, call OpenAI service, persist attempt
    """
    names: list[str] = []

    if request.method == "GET":
        form = NameRequestForm()
        return render(request, "name_generator/generate.html", {"form": form, "names": names})

    # POST
    form = NameRequestForm(request.POST)
    if not form.is_valid():
        # show validation errors + no results
        return render(request, "name_generator/generate.html", {"form": form, "names": names})

    # Map form fields to your existing service expectations
    prompt   = (form.cleaned_data.get("prompt") or "").strip()
    industry = (form.cleaned_data.get("industry") or "").strip()
    style    = (form.cleaned_data.get("style") or "").strip()  
    count    = form.cleaned_data.get("count") or 10

    try:
        names = generate_names(industry=industry, vibe=style, count=count)
    except ServiceError as e:
        log.exception("ServiceError generating names: %s", e)
        names = []

    # Persist attempt (prompt -> keywords, style -> style)
    NameIdea.objects.create(
        user=request.user if getattr(request, "user", None) and request.user.is_authenticated else None,
        keywords=prompt,            
        industry=industry,
        style=style,
        result="\n".join(names),
    )

    ctx: Dict[str, Any] = {
        "form": form,        
        "names": names,
        "industry": industry,
        "vibe": style,       
        "keywords": prompt,
        "count": count,
    }
    return render(request, "name_generator/generate.html", ctx)