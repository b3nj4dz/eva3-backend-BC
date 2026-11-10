from django.contrib import admin
from .models import CategoriaEquipo, EquipoInformatico


@admin.register(CategoriaEquipo)
class CategoriaEquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'descripcion')
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}


@admin.register(EquipoInformatico)
class EquipoInformaticoAdmin(admin.ModelAdmin):
    list_display = ('codigo_sku', 'nombre', 'categoria', 'tarifa_diaria', 'precio_venta', 'stock', 'estado', 'activo')
    list_filter = ('categoria', 'estado', 'activo', 'destacado')
    search_fields = ('codigo_sku', 'nombre', 'especificaciones')
    list_editable = ('tarifa_diaria', 'precio_venta', 'stock', 'estado', 'activo')
    prepopulated_fields = {'slug': ('codigo_sku', 'nombre')}