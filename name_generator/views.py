from __future__ import annotations

import logging
from typing import Any, Dict

from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from .models import NameIdea
from .services import generate_names, ServiceError  # keep import available

log = logging.getLogger(__name__)


def health(request: HttpRequest) -> HttpResponse:
    """Simple health endpoint for liveness checks."""
    return HttpResponse("ok")


@require_http_methods(["GET", "POST"])
def generate(request: HttpRequest) -> HttpResponse:
    """
    Render the name generator page.

    GET: show the form.
    POST: call the service to generate names and persist a NameIdea row.
    Never raises—renders a friendly page even on failure.
    """
    if request.method == "GET":
        return render(request, "name_generator/generate.html", {"names": []})

    # POST
    industry = (request.POST.get("industry") or "").strip()
    vibe = (request.POST.get("vibe") or "").strip()
    keywords = (request.POST.get("keywords") or "").strip()
    count_str = request.POST.get("count") or "10"
    try:
        count = max(1, min(50, int(count_str)))
    except ValueError:
        count = 10

    try:
        names = generate_names(industry=industry, vibe=vibe, count=count)
    except ServiceError as e:
        log.exception("ServiceError generating names: %s", e)
        names = []

    # Persist the attempt (even if names is empty—useful for debugging)
    NameIdea.objects.create(
        user=getattr(request, "user", None) if getattr(request, "user", None).is_authenticated else None,
        keywords=keywords,
        industry=industry,
        style=vibe,
        result="\n".join(names),
    )

    context: Dict[str, Any] = {
        "names": names,
        "industry": industry,
        "vibe": vibe,
        "keywords": keywords,
        "count": count,
    }
    return render(request, "name_generator/generate.html", context)