from django.urls import path
from .views import home, page_detail

app_name = 'cms'  # This registers the namespace for URL reversal

urlpatterns = [
    path('', home, name='home'),
    path('pages/<slug:slug>/', page_detail, name='page_detail'),
]
