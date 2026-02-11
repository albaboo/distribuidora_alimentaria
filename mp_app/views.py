from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import View, ListView

from mp_app.models import Client
from mp_app.models import Albara
from mp_app.models import LiniaAlbara


# Create your views here.

def page_not_found(request, exception):
    return render(request, "error/404.html", status=404)


# /clients/
class LlistarClientsView(ListView):
    model = Client
    template_name = 'client/list_clients.html'
    context_object_name = 'clients'

    def get_queryset(self):
        return Client.objects.filter(actiu=True)


# /clients/<codi_client>/
class DetallClientView(View):
    def get(self, request, *args, **kwargs):
        client = Client.objects.get(codi_client=self.kwargs['codi_client'])
        albarans = client.albarans.all()
        total_general = sum(albara.total for albara in albarans)
        return render(request, "client/detall_client.html",
                      {'client': client, 'albarans': albarans, 'total_general': total_general})


# /clients/<codi_client>/editar/
class EditarClientView(View):
    def get(self, request, *args, **kwargs):
        client = Client.objects.get(codi_client=self.kwargs['codi_client'])
        return render(request, "client/editar_client.html", {'client': client})

    def post(self, request, *args, **kwargs):
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

        return redirect('detall_client', codi_client=client.codi_client)


# /clients/nou/
class NouClientView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "client/nou_client.html")

    def post(self, request, *args, **kwargs):
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


# /albarans/
class LlistarAlbaransView(LoginRequiredMixin, ListView):
    model = Albara
    template_name = 'albara/list_albarans.html'
    context_object_name = 'albarans'

    def get_queryset(self):
        return Albara.objects.all()


# /albarans/<numero_albara>/
class DetallAlbaraView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        albara = Albara.objects.get(numero_albara=self.kwargs['numero_albara'])
        linies = albara.linies.all()
        return render(request, "albara/detall_albara.html", {'albara': albara, 'linies': linies})


# /albarans/<numero_albara>/editar/
class EditarAlbaraView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        albara = Albara.objects.get(numero_albara=self.kwargs['numero_albara'])
        if albara.estat == Albara.CANCELAT:
            messages.error(request, "Un albara cancel·lat no es pot editar.")
            return redirect('detall_albara', numero_albara=albara.numero_albara)
        clients = Client.objects.filter(
            Q(actiu=True) | Q(codi_client=albara.client.codi_client)
        )
        estats = Albara.ESTAT_CHOICES
        return render(request, "albara/editar_albara.html", {'albara': albara, 'estats': estats, 'clients': clients})

    def post(self, request, *args, **kwargs):
        albara = Albara.objects.get(numero_albara=self.kwargs['numero_albara'])
        if albara.estat == Albara.CANCELAT:
            messages.error(request, "Un albara cancel·lat no es pot editar.")
            return redirect('detall_albara', numero_albara=albara.numero_albara)

        estat = request.POST.get('estat')
        orden_estats = [
            Albara.PENDENT,
            Albara.EN_PREPARACIO,
            Albara.ENVIAT,
            Albara.ENTREGAT,
        ]

        can_edit = True
        if estat != Albara.CANCELAT and estat != albara.estat:
            try:
                index = orden_estats.index(albara.estat)
                next_estat = orden_estats[index + 1]
                can_edit = (estat == next_estat)
            except (ValueError, IndexError):
                can_edit = False

        if not can_edit:
            messages.error(request,"Nomes es pot passar al seguent estat o cancel·lar l'albara.")
            return redirect('editar_albara', numero_albara=albara.numero_albara)

        client = Client.objects.get(codi_client=request.POST.get('client'))
        albara.client = client
        albara.data_entrega_prevista = request.POST.get('data_entrega_prevista')
        albara.estat = request.POST.get('estat')
        albara.observacions = request.POST.get('observacions')

        albara.save()

        return redirect('detall_albara', numero_albara=albara.numero_albara)


# /albarans/nova/
class NouAlbaraView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        clients = Client.objects.filter(actiu=True)
        if clients.count() == 0:
            return render(request, 'home.html')
        estats = Albara.ESTAT_CHOICES
        return render(request, "albara/nou_albara.html", {'clients': clients})

    def post(self, request, *args, **kwargs):
        client = Client.objects.get(codi_client=request.POST.get('client'))
        albara = Albara.objects.create(
            client=client,
            data_entrega_prevista=request.POST.get('data_entrega_prevista'),
            total=0,
            observacions=request.POST.get('observacions')
        )

        return redirect('detall_albara', numero_albara=albara.numero_albara)


# /albarans/nova/<codi_client>/
class NouAlbaraClientView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        clients = [Client.objects.get(codi_client=self.kwargs['codi_client'])]
        return render(request, "albara/nou_albara.html", {'clients': clients})

    def post(self, request, *args, **kwargs):
        client = Client.objects.get(codi_client=request.POST.get('client'))
        albara = Albara.objects.create(
            client=client,
            data_entrega_prevista=request.POST.get('data_entrega_prevista'),
            total=0,
            observacions=request.POST.get('observacions')
        )

        return redirect('detall_albara', numero_albara=albara.numero_albara)


# /linies/<id>/
class DetallLiniaView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        linia = LiniaAlbara.objects.get(id=self.kwargs['id'])
        return render(request, "linia/detall_linia.html", {'linia': linia})


# /linies/<id>/editar/
class EditarLiniaView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        linia = LiniaAlbara.objects.get(id=self.kwargs['id'])
        return render(request, "linia/editar_linia.html", {'linia': linia})

    def post(self, request, *args, **kwargs):
        linia = LiniaAlbara.objects.get(id=self.kwargs['id'])
        linia.nom_producte = request.POST.get('nom_producte')
        linia.quantitat = int(request.POST.get('quantitat'))
        linia.preu_unitari = Decimal(request.POST.get('preu_unitari'))
        linia.notes = request.POST.get('notes')

        linia.save()

        return redirect('detall_linia', id=linia.id)


# /linies/nova/<numero_albara>
class NovaLiniaView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        albara = Albara.objects.get(numero_albara=self.kwargs['numero_albara'])
        return render(request, "linia/nova_linia.html", {'albara': albara})

    def post(self, request, *args, **kwargs):
        albara = Albara.objects.get(numero_albara=self.kwargs['numero_albara'])
        linia = LiniaAlbara.objects.create(
            albara=albara,
            nom_producte=request.POST.get('nom_producte'),
            quantitat=int(request.POST.get('quantitat')),
            preu_unitari=Decimal(request.POST.get('preu_unitari')),
            notes=request.POST.get('notes')
        )

        return redirect('detall_linia', id=linia.id)


# /consulta/albara
class ConsultaFormulariAlbaraView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        return render(request, "consulta/formulari_albara.html")

    def post(self, request, *args, **kwargs):
        numero_albara = request.POST.get('numero_albara')
        return redirect('consulta_albara', numero_albara=numero_albara)


# /consulta/albara/<numero_albara>/
class ConsultaAlbaraView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        try:
            albara = Albara.objects.get(numero_albara=self.kwargs['numero_albara'])
            if albara:
                linies = albara.linies.all()
                return render(request, "consulta/resultat_albara.html",
                              {'albara': albara, 'linies': linies, 'user': self.request.user})
            else:
                return render(request, "error/albara-400.html", status=404)
        except:
            return render(request, "error/albara-400.html", status=404)


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'home.html')
