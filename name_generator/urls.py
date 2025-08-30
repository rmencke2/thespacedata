from django.urls import path
from . import views

app_name = "name_generator"

urlpatterns = [
    path("", views.generate, name="generate"),       # alias above keeps this working
    path("api/", views.api_generate, name="api_generate"),
]