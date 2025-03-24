"""
URL configuration for venuenouveau project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from cms import admin as cms_admin

urlpatterns = [
    path('admin/', admin.site.urls),

    # Redirect to the 'home' view in the 'cms' app
    path('', lambda request: redirect('cms:home', permanent=False)),

    # Include all CMS routes under the 'cms' namespace
    path('', include(('cms.urls', 'cms'), namespace='cms')),
]
