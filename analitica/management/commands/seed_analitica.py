"""Genera visitas de DEMOSTRACIÓN para mostrar el panel de estadísticas sin tener el sitio publicado.

Los visitantes generados tienen códigos que empiezan con «demo-», y el panel avisa cuando existen.
    python manage.py seed_analitica              # 30 días, ~300 visitantes
    python manage.py seed_analitica --borrar     # elimina solo los datos de demostración
"""
import random
import uuid
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from analitica.models import Evento
from museo.models import Obra, Presentacion

ORIGENES = [('qr-biblioteca', 22), ('qr-pasillo-central', 12), ('instagram', 25), ('whatsapp', 14),
            ('directo', 20), ('google', 5), ('facebook', 2)]


class Command(BaseCommand):
    help = 'Genera (o borra con --borrar) visitas de demostración para el panel de estadísticas.'

    def add_arguments(self, parser):
        parser.add_argument('--dias', type=int, default=30)
        parser.add_argument('--visitantes', type=int, default=300)
        parser.add_argument('--borrar', action='store_true', help='Elimina los datos de demostración y termina.')

    def handle(self, *args, dias, visitantes, borrar, **opts):
        borrados, _ = Evento.objects.filter(visitante__startswith='demo-').delete()
        if borrar:
            self.stdout.write(self.style.SUCCESS(f'{borrados} eventos de demostración eliminados.'))
            return

        rnd = random.Random(2026)
        obras = list(Obra.objects.values_list('id', flat=True))
        pres = list(Presentacion.objects.values_list('id', flat=True))
        ahora = timezone.now()
        eventos = []
        codigo = lambda: 'demo-' + uuid.UUID(int=rnd.getrandbits(128)).hex[:20]

        def ev(tipo, vis, ses, origen, fecha, **extra):
            eventos.append(Evento(tipo=tipo, visitante=vis, sesion=ses, origen=origen, fecha=fecha, **extra))

        for _ in range(visitantes):
            vis = codigo()
            usa_a11y = rnd.random() < 0.12
            for _ in range(rnd.choices([1, 2, 3], weights=[70, 22, 8])[0]):
                # Más visitas hacia el final del período, como si la difusión fuera creciendo.
                hace = dias * (1 - rnd.random() ** 0.6)
                t = ahora - timedelta(days=hace, minutes=rnd.randint(0, 600))
                ses, origen = codigo(), rnd.choices([o for o, _ in ORIGENES], weights=[w for _, w in ORIGENES])[0]
                paginas = ['/'] + rnd.sample(['/presentaciones/', '/obras/', '/obras/sala-virtual/'], k=rnd.randint(0, 3))
                for ruta in paginas:
                    t += timedelta(seconds=rnd.randint(10, 90))
                    ev('pagina', vis, ses, origen, t, ruta=ruta)
                    if ruta == '/presentaciones/' and pres and rnd.random() < 0.6:
                        ev('presentacion', vis, ses, origen, t + timedelta(seconds=20), ruta='/presentaciones/x/',
                           objeto_id=rnd.choice(pres))
                    if ruta == '/obras/' and obras:
                        for o in rnd.sample(obras, k=rnd.randint(0, min(3, len(obras)))):
                            ev('obra', vis, ses, origen, t + timedelta(seconds=15), ruta=ruta, objeto_id=o, detalle='galeria')
                    if ruta == '/obras/sala-virtual/':
                        ev('sala_entrada', vis, ses, origen, t, ruta=ruta)
                        ev('sala_tiempo', vis, ses, origen, t + timedelta(minutes=3), ruta=ruta,
                           valor=int(rnd.lognormvariate(5.2, 0.6)))   # mediana ≈ 3 minutos
                        for o in (rnd.sample(obras, k=rnd.randint(1, len(obras))) if obras else []):
                            ev('obra', vis, ses, origen, t + timedelta(seconds=30), ruta=ruta, objeto_id=o, detalle='sala')
                            if usa_a11y and rnd.random() < 0.5:
                                ev('a11y_leer', vis, ses, origen, t + timedelta(seconds=40), ruta=ruta, objeto_id=o)
                        if usa_a11y and rnd.random() < 0.25:
                            ev('a11y_voz', vis, ses, origen, t + timedelta(seconds=10), ruta=ruta)
                if usa_a11y and rnd.random() < 0.4:
                    ev('a11y_opcion', vis, ses, origen, t, ruta='/',
                       detalle=rnd.choices(Evento.OPCIONES_ACCESIBILIDAD, weights=[35, 25, 25, 15])[0])

        Evento.objects.bulk_create(eventos, batch_size=1000)
        self.stdout.write(self.style.SUCCESS(f'{len(eventos)} eventos de demostración creados ({visitantes} visitantes, {dias} días).'))
