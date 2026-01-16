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


class Albara(models.Model):
    PENDENT = 'PENDENT'
    EN_PREPARACIO = 'EN_PREPARACIO'
    ENVIAT = 'ENVIAT'
    ENTREGAT = 'ENTREGAT'
    CANCELAT = 'CANCELAT'

    ESTAT_CHOICES = [
        (PENDENT, 'Pendent'),
        (EN_PREPARACIO, 'En Preparació'),
        (ENVIAT, 'Enviat'),
        (ENTREGAT, 'Entregat'),
        (CANCELAT, 'Cancel·lat'),
    ]
    numero_albara = models.CharField(unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='albarans')
    data_creacio = models.DateTimeField(auto_now_add=True)
    data_entrega_prevista = models.DateField()
    estat = models.CharField(choices=ESTAT_CHOICES, default=PENDENT)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    observacions = models.TextField(null=True, blank=True)

    def calcular_total(self):
        self.total = sum(linea.subtotal for linea in self.lineas.all())
        self.save()
        return self.total

class LineaAlbara(models.Model):
    albara = models.ForeignKey(Albara, on_delete=models.CASCADE, related_name='lineas')
    nom_producte = models.CharField()
    quantitat = models.IntegerField()
    preu_unitari = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.CharField(null=True, blank=True)

    def save(self, *args, **kwargs):
        self.subtotal = self.quantitat * self.preu_unitari
        super().save(*args, **kwargs)
        self.albara.calcular_total()

    def delete(self, *args, **kwargs):
        albara = self.albara

        super().delete(*args, **kwargs)
        albara.calcular_total()