from django.conf import settings
from django.db import models

class NameIdea(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True
    )
    keywords = models.CharField(max_length=200, help_text="Comma-separated keywords")
    industry = models.CharField(max_length=120, blank=True)
    style = models.CharField(max_length=80, blank=True, help_text="e.g., modern, playful")
    result = models.TextField(help_text="One or more suggested names (newline separated)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (self.result.splitlines() or ["Name"])[0]