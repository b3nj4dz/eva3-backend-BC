from django.urls import path
from . import views

app_name = 'inventario'

urlpatterns = [
    path('', views.equipo_lista, name='lista'),
    path('equipo/<slug:slug>/', views.equipo_detalle, name='detalle'),
    path('gestion/', views.equipo_gestion, name='gestion'),
    path('gestion/nuevo/', views.equipo_crear, name='crear'),
    path('gestion/editar/<int:id>/', views.equipo_editar, name='editar'),
    path('gestion/eliminar/<int:id>/', views.equipo_eliminar, name='eliminar'),
]