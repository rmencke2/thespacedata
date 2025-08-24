# myproject/views.py
from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request, "home.html")

def health(request):
    return HttpResponse("ok")

