from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from .models import CategoriaEquipo, EquipoInformatico
from .forms import EquipoInformaticoForm


def _es_staff(user):
    return user.is_staff


# 1. Catálogo Público de Equipos
def equipo_lista(request):
    categoria_slug = request.GET.get('categoria', None)
    query = request.GET.get('q', '').strip()
    orden = request.GET.get('orden', 'recientes')

    equipos_qs = EquipoInformatico.objects.filter(activo=True)

    if categoria_slug:
        equipos_qs = equipos_qs.filter(categoria__slug=categoria_slug)

    if query:
        equipos_qs = equipos_qs.filter(
            Q(nombre__icontains=query) |
            Q(codigo_sku__icontains=query) |
            Q(especificaciones__icontains=query)
        )

    if orden == 'precio_asc':
        equipos_qs = equipos_qs.order_by('tarifa_diaria')
    elif orden == 'precio_desc':
        equipos_qs = equipos_qs.order_by('-tarifa_diaria')
    elif orden == 'nombre_asc':
        equipos_qs = equipos_qs.order_by('nombre')
    else:
        equipos_qs = equipos_qs.order_by('-fecha_creacion')

    paginator = Paginator(equipos_qs, 6)
    page_number = request.GET.get('page')
    equipos_paginados = paginator.get_page(page_number)

    categorias = CategoriaEquipo.objects.all()

    return render(request, 'inventario/equipo_lista.html', {
        'equipos': equipos_paginados,
        'categorias': categorias,
        'categoria_seleccionada': categoria_slug,
        'query_actual': query,
        'orden_actual': orden,
        'total_resultados': equipos_qs.count(),
    })


# 2. Detalle del Equipo
def equipo_detalle(request, slug):
    equipo = get_object_or_404(EquipoInformatico, slug=slug, activo=True)
    relacionados = EquipoInformatico.objects.filter(
        categoria=equipo.categoria, 
        activo=True
    ).exclude(id=equipo.id)[:3]

    return render(request, 'inventario/equipo_detalle.html', {
        'equipo': equipo,
        'relacionados': relacionados
    })


# 3. Vista Administrativa: Gestión del Inventario
@user_passes_test(_es_staff)
def equipo_gestion(request):
    equipos = EquipoInformatico.objects.all().order_by('-fecha_creacion')
    return render(request, 'inventario/equipo_gestion.html', {'equipos': equipos})


# 4. Crear Equipo
@user_passes_test(_es_staff)
def equipo_crear(request):
    if request.method == 'POST':
        form = EquipoInformaticoForm(request.POST, request.FILES)
        if form.is_valid():
            equipo = form.save()
            messages.success(request, f"Equipo '{equipo.nombre}' creado exitosamente.")
            return redirect('inventario:gestion')
    else:
        form = EquipoInformaticoForm()

    return render(request, 'inventario/equipo_form.html', {'form': form})


# 5. Editar Equipo
@user_passes_test(_es_staff)
def equipo_editar(request, id):
    equipo = get_object_or_404(EquipoInformatico, id=id)
    if request.method == 'POST':
        form = EquipoInformaticoForm(request.POST, request.FILES, instance=equipo)
        if form.is_valid():
            form.save()
            messages.success(request, f"Equipo '{equipo.nombre}' actualizado correctamente.")
            return redirect('inventario:gestion')
    else:
        form = EquipoInformaticoForm(instance=equipo)

    return render(request, 'inventario/equipo_form.html', {'form': form, 'equipo': equipo})


# 6. Eliminar Equipo (Baja lógica)
@user_passes_test(_es_staff)
def equipo_eliminar(request, id):
    equipo = get_object_or_404(EquipoInformatico, id=id)
    equipo.activo = False
    equipo.save()
    messages.warning(request, f"Equipo '{equipo.nombre}' dado de baja del catálogo.")
    return redirect('inventario:gestion')