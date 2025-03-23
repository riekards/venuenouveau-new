from django.shortcuts import render, get_object_or_404
from .models import Page

def home(request):
    # For the homepage, we assume a page with slug 'home' exists.
    page = get_object_or_404(Page, slug='home')
    return render(request, 'cms/page_detail.html', {'page': page})

def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug)
    return render(request, 'cms/page_detail.html', {'page': page})
