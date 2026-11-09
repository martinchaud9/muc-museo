from django.urls import path

from . import views

app_name = 'analitica'

urlpatterns = [
    path('evento/', views.registrar_evento, name='evento'),
]
