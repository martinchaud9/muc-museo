from django.contrib import admin

from .models import Evento


@admin.register(Evento)
class EventoAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tipo', 'origen', 'ruta', 'objeto_id', 'detalle')
    list_filter = ('tipo', 'origen')
    date_hierarchy = 'fecha'

    # Los eventos los genera el sitio: desde el admin solo se consultan.
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
