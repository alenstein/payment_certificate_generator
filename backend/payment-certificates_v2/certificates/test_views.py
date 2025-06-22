from django.shortcuts import render
from django.http import HttpResponse

def test_create_project(request):
    """Simple test view to debug project creation"""
    return HttpResponse("Project creation page is working!")
