from django.shortcuts import render, redirect
from django.views.generic import View, ListView

from mp_app.models import Client


# Create your views here.

#/clients/
class LlistarClientsView(ListView):
    model = Client
    template_name = 'client/list_clients.html'
    context_object_name = 'clients'

    def get_queryset(self):
        return Client.objects.filter(actiu=True)

#/clients/<codi_client>/
class DetallClientView(View):
    def get(self, request, *args, **kwargs):
        client = Client.objects.get(codi_client=self.kwargs['codi_client'])
        albarans = client.albarans.all()
        return render(request, "client/detall_client.html", {'client': client, 'albarans': albarans})

#/clients/<codi_client>/editar/
class EditarClientView(View):
    def get(self,request, *args, **kwargs):
        client = Client.objects.get(codi_client=self.kwargs['codi_client'])
        return render(request, "client/editar_client.html", {"client": client})

    def post(self,request, *args, **kwargs):
        client = Client.objects.get(codi_client=self.kwargs['codi_client'])

        client.nom_comercial = request.POST.get('nom_comercial')
        client.cif = request.POST.get('cif')
        client.persona_contacte = request.POST.get('persona_contacte')
        client.telefon = request.POST.get('telefon')
        client.email = request.POST.get('email')
        client.adreca_entrega = request.POST.get('adreca_entrega')
        client.poblacio = request.POST.get('poblacio')
        client.codi_postal = request.POST.get('codi_postal')
        client.actiu = request.POST.get('actiu') == 'on'

        client.save()

        redirect_url = f"/clients/{client.codi_client}/"
        return redirect(redirect_url)
# /clients/nou/
class NouClientView(View):
    def get(self, request, *args, **kwargs):
        return render(request, "client/nou_client.html")

    def post(self,request, *args, **kwargs):
        client = Client.objects.create(
            nom_comercial=request.POST.get('nom_comercial'),
            cif=request.POST.get('cif'),
            persona_contacte=request.POST.get('persona_contacte'),
            telefon=request.POST.get('telefon'),
            email=request.POST.get('email'),
            adreca_entrega=request.POST.get('adreca_entrega'),
            poblacio=request.POST.get('poblacio'),
            codi_postal=request.POST.get('codi_postal'),
            actiu=request.POST.get('actiu') == 'on'
        )

        return redirect('detall_client', codi_client=client.codi_client)

class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'home.html')