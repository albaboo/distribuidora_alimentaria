"""
URL configuration for mini_distribuidora project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path

from mp_app import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.HomeView.as_view(), name='home'),
    path('clients/', views.LlistarClientsView.as_view(), name='llistar_clients'),
    path('clients/nou/', views.NouClientView.as_view(), name='nou_client'),
    path('clients/<str:codi_client>/', views.DetallClientView.as_view(), name='detall_client'),
    path('clients/<str:codi_client>/editar/', views.EditarClientView.as_view(), name='editar_client'),
    path('albarans/', views.LlistarAlbaransView.as_view(), name='llistar_albarans'),
    path('albarans/nou/', views.NouAlbaraView.as_view(), name='nou_albara'),
]

handler404 = 'mp_app.views.page_not_found'