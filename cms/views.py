from django.shortcuts import render, get_object_or_404
from .models import Page, PricingPackage

def home(request):
    # Loads the page with slug 'home'
    page = get_object_or_404(Page, slug='home')
    return render(request, 'cms/page_detail.html', {'page': page})

def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_public=True)
    context = {'page': page}
    if slug == 'trendy-offers':
        # Query approved pricing packages.
        pricing_packages = PricingPackage.objects.filter(approved=True)
        context['pricing_packages'] = pricing_packages
    return render(request, 'cms/page_detail.html', context)