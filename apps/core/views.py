from django.shortcuts import render
from apps.inventario.models import EquipoInformatico, CategoriaEquipo


def inicio(request):
    # Consultar los equipos destacados que estén activos
    equipos_destacados = EquipoInformatico.objects.filter(destacado=True, activo=True)[:6]
    
    # Consultar todas las categorías (sin el filtro activo=True)
    categorias = CategoriaEquipo.objects.all()

    return render(request, 'core/index.html', {
        'equipos_destacados': equipos_destacados,
        'categorias': categorias,
    })


def nosotros(request):
    return render(request, 'core/nosotros.html')