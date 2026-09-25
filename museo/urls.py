from django.urls import path

from . import views

app_name = 'museo'

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('presentaciones/', views.presentaciones, name='presentaciones'),
    path('presentaciones/<int:pk>/', views.presentacion_detalle, name='presentacion_detalle'),
    path('obras/', views.galeria, name='galeria'),
    path('obras/sala-virtual/', views.sala_virtual, name='sala_virtual'),
]
