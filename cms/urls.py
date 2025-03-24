from django.urls import path
from .views import home, page_detail

app_name = 'cms'

urlpatterns = [
    path('', home, name='home'),  # Add this line for the home view
    path('<slug:slug>/', page_detail, name='page_detail'),
]
