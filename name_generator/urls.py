from django.urls import path
from . import views

app_name = "name_generator"

urlpatterns = [
    path("", views.generate, name="generate"),       # alias above keeps this working
    path("health/", views.health, name="health"),
]