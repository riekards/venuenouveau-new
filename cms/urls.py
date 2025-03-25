from django.urls import path
from . import views

app_name = 'cms'  # Ensure this is unique and not duplicated in other apps

urlpatterns = [
    path('', views.home, name='home'),
    path('page/<slug:slug>/', views.page_detail, name='page_detail'),
    # ...other URL patterns...
]
