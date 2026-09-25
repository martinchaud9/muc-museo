"""Carga los datos iniciales: superusuario, fotos de portada, obras y presentaciones de ejemplo.

Las fotos (tomadas en el MUC) están en museo/datos_iniciales/. Los datos de las obras
(título, autor, año) son provisorios y se completan desde el panel /admin/.
"""
from datetime import timedelta
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand
from django.utils import timezone

from museo.models import FotoPortada, Obra, Presentacion

DATOS = Path(__file__).resolve().parents[2] / 'datos_iniciales'

PORTADA = [
    ('muc-4.jpg', 'Sala principal del MUC', 'center 55%'),
    ('muc-3.jpg', 'Obra en la sala principal', 'center 45%'),
    ('muc-2.jpg', 'Ingreso a las salas', 'center 40%'),
]

PENDIENTE = ' Datos a completar: título, autor, año y técnica.'
OBRAS = [
    ('arboles.jpg', 'Sendero entre árboles', 'Óleo sobre tela',
     'Paisaje de un camino bordeado de árboles, trabajado con pinceladas sueltas en verdes, amarillos y rosados.'),
    ('sala_espera.jpg', 'Escena de interior con personajes', 'Óleo sobre tela',
     'Pintura de tono surrealista: figuras fantásticas reunidas en un interior iluminado por un foco cenital.'),
    ('rojo.jpg', 'Composición en rojo y negro', 'Acrílico sobre tela',
     'Obra abstracta con una franja central de formas geométricas quebradas sobre un fondo rojo intenso.'),
    ('retrato.jpg', 'Retrato frente al marco', 'Fotografía',
     'Fotografía en blanco y negro: una mujer sostiene un marco que devuelve su propia mirada.'),
    ('campana.jpg', 'Campanario', 'Fotografía',
     'Detalle arquitectónico de un campanario de estilo neogótico, en tonos violáceos.'),
]


class Command(BaseCommand):
    help = 'Crea el usuario administrador y carga fotos de portada, obras y presentaciones iniciales.'

    def handle(self, *args, **opts):
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@muc.ucse.edu.ar', 'admin12345')
            self.stdout.write('Usuario admin / admin12345 creado.')

        if not FotoPortada.objects.exists():
            for i, (archivo, titulo, enfoque) in enumerate(PORTADA):
                f = FotoPortada(titulo=titulo, enfoque=enfoque, orden=i)
                with open(DATOS / 'portada' / archivo, 'rb') as fh:
                    f.imagen.save(archivo, File(fh), save=False)
                f.save()
            self.stdout.write(f'{len(PORTADA)} fotos de portada cargadas.')

        if not Obra.objects.exists():
            for i, (archivo, titulo, tecnica, desc) in enumerate(OBRAS):
                o = Obra(titulo=titulo, autor='Autor a identificar', tecnica=tecnica,
                         descripcion=desc + PENDIENTE, orden=i)
                with open(DATOS / 'obras' / archivo, 'rb') as fh:
                    o.imagen.save(archivo, File(fh), save=False)
                o.save()
            self.stdout.write(f'{len(OBRAS)} obras cargadas.')

        if not Presentacion.objects.exists():
            hoy = timezone.localdate()
            datos = [
                ('Miradas del monte', 'exposicion', 'Pintura santiagueña del siglo XX en diálogo con el paisaje.',
                 hoy - timedelta(days=10), hoy + timedelta(days=45), 'Lunes a viernes de 9 a 13 y de 17 a 20 h', 'arboles.jpg'),
                ('Imagen y memoria', 'muestra', 'Muestra de fotografía contemporánea de artistas locales.',
                 hoy + timedelta(days=12), hoy + timedelta(days=60), 'Lunes a viernes de 9 a 13 y de 17 a 20 h', 'retrato.jpg'),
                ('Charla: el patrimonio universitario', 'charla', 'Encuentro abierto sobre la historia de la colección del MUC.',
                 hoy + timedelta(days=20), None, 'Jueves 19 h', 'sala_espera.jpg'),
                ('Taller de pintura abstracta', 'taller', 'Taller introductorio gratuito con inscripción previa.',
                 hoy - timedelta(days=90), hoy - timedelta(days=60), 'Sábados de 10 a 12 h', 'rojo.jpg'),
            ]
            for titulo, tipo, resumen, ini, fin, horario, img in datos:
                p = Presentacion(titulo=titulo, tipo=tipo, resumen=resumen, fecha_inicio=ini, fecha_fin=fin, horario=horario,
                                 descripcion=resumen + '\n\nTexto de ejemplo: reemplazar desde el panel de administración.')
                with open(DATOS / 'obras' / img, 'rb') as fh:
                    p.imagen.save(f'presentacion-{tipo}.jpg', File(fh), save=False)
                p.save()
            self.stdout.write(f'{len(datos)} presentaciones de ejemplo creadas.')
        self.stdout.write(self.style.SUCCESS('Datos iniciales listos.'))
