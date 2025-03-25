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
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from django.shortcuts import redirect
from cms import admin as cms_admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('cms/', include(('cms.urls', 'cms'), namespace='cms')),  # Ensure this is unique
    # If there are other conflicting namespaces, rename them:
    # path('cms-admin/', include(('cms_admin.urls', 'cms_admin'), namespace='cms_admin')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
