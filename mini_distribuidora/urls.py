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
from django.urls import path, include

from mp_app import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.HomeView.as_view(), name='home'),
    path('clients/', views.LlistarClientsView.as_view(), name='llistar_clients'),
    path('clients/nou/', views.NouClientView.as_view(), name='nou_client'),
    path('clients/<str:codi_client>/', views.DetallClientView.as_view(), name='detall_client'),
    path('clients/<str:codi_client>/editar/', views.EditarClientView.as_view(), name='editar_client'),
    path('albarans/', views.LlistarAlbaransView.as_view(), name='llistar_albarans'),
    path('albarans/nova/', views.NouAlbaraView.as_view(), name='nou_albara'),
    path('albarans/nova/<str:codi_client>/', views.NouAlbaraClientView.as_view(), name='nou_albara_client'),
    path('albarans/<str:numero_albara>/', views.DetallAlbaraView.as_view(), name='detall_albara'),
    path('albarans/<str:numero_albara>/editar/', views.EditarAlbaraView.as_view(), name='editar_albara'),
    path('linies/nova/<str:numero_albara>/', views.NovaLiniaView.as_view(), name='nova_linia'),
    path('linies/<str:id>/', views.DetallLiniaView.as_view(), name='detall_linia'),
    path('linies/<str:id>/editar/', views.EditarLiniaView.as_view(), name='editar_linia'),
    path('consulta/albara/<str:numero_albara>/', views.ConsultaAlbaraView.as_view(), name='consulta_albara'),
    path('consulta/albara/', views.ConsultaFormulariAlbaraView.as_view(), name='cercar_albara'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path("accounts/", include("django.contrib.auth.urls")),
    path('cataleg/', views.CatalegView.as_view(), name='cataleg'),
    path('cataleg/producte/<str:codi>/', views.DetallProducteView.as_view(), name='detall_producte'),
    path('cataleg/categoria/<int:categoria>/', views.CatalegCategoriaView.as_view(), name='cataleg_categoria')
]

handler404 = 'mp_app.views.page_not_found'