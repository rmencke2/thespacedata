# users/urls.py
from django.urls import path
from . import views

app_name = "users"

urlpatterns = [
    path("", views.index, name="index"),          # /users/
    path("profile/", views.profile, name="profile"),
]