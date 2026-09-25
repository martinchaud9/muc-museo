from django.shortcuts import get_object_or_404, render
from django.utils import timezone
from django.db.models import Q

from .models import FotoPortada, Obra, Presentacion


def inicio(request):
    hoy = timezone.localdate()
    proximas = (Presentacion.objects.filter(publicada=True)
                .filter(Q(fecha_fin__gte=hoy) | Q(fecha_fin__isnull=True, fecha_inicio__gte=hoy))
                .order_by('fecha_inicio')[:3])
    return render(request, 'museo/inicio.html', {
        'fotos': FotoPortada.objects.filter(activa=True),
        'proximas': proximas,
        'destacadas': Obra.objects.all()[:4],
    })


def presentaciones(request):
    hoy = timezone.localdate()
    publicadas = Presentacion.objects.filter(publicada=True)
    vigentes = publicadas.filter(Q(fecha_fin__gte=hoy) | Q(fecha_fin__isnull=True, fecha_inicio__gte=hoy)).order_by('fecha_inicio')
    pasadas = publicadas.exclude(pk__in=vigentes)
    return render(request, 'museo/presentaciones.html', {'vigentes': vigentes, 'pasadas': pasadas})


def presentacion_detalle(request, pk):
    p = get_object_or_404(Presentacion, pk=pk, publicada=True)
    return render(request, 'museo/presentacion_detalle.html', {'p': p})


def galeria(request):
    return render(request, 'museo/galeria.html', {'obras': Obra.objects.all()})


def sala_virtual(request):
    obras = list(Obra.objects.filter(en_sala_virtual=True)[:13])
    datos = [{
        'id': o.pk, 'titulo': o.titulo, 'autor': o.autor, 'anio': o.anio,
        'tecnica': o.tecnica, 'dimensiones': o.dimensiones, 'descripcion': o.descripcion,
        'ancho': o.imagen.width, 'alto': o.imagen.height,
    } for o in obras]
    return render(request, 'museo/sala_virtual.html', {'obras': obras, 'obras_data': datos})
