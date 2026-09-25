from django.db import models


class FotoPortada(models.Model):
    """Fotos del museo que se muestran en la portada (se rotan en el carrusel)."""
    titulo = models.CharField(max_length=120, blank=True)
    imagen = models.ImageField(upload_to='portada/')
    enfoque = models.CharField(
        max_length=30, default='center',
        help_text='Qué parte de la foto priorizar al recortarla en pantallas anchas (CSS background-position, ej. "center 40%").')
    orden = models.PositiveIntegerField(default=0)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['orden', 'id']
        verbose_name = 'foto de portada'
        verbose_name_plural = 'fotos de portada'

    def __str__(self):
        return self.titulo or f'Foto {self.pk}'


class Presentacion(models.Model):
    """Exposiciones, muestras, charlas y eventos del museo."""
    TIPOS = [
        ('exposicion', 'Exposición'),
        ('muestra', 'Muestra temporal'),
        ('charla', 'Charla / conferencia'),
        ('taller', 'Taller'),
        ('evento', 'Evento'),
    ]
    titulo = models.CharField(max_length=150)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='exposicion')
    resumen = models.CharField(max_length=250)
    descripcion = models.TextField()
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField(null=True, blank=True)
    horario = models.CharField(max_length=100, blank=True)
    lugar = models.CharField(max_length=150, default='MUC - Museo Universitario de la Cultura')
    imagen = models.ImageField(upload_to='presentaciones/', blank=True)
    publicada = models.BooleanField(default=True)

    class Meta:
        ordering = ['-fecha_inicio']
        verbose_name = 'presentación'
        verbose_name_plural = 'presentaciones'

    def __str__(self):
        return self.titulo


class Obra(models.Model):
    """Obra de arte del acervo, visible en la galería y en la sala virtual."""
    titulo = models.CharField(max_length=150)
    autor = models.CharField(max_length=150)
    anio = models.CharField('año', max_length=20, blank=True)
    tecnica = models.CharField('técnica', max_length=120, blank=True)
    dimensiones = models.CharField(max_length=60, blank=True)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(upload_to='obras/')
    en_sala_virtual = models.BooleanField('mostrar en la sala virtual', default=True)
    orden = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['orden', 'id']
        verbose_name = 'obra'
        verbose_name_plural = 'obras'

    def __str__(self):
        return f'{self.titulo} — {self.autor}'
