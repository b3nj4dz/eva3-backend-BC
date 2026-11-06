from django.urls import path
from . import views

app_name = 'cotizaciones'

urlpatterns = [
    path('', views.cotizacion_ver, name='ver'),
    path('agregar/<int:id>/', views.cotizacion_agregar, name='agregar'),
    path('modificar-dias/<str:id>/<str:accion>/', views.cotizacion_modificar_dias, name='modificar_dias'),
    path('eliminar/<str:id>/', views.cotizacion_eliminar, name='eliminar'),
    path('limpiar/', views.cotizacion_limpiar, name='limpiar'),
    path('comprobante/', views.comprobante_simulado, name='comprobante'),
]