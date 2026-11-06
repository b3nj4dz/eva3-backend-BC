from django.shortcuts import render
from apps.inventario.models import EquipoInformatico, CategoriaEquipo


def inicio(request):
    """Portada con equipos destacados y categorías de flota"""
    destacados = EquipoInformatico.objects.filter(
        activo=True, 
        destacado=True
    ).select_related('categoria')[:4]

    categorias = CategoriaEquipo.objects.filter(activo=True)[:4]

    return render(request, 'core/index.html', {
        'destacados': destacados,
        'categorias': categorias,
        'total_equipos': EquipoInformatico.objects.filter(activo=True).count(),
    })


def nosotros(request):
    """Página sobre el servicio de leasing y arriendo corporativo"""
    return render(request, 'core/nosotros.html')