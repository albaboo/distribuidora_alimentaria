from decimal import Decimal

from django.contrib.auth.models import User
from django.db import models


# Create your models here.

class Client(models.Model):
    codi_client = models.CharField(unique=True)
    nom_comercial = models.CharField()
    cif = models.CharField()
    persona_contacte = models.CharField()
    telefon = models.CharField()
    email = models.EmailField()
    adreca_entrega = models.CharField()
    poblacio = models.CharField()
    codi_postal = models.CharField()
    actiu = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)
            self.codi_client = f"CLI{self.id:03d}"
            kwargs['force_insert'] = False
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)


class Categoria(models.Model):
    nom = models.CharField()
    descripcio = models.TextField(null=True, blank=True)
    requereix_refrigeracio = models.BooleanField()
    temperatura_maxima = models.DecimalField(max_digits=10, decimal_places=2, null=True)


class Producte(models.Model):
    UNITAT = 'UNITAT'
    CAIXA = 'CAIXA'
    PALET = 'PALET'
    KG = 'KG'
    LITRE = 'LITRE'

    UNITAT_MESURA_CHOICES = [
        (UNITAT, 'Unitat'),
        (CAIXA, 'Caixa'),
        (PALET, 'Palet'),
        (KG, 'Kg'),
        (LITRE, 'Litre'),
    ]

    IVA_4 = Decimal('0.04')
    IVA_10 = Decimal('0.10')
    IVA_21 = Decimal('0.21')

    IVA_CHOICES = [
        (IVA_4, '4%'),
        (IVA_10, '10%'),
        (IVA_21, '21%'),
    ]

    codi = models.CharField(unique=True)
    nom = models.CharField()
    descripcio = models.TextField(null=True, blank=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productes')
    preu_unitari = models.DecimalField(max_digits=10, decimal_places=2)
    unitat_mesura = models.CharField(choices=UNITAT_MESURA_CHOICES, default=UNITAT)
    iva = models.DecimalField(choices=IVA_CHOICES, default=IVA_21, max_digits=10, decimal_places=2)
    es_periple = models.BooleanField()
    imatge_url = models.URLField(null=True, blank=True)
    actiu = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)
            self.codi_client = f"BEB{self.id:03d}"
            kwargs['force_insert'] = False
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)


class Magatzem(models.Model):
    nom = models.CharField()
    adreca = models.CharField()
    capacitat_maxima = models.DecimalField(max_digits=10, decimal_places=2)
    te_cambra_frio = models.BooleanField()
    responsable = models.CharField()


class StockMagatzem(models.Model):
    producte = models.ForeignKey(Producte, on_delete=models.CASCADE, related_name='stock_magatzems')
    magatzem = models.ForeignKey(Magatzem, on_delete=models.CASCADE, related_name='stock_magatzems')
    quantitat = models.IntegerField()
    data_ultima_entrada = models.DateField()
    ubicacio = models.CharField()


class Empleat(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='empleat')
    codi_empleat = models.CharField(unique=True)
    telefon = models.CharField()
    data_alta = models.DateField()
    magatzem_assignat = models.ForeignKey(Magatzem, on_delete=models.SET_NULL, related_name='empleats', null=True)
    carrec = models.CharField()

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)
            self.codi_client = f"EMP{self.id:03d}"
            kwargs['force_insert'] = False
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)


class Albara(models.Model):
    PENDENT = 'PENDENT'
    EN_PREPARACIO = 'EN_PREPARACIO'
    ENVIAT = 'ENVIAT'
    ENTREGAT = 'ENTREGAT'
    CANCELAT = 'CANCELAT'

    ESTAT_CHOICES = [
        (PENDENT, 'Pendent'),
        (EN_PREPARACIO, 'En Preparacio'),
        (ENVIAT, 'Enviat'),
        (ENTREGAT, 'Entregat'),
        (CANCELAT, 'Cancel·lat'),
    ]
    numero_albara = models.CharField(unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='albarans', null=True)
    empleat = models.ForeignKey(Empleat, on_delete=models.CASCADE, related_name='albarans', null=True)
    magatzem = models.ForeignKey(Magatzem, on_delete=models.CASCADE, related_name='albarans', null=True)
    data_creacio = models.DateTimeField(auto_now_add=True)
    data_entrega_prevista = models.DateField()
    estat = models.CharField(choices=ESTAT_CHOICES, default=PENDENT)
    base_imposable = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    observacions = models.TextField(null=True, blank=True)
    signatura_client = models.CharField(null=True)

    def save(self, *args, **kwargs):
        if not self.id:
            super().save(*args, **kwargs)
            self.numero_albara = f"ALB-{self.data_creacio.year}-{self.id:03d}"
            kwargs['force_insert'] = False
            super().save(*args, **kwargs)
        else:
            super().save(*args, **kwargs)

    def calcular_base_imposible(self):
        self.base_imposable = sum(linia.subtotal for linia in self.linies.all())
        self.save()
        return self.base_imposable

    def calcular_total_iva(self):
        self.total = sum(linia.subtotal * linia.producte.iva for linia in self.linies.all())
        self.save()
        return self.total

    def calcular_total(self):
        self.total = self.calcular_base_imposible() + self.calcular_total_iva()
        self.save()
        return self.total


class LiniaAlbara(models.Model):
    albara = models.ForeignKey(Albara, on_delete=models.CASCADE, related_name='linies')
    producte = models.ForeignKey(Producte, on_delete=models.CASCADE, related_name='linies', null=True)
    quantitat = models.IntegerField()
    preu_unitari = models.DecimalField(max_digits=10, decimal_places=2)
    descompte_percentatge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.CharField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.preu_unitari = self.producte.preu_unitari
        self.subtotal = Decimal(self.quantitat) * self.preu_unitari * (
                    Decimal('1') - Decimal(self.descompte_percentatge) / Decimal('100'))
        super().save(*args, **kwargs)
        self.albara.calcular_total()

    def delete(self, *args, **kwargs):
        albara = self.albara

        super().delete(*args, **kwargs)
        albara.calcular_total()
