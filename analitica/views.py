import json
import re
from datetime import timedelta
from statistics import mean, median

from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from museo.models import Obra, Presentacion

from .models import Evento

TIPOS_VALIDOS = {t for t, _ in Evento.TIPOS}
CODIGO = re.compile(r'^[A-Za-z0-9-]{8,40}$')
ORIGEN = re.compile(r'^[a-z0-9-]{1,30}$')
MAX_SEGUNDOS = 4 * 3600


@csrf_exempt   # lo envía navigator.sendBeacon, que no puede adjuntar el token CSRF; solo crea registros anónimos validados
@require_POST
def registrar_evento(request):
    if len(request.body) > 2000:
        return HttpResponseBadRequest()
    try:
        datos = json.loads(request.body)
    except (ValueError, UnicodeDecodeError):
        return HttpResponseBadRequest()
    if not isinstance(datos, dict):
        return HttpResponseBadRequest()

    tipo = datos.get('tipo')
    visitante, sesion = str(datos.get('visitante', '')), str(datos.get('sesion', ''))
    if tipo not in TIPOS_VALIDOS or not CODIGO.match(visitante) or not CODIGO.match(sesion):
        return HttpResponseBadRequest()

    # Las visitas del personal del museo (logueado en el admin) no cuentan como público.
    if request.user.is_authenticated and request.user.is_staff:
        return HttpResponse(status=204)

    origen = str(datos.get('origen') or 'directo')
    detalle = str(datos.get('detalle') or '')
    if tipo == 'a11y_opcion' and detalle not in Evento.OPCIONES_ACCESIBILIDAD:
        return HttpResponseBadRequest()
    if tipo == 'obra' and detalle not in ('galeria', 'sala'):
        detalle = ''

    def entero(clave, maximo):
        v = datos.get(clave)
        return min(v, maximo) if isinstance(v, int) and not isinstance(v, bool) and v >= 0 else None

    Evento.objects.create(
        tipo=tipo, visitante=visitante, sesion=sesion,
        origen=origen if ORIGEN.match(origen) else 'otro',
        ruta=str(datos.get('ruta') or '')[:200],
        objeto_id=entero('objeto_id', 2_000_000_000),
        valor=entero('valor', MAX_SEGUNDOS) if tipo == 'sala_tiempo' else None,
        detalle=detalle,
    )
    return HttpResponse(status=204)


NOMBRES_ORIGEN = {
    'directo': 'Acceso directo', 'instagram': 'Instagram', 'whatsapp': 'WhatsApp', 'facebook': 'Facebook',
    'x': 'X (Twitter)', 'google': 'Buscadores', 'otro-sitio': 'Otros sitios web',
}
NOMBRES_OPCION = {
    'texto-grande': 'Texto más grande', 'alto-contraste': 'Alto contraste',
    'daltonismo': 'Colores para daltonismo', 'sin-animaciones': 'Sin animaciones',
}


def nombre_origen(clave):
    if clave in NOMBRES_ORIGEN:
        return NOMBRES_ORIGEN[clave]
    if clave.startswith('qr-'):
        return 'QR · ' + clave[3:].replace('-', ' ').capitalize()
    return clave.replace('-', ' ').capitalize()


def con_porcentaje(filas, clave):
    """Agrega a cada fila el ancho de su barra (% respecto del máximo)."""
    maximo = max((f[clave] for f in filas), default=0) or 1
    for f in filas:
        f['ancho'] = round(100 * f[clave] / maximo, 1)
    return filas


@staff_member_required
def estadisticas(request):
    try:
        dias = int(request.GET.get('dias', 30))
    except ValueError:
        dias = 30
    dias = dias if dias in (7, 30, 90) else 30
    hoy = timezone.localdate()
    desde_dia = hoy - timedelta(days=dias - 1)
    eventos = Evento.objects.filter(fecha__date__gte=desde_dia)

    # --- Resumen ---
    visitantes = eventos.values('visitante').distinct().count()
    resumen = {
        'visitas': eventos.filter(tipo='pagina').count(),
        'visitantes': visitantes,
        'sesiones': eventos.values('sesion').distinct().count(),
    }

    # --- Visitas por día (los días sin visitas cuentan como 0) ---
    por_dia = {f['dia']: f for f in eventos.filter(tipo='pagina').annotate(dia=TruncDate('fecha'))
               .values('dia').annotate(visitas=Count('id'), visitantes=Count('visitante', distinct=True))}
    serie = []
    for i in range(dias):
        d = desde_dia + timedelta(days=i)
        f = por_dia.get(d, {})
        serie.append({'dia': d, 'visitas': f.get('visitas', 0), 'visitantes': f.get('visitantes', 0)})
    max_dia = max((s['visitantes'] for s in serie), default=0)
    for s in serie:
        s['alto'] = round(100 * s['visitantes'] / max_dia, 1) if max_dia else 0
    paso_etiqueta = {7: 1, 30: 5, 90: 15}[dias]

    # --- Origen de las visitas (por sesión) ---
    origenes = [{'nombre': nombre_origen(f['origen']), 'clave': f['origen'], 'sesiones': f['sesiones']}
                for f in eventos.values('origen').annotate(sesiones=Count('sesion', distinct=True)).order_by('-sesiones')]
    total_ses = sum(o['sesiones'] for o in origenes) or 1
    for o in origenes:
        o['pct'] = round(100 * o['sesiones'] / total_ses)
    con_porcentaje(origenes, 'sesiones')

    # --- Obras y presentaciones más vistas ---
    titulos_obra = dict(Obra.objects.values_list('id', 'titulo'))
    obras = [{'nombre': titulos_obra.get(f['objeto_id'], f'Obra eliminada (#{f["objeto_id"]})'), 'vistas': f['vistas'],
              'visitantes': f['visitantes']}
             for f in eventos.filter(tipo='obra', objeto_id__isnull=False).values('objeto_id')
             .annotate(vistas=Count('id'), visitantes=Count('visitante', distinct=True)).order_by('-vistas')[:10]]
    con_porcentaje(obras, 'vistas')
    titulos_pres = dict(Presentacion.objects.values_list('id', 'titulo'))
    presentaciones = [{'nombre': titulos_pres.get(f['objeto_id'], f'Presentación eliminada (#{f["objeto_id"]})'),
                       'vistas': f['vistas'], 'visitantes': f['visitantes']}
                      for f in eventos.filter(tipo='presentacion', objeto_id__isnull=False).values('objeto_id')
                      .annotate(vistas=Count('id'), visitantes=Count('visitante', distinct=True)).order_by('-vistas')[:10]]
    con_porcentaje(presentaciones, 'vistas')

    # --- Recorrido virtual ---
    sesiones_sala = set(eventos.filter(tipo='sala_entrada').values_list('sesion', flat=True))
    segundos = [f['total'] for f in eventos.filter(tipo='sala_tiempo').values('sesion').annotate(total=Sum('valor'))
                if f['total']]
    obras_por_recorrido = [f['n'] for f in eventos.filter(tipo='obra', detalle='sala').values('sesion')
                           .annotate(n=Count('objeto_id', distinct=True))]
    obras_por_recorrido += [0] * max(0, len(sesiones_sala) - len(obras_por_recorrido))
    sala = {
        'recorridos': len(sesiones_sala),
        'pct_sesiones': round(100 * len(sesiones_sala) / resumen['sesiones']) if resumen['sesiones'] else 0,
        'tiempo_medio': round(mean(segundos) / 60, 1) if segundos else 0,
        'tiempo_mediana': round(median(segundos) / 60, 1) if segundos else 0,
        'obras_medio': round(mean(obras_por_recorrido), 1) if obras_por_recorrido else 0,
    }

    # --- Funciones de accesibilidad ---
    a11y = eventos.filter(tipo__startswith='a11y_')
    usaron = a11y.values('visitante').distinct().count()
    funciones = [
        {'nombre': 'Escuchar descripción', 'veces': a11y.filter(tipo='a11y_leer').count(),
         'visitantes': a11y.filter(tipo='a11y_leer').values('visitante').distinct().count()},
        {'nombre': 'Control por voz', 'veces': a11y.filter(tipo='a11y_voz').count(),
         'visitantes': a11y.filter(tipo='a11y_voz').values('visitante').distinct().count()},
    ] + [
        {'nombre': NOMBRES_OPCION[f['detalle']], 'veces': f['veces'], 'visitantes': f['visitantes']}
        for f in a11y.filter(tipo='a11y_opcion').values('detalle')
        .annotate(veces=Count('id'), visitantes=Count('visitante', distinct=True))
    ]
    funciones.sort(key=lambda f: -f['visitantes'])
    con_porcentaje(funciones, 'visitantes')
    accesibilidad = {'usaron': usaron, 'pct': round(100 * usaron / visitantes) if visitantes else 0, 'funciones': funciones}

    contexto = {
        **admin.site.each_context(request),
        'title': 'Estadísticas del sitio',
        'dias': dias, 'desde': desde_dia, 'hasta': hoy,
        'resumen': resumen, 'serie': serie, 'max_dia': max_dia, 'paso_etiqueta': paso_etiqueta,
        'origenes': origenes, 'obras': obras, 'presentaciones': presentaciones,
        'sala': sala, 'accesibilidad': accesibilidad,
        'hay_demo': Evento.objects.filter(visitante__startswith='demo-').exists(),
    }
    return render(request, 'analitica/estadisticas.html', contexto)
