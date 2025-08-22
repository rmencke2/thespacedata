from django.http import HttpResponse
# core/views.py

def home(request):
    return HttpResponse("Hello from thespacedata 👋", content_type="text/plain", status=200)

def health(request):
    return HttpResponse("OK", content_type="text/plain", status=200)