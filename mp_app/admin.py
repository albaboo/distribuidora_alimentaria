from django.contrib import admin

from mp_app.models import Client, Albara, LiniaAlbara, Empleat, Categoria, Producte, Magatzem, StockMagatzem

# Register your models here.

admin.site.register(Client)
admin.site.register(Categoria)
admin.site.register(Producte)
admin.site.register(Magatzem)
admin.site.register(StockMagatzem)
admin.site.register(Empleat)
admin.site.register(Albara)
admin.site.register(LiniaAlbara)