# myproject/views.py
from django.shortcuts import render
from django.http import JsonResponse
from django.http import HttpResponse

def home(request):
    return render(request, "home.html")

def health(request):
    return JsonResponse({"ok": True})

def privacy_policy(request):
    return render(request, "privacy-policy.html")

def support(request):
    return render(request, "support.html")
