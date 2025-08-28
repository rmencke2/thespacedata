from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class LogoProject(models.Model):
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    brand_name = models.CharField(max_length=120)
    tagline = models.CharField(max_length=160, blank=True)
    industry = models.CharField(max_length=120, blank=True)
    values = models.TextField(blank=True)
    style_keywords = models.CharField(max_length=200, blank=True)
    colors = models.CharField(max_length=200, blank=True)
    icon_ideas = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.brand_name

class LogoConcept(models.Model):
    project = models.ForeignKey(LogoProject, on_delete=models.CASCADE, related_name="concepts")
    index = models.PositiveSmallIntegerField(default=0)
    source = models.CharField(max_length=20, default="openai")
    preview_png = models.ImageField(upload_to="logos/previews/")
    svg_file = models.FileField(upload_to="logos/svg/", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project} · Concept {self.index}"