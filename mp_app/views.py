from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Q
from django.shortcuts import render, redirect
from django.views.generic import View, ListView

from mp_app.models import Client, Producte, Categoria, Magatzem
from mp_app.models import Albara
from mp_app.models import LiniaAlbara


# Create your views here.

def page_not_found(request, exception):
    return render(request, "error/404.html", status=404)


class EmpleatRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(request.user, 'empleat'):
            raise PermissionDenied("Nomes empleats poden accedir aqui.")
        return super().dispatch(request, *args, **kwargs)


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
            messages.error(request, "Nomes es pot passar al seguent estat o cancel·lar l'albara.")
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
        productes_actius = Producte.objects.filter(actiu=True)
        return render(request, "linia/editar_linia.html", {'linia': linia, 'productes_actius': productes_actius})

    def post(self, request, *args, **kwargs):
        linia = LiniaAlbara.objects.get(id=self.kwargs['id'])
        linia.producte = Producte.objects.get(id=request.POST.get('producte'))
        linia.quantitat = int(request.POST.get('quantitat'))
        linia.notes = request.POST.get('notes')

        linia.save()

        return redirect('detall_linia', id=linia.id)


# /linies/nova/<numero_albara>
class NovaLiniaView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        albara = Albara.objects.get(numero_albara=self.kwargs['numero_albara'])
        productes_actius = Producte.objects.filter(actiu=True)
        return render(request, "linia/nova_linia.html", {'albara': albara, 'productes_actius': productes_actius})

    def post(self, request, *args, **kwargs):
        albara = Albara.objects.get(numero_albara=self.kwargs['numero_albara'])
        producte = Producte.objects.get(id=request.POST.get('producte'))
        stock = producte.stock_magatzems.get(magatzem=albara.magatzem)
        quantitat = int(request.POST.get('quantitat'))
        if stock.quantitat < quantitat:
            messages.error(request, "No hi ha prou stock disponible.")
            return redirect('nova_linia', numero_albara=albara.numero_albara)
        linia = LiniaAlbara.objects.create(
            albara=albara,
            producte=producte,
            quantitat=quantitat,
            preu_unitari=producte.preu_unitari,
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


# /cataleg/
class CatalegView(ListView):
    model = Producte
    template_name = 'producte/cataleg_producte.html'
    context_object_name = 'productes'

    def get_queryset(self):
        return Producte.objects.filter(actiu=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Categoria.objects.all()
        context['categoria_actual'] = None
        return context


# /cataleg/categoria/<categoria>/
class CatalegCategoriaView(ListView):
    model = Producte
    template_name = 'producte/cataleg_producte.html'
    context_object_name = 'productes'

    def get_queryset(self):
        categoria_id = self.kwargs['categoria']
        return Producte.objects.filter(actiu=True, categoria__id=categoria_id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Categoria.objects.all()
        context['categoria_actual'] = int(self.kwargs['categoria'])
        return context


# /cataleg/producte/<codi>/
class DetallProducteView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        producte = Producte.objects.get(codi=self.kwargs['codi'])
        stocks = producte.stock_magatzems.all()
        return render(request, "producte/detall_producte.html", {'producte': producte, 'stocks': stocks})


class HomeView(View):
    def get(self, request, *args, **kwargs):
        return render(request, 'home.html')


class PreparacioView(EmpleatRequiredMixin, ListView):
    model = Albara
    template_name = "preparacio/list_preparacio.html"
    context_object_name = "albarans"

    def get_queryset(self):
        empleat = self.request.user.empleat
        return Albara.objects.filter(
            magatzem=empleat.magatzem,
            estat__in=[Albara.PENDENT, Albara.EN_PREPARACIO]
        )


class MarcarPreparatView(EmpleatRequiredMixin, View):

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        empleat = request.user.empleat
        albara = Albara.objects.get(id=self.kwargs['id'])

        if albara.magatzem != empleat.magatzem:
            raise PermissionDenied("Aquest albarà no pertany al teu magatzem.")

        for linia in albara.linies.all():
            stock = linia.producte.stock_magatzems.get(magatzem=empleat.magatzem)

            if stock.quantitat < linia.quantitat:
                messages.error(request, f"No hi ha prou stock per {linia.producte.nom}")
                return redirect('preparacio')

        for linia in albara.linies.all():
            stock = linia.producte.stock_magatzems.get(magatzem=empleat.magatzem)
            stock.quantitat -= linia.quantitat
            stock.save()

        albara.estat = Albara.ENVIAT
        albara.save()

        messages.success(request, "Albarà marcat com ENVIAT")
        return redirect("preparacio")


class StockView(EmpleatRequiredMixin, View):

    def get(self, request):
        magatzem_id = request.GET.get("magatzem")
        categoria_id = request.GET.get("categoria")
        productes = Producte.objects.all()
        if categoria_id:
            productes = productes.filter(categoria__id=categoria_id)
        context = {
            "productes": productes,
            "magatzems": Magatzem.objects.all(),
            "categories": Categoria.objects.all(),
        }
        return render(request, "stock/stock.html", context)


class ReposicioStockView(EmpleatRequiredMixin, View):

    def get(self, request):
        return render(request, "stock/reposicio.html", {
            "productes": Producte.objects.all(),
            "magatzems": Magatzem.objects.all()
        })

    def post(self, request):
        producte = Producte.objects.get(id=request.POST.get("producte"))
        magatzem = Magatzem.objects.get(id=request.POST.get("magatzem"))
        quantitat = int(request.POST.get("quantitat"))
        stock = producte.stock_magatzems.get(magatzem=magatzem)
        stock.quantitat += quantitat
        stock.save()
        messages.success(request, "Stock actualitzat correctament.")
        return redirect("stock")
