from django.contrib import admin
from .models import CategoriaEquipo, EquipoInformatico

# Identidad Corporativa requerida por la pauta
admin.site.site_header = 'TechRental & Build - Panel de Control'
admin.site.site_title = 'TechRental Admin'
admin.site.index_title = 'Gestión Operativa de Flota y Componentes'


@admin.register(CategoriaEquipo)
class CategoriaEquipoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug', 'activo')
    search_fields = ('nombre', 'descripcion')
    prepopulated_fields = {'slug': ('nombre',)}
    list_editable = ('activo',)


@admin.register(EquipoInformatico)
class EquipoInformaticoAdmin(admin.ModelAdmin):
    # Vista tabular solicitada en la pauta
    list_display = (
        'codigo_sku', 
        'nombre', 
        'categoria', 
        'tarifa_diaria', 
        'monto_garantia', 
        'stock', 
        'estado', 
        'activo'
    )
    # Filtros laterales
    list_filter = ('categoria', 'estado', 'activo', 'destacado')
    # Búsqueda por texto
    search_fields = ('codigo_sku', 'nombre', 'especificaciones')
    # Edición rápida en grilla
    list_editable = ('tarifa_diaria', 'stock', 'estado', 'activo')
    prepopulated_fields = {'slug': ('codigo_sku', 'nombre')}
    list_per_page = 15

    # Estructura del formulario en secciones lógicas
    fieldsets = (
        ('Identificación del Recurso', {
            'fields': ('codigo_sku', 'nombre', 'slug', 'categoria', 'imagen')
        }),
        ('Especificaciones Técnicas', {
            'fields': ('especificaciones',)
        }),
        ('Valores Cuantitativos y Stock', {
            'fields': ('tarifa_diaria', 'monto_garantia', 'stock')
        }),
        ('Estado Operativo y Visibilidad', {
            'fields': ('estado', 'destacado', 'activo')
        }),
    )