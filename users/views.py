# users/views.py
from django.http import HttpResponse
from django.shortcuts import render

def index(request):
    # Replace with a real template when you have one
    return HttpResponse("Users index")

def profile(request):
    # Replace with a real template when you have one
    return HttpResponse("User profile page")