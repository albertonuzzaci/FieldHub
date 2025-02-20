"""
URL configuration for FieldHub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.urls import path, include, re_path
from .setupDB import *
from .views import *
from django.conf.urls.static import static
from django.conf.urls import handler403, handler404

handler403 = permission_denied_view
#handler404 = resource_not_found_view -> con debug=False. 
#si aggiorna poi la view aggiungendo ,exception com secondo parametro e l'ultimo urlpattern non serve. 

urlpatterns = [
    path('admin/', admin.site.urls, name="adminpage"),
    path('core/', include('core.urls')),
    path('users/', include('users.urls')),
    re_path(r'^$|^/$|^home/$', home_page, name='homepage'),
    re_path(r'^.*', resource_not_found_view, name='notfound'),
]


