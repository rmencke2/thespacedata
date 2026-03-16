from django.urls import path
from . import views

app_name = "color_picker"

urlpatterns = [
    path("", views.index, name="index"),
    path("extract/", views.extract, name="color_extract"),
    path("api/extract/", views.api_extract, name="api_extract"),
]