# name_generator/views.py
from django.shortcuts import render, redirect
from django.urls import reverse
from .forms import NameRequestForm
from .models import NameIdea
from .services import openai_generate, local_generate  # both should accept (prompt, count=6)


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