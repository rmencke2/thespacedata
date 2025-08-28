from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.core.files.base import ContentFile

from .forms import BriefForm
from .models import LogoProject, LogoConcept
from .generator import generate_logo_pngs  # uses brief dict + count
from .vectorize import attach_svg


def index(request):
    return redirect("logo_generator:new")


def new(request):
    form = BriefForm()
    return render(request, "logo_generator/new.html", {"form": form})


def create(request):
    if request.method != "POST":
        return redirect("logo_generator:new")

    form = BriefForm(request.POST)
    if not form.is_valid():
        return render(request, "logo_generator/new.html", {"form": form})

    # Save project from the brief
    project = form.save(commit=True)

    # Your generator wants the brief dict and `count`, not a prompt and `n`
    brief = form.cleaned_data
    pngs, err = generate_logo_pngs(brief, count=3)

    if err:
        if err == "missing_api_key":
            messages.error(request, "OpenAI API key is missing. Set OPENAI_API_KEY.")
        else:
            messages.error(request, "Generation failed. Please try again.")
        return redirect("logo_generator:new")

    # Create concept rows and attach previews
    concepts = []
    for i in range(len(pngs)):
        concept = LogoConcept.objects.create(project=project, index=i)
        concept.preview_png.save(f"concept_{concept.id}.png", ContentFile(pngs[i]), save=True)
        concepts.append(concept)

    # Try vectorizing the first preview (optional best-effort)
    if concepts:
        try:
            attach_svg(concepts[0])
        except Exception:
            pass

    return redirect("logo_generator:show", pk=project.id)


def show(request, pk):
    project = get_object_or_404(LogoProject, pk=pk)
    concepts = project.concepts.order_by("index")
    return render(request, "logo_generator/show.html", {"project": project, "concepts": concepts})