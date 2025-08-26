from django.urls import path
from . import views

app_name = "name_generator"

urlpatterns = [
    path("", views.generate, name="generate"),  # use generate(), not index
]