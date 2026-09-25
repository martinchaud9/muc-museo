from django.contrib import admin

from .models import FotoPortada, Obra, Presentacion

admin.site.site_header = 'MUC · Administración'
admin.site.site_title = 'MUC'
admin.site.index_title = 'Contenido del sitio'


@admin.register(FotoPortada)
class FotoPortadaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'orden', 'activa')
    list_editable = ('orden', 'activa')


@admin.register(Presentacion)
class PresentacionAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'tipo', 'fecha_inicio', 'fecha_fin', 'publicada')
    list_filter = ('tipo', 'publicada')
    search_fields = ('titulo', 'descripcion')


@admin.register(Obra)
class ObraAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'anio', 'en_sala_virtual', 'orden')
    list_editable = ('en_sala_virtual', 'orden')
    search_fields = ('titulo', 'autor')
