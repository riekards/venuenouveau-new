from .models import Page

def navigation_pages(request):
    pages = Page.objects.filter(is_public=True)
    return {'navigation_pages': pages}
