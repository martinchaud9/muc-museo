import json

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Evento

VIS = 'a1b2c3d4-0000-4000-8000-000000000001'
SES = 'a1b2c3d4-0000-4000-8000-000000000002'


class RegistrarEventoTests(TestCase):
    def enviar(self, **datos):
        cuerpo = {'tipo': 'pagina', 'visitante': VIS, 'sesion': SES, 'origen': 'qr-biblioteca', 'ruta': '/', **datos}
        return self.client.post(reverse('analitica:evento'), json.dumps(cuerpo), content_type='application/json')

    def test_guarda_evento_valido(self):
        self.assertEqual(self.enviar().status_code, 204)
        e = Evento.objects.get()
        self.assertEqual((e.tipo, e.origen, e.ruta), ('pagina', 'qr-biblioteca', '/'))

    def test_rechaza_tipo_desconocido_y_codigos_invalidos(self):
        self.assertEqual(self.enviar(tipo='hackeo').status_code, 400)
        self.assertEqual(self.enviar(visitante='x').status_code, 400)
        self.assertEqual(self.client.post(reverse('analitica:evento'), 'no es json', content_type='application/json').status_code, 400)
        self.assertFalse(Evento.objects.exists())

    def test_origen_invalido_se_guarda_como_otro_y_tiempo_se_limita(self):
        self.enviar(tipo='sala_tiempo', origen='<script>', valor=10**9)
        e = Evento.objects.get()
        self.assertEqual(e.origen, 'otro')
        self.assertEqual(e.valor, 4 * 3600)

    def test_opcion_de_accesibilidad_debe_ser_conocida(self):
        self.assertEqual(self.enviar(tipo='a11y_opcion', detalle='daltonismo').status_code, 204)
        self.assertEqual(self.enviar(tipo='a11y_opcion', detalle='otra').status_code, 400)

    def test_no_cuenta_al_personal_del_museo(self):
        staff = get_user_model().objects.create_user('staff', password='x', is_staff=True)
        self.client.force_login(staff)
        self.assertEqual(self.enviar().status_code, 204)
        self.assertFalse(Evento.objects.exists())

    def test_solo_acepta_post(self):
        self.assertEqual(self.client.get(reverse('analitica:evento')).status_code, 405)


class PanelEstadisticasTests(TestCase):
    def test_requiere_personal(self):
        r = self.client.get(reverse('estadisticas'))
        self.assertEqual(r.status_code, 302)

    def test_muestra_metricas(self):
        for tipo, extra in [('pagina', {}), ('sala_entrada', {}), ('sala_tiempo', {'valor': 120}),
                            ('a11y_opcion', {'detalle': 'alto-contraste'})]:
            Evento.objects.create(tipo=tipo, visitante=VIS, sesion=SES, origen='instagram', **extra)
        admin = get_user_model().objects.create_superuser('admin', 'a@a.com', 'x')
        self.client.force_login(admin)
        r = self.client.get(reverse('estadisticas'), {'dias': 7})
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['resumen']['visitantes'], 1)
        self.assertEqual(r.context['sala']['tiempo_medio'], 2.0)
        self.assertEqual(r.context['accesibilidad']['pct'], 100)
        self.assertContains(r, 'Instagram')
        self.assertContains(r, 'Alto contraste')
