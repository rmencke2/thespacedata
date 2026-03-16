from django.contrib import admin
from .models import NameIdea

@admin.register(NameIdea)
class NameIdeaAdmin(admin.ModelAdmin):
    list_display = ("__str__", "industry", "style", "user", "created_at")
    search_fields = ("result", "keywords", "industry", "style")
    list_filter = ("industry", "style", "created_at")