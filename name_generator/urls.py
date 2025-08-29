from django.urls import path
from . import views

app_name = "name_generator"

urlpatterns = [
    path("", views.generate, name="generate"), 
    path("generate/", generate_view, name="generate-names"),
 # use generate(), not index
]