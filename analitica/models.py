from django.db import models
from django.utils import timezone


class Evento(models.Model):
    """Una acción de un visitante en el sitio. Es anónima: el visitante se identifica con un
    código aleatorio guardado en su navegador, sin nombre, correo ni dirección IP."""
    TIPOS = [
        ('pagina', 'Página vista'),
        ('obra', 'Obra vista'),
        ('presentacion', 'Presentación vista'),
        ('sala_entrada', 'Entrada a la sala virtual'),
        ('sala_tiempo', 'Tiempo en la sala virtual'),
        ('a11y_leer', 'Escuchó una descripción'),
        ('a11y_voz', 'Activó el control por voz'),
        ('a11y_opcion', 'Activó una opción de accesibilidad'),
    ]
    OPCIONES_ACCESIBILIDAD = ['texto-grande', 'alto-contraste', 'daltonismo', 'sin-animaciones']

    tipo = models.CharField(max_length=20, choices=TIPOS)
    visitante = models.CharField(max_length=40, db_index=True)
    sesion = models.CharField(max_length=40, db_index=True)
    origen = models.CharField(max_length=30, default='directo')
    ruta = models.CharField(max_length=200, blank=True)
    objeto_id = models.PositiveIntegerField(null=True, blank=True, help_text='Obra o presentación, según el tipo.')
    valor = models.PositiveIntegerField(null=True, blank=True, help_text='Segundos, en «Tiempo en la sala virtual».')
    detalle = models.CharField(max_length=30, blank=True, help_text='«galeria» o «sala» en obras vistas; la opción activada en accesibilidad.')
    fecha = models.DateTimeField(default=timezone.now, db_index=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'evento'
        verbose_name_plural = 'eventos'
        indexes = [models.Index(fields=['tipo', 'fecha'])]

    def __str__(self):
        return f'{self.get_tipo_display()} · {self.fecha:%d/%m/%Y %H:%M}'
