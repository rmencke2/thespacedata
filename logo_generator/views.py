import logging
import subprocess

from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.core.files.base import ContentFile
from django.db import transaction

from .forms import BriefForm
from .models import LogoProject, LogoConcept
from .generator import generate_logo_pngs
from .vectorize import attach_svg

log = logging.getLogger(__name__)


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

    # Save project from the brief, associate with user if authenticated
    project = form.save(commit=False)
    if request.user.is_authenticated:
        project.user = request.user
    project.save()

    brief = form.cleaned_data
    pngs, err = generate_logo_pngs(brief, count=3)

    if err:
        if err == "missing_api_key":
            messages.error(request, "OpenAI API key is missing. Set OPENAI_API_KEY.")
        else:
            messages.error(request, "Generation failed. Please try again.")
        project.delete()  # Clean up the project if generation failed
        return redirect("logo_generator:new")

    # Create concept rows and attach previews atomically
    concepts = []
    with transaction.atomic():
        for i, png_data in enumerate(pngs):
            concept = LogoConcept.objects.create(project=project, index=i)
            concept.preview_png.save(f"concept_{concept.id}.png", ContentFile(png_data), save=True)
            concepts.append(concept)

    # Try vectorizing the first preview (optional)
    if concepts:
        try:
            attach_svg(concepts[0])
        except FileNotFoundError:
            log.debug("potrace not installed, SVG vectorization skipped")
        except subprocess.CalledProcessError as e:
            log.warning("SVG vectorization failed: %s", e)
        except Exception as e:
            log.exception("Unexpected error in SVG generation: %s", e)

    return redirect("logo_generator:show", pk=project.id)


def show(request, pk):
    """Display a logo project. Users can only view their own projects."""
    project = get_object_or_404(LogoProject.objects.select_related("user"), pk=pk)

    # Authorization: only the owner can view their project
    # Allow anonymous projects (user=None) to be viewed by anyone (backwards compatibility)
    if project.user is not None:
        if not request.user.is_authenticated or project.user != request.user:
            messages.error(request, "You don't have permission to view this project.")
            return redirect("logo_generator:new")

    concepts = project.concepts.order_by("index")
    return render(request, "logo_generator/show.html", {"project": project, "concepts": concepts})