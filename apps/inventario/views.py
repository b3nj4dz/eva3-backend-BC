from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import EquipoInformatico, CategoriaEquipo
from .forms import EquipoInformaticoForm


def es_administrador(user):
    """Verifica si el usuario es staff o superusuario para proteger el Backoffice"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)


# --- OPERACIÓN READ (Catálogo Público) ---
def equipo_lista(request):
    query = request.GET.get('q', '').strip()
    categoria_slug = request.GET.get('categoria', '')
    orden = request.GET.get('orden', '-fecha_creacion')

    equipos = EquipoInformatico.objects.filter(activo=True).select_related('categoria')

    if categoria_slug:
        equipos = equipos.filter(categoria__slug=categoria_slug)

    # Buscador multi-campo con objeto Q (búsqueda simultánea requerida)
    if query:
        equipos = equipos.filter(
            Q(nombre__icontains=query) |
            Q(codigo_sku__icontains=query) |
            Q(especificaciones__icontains=query) |
            Q(categoria__nombre__icontains=query)
        )

    ordenes_validos = {
        'precio_asc': 'tarifa_diaria',
        'precio_desc': '-tarifa_diaria',
        'nombre_asc': 'nombre',
        'recientes': '-fecha_creacion',
    }
    equipos = equipos.order_by(ordenes_validos.get(orden, '-fecha_creacion'))

    # Paginación con Paginator (6 ítems por página)
    paginador = Paginator(equipos, 6)
    pagina = paginador.get_page(request.GET.get('page'))
    categorias = CategoriaEquipo.objects.filter(activo=True)

    return render(request, 'inventario/equipo_lista.html', {
        'equipos': pagina,
        'categorias': categorias,
        'categoria_seleccionada': categoria_slug,
        'query_actual': query,
        'orden_actual': orden,
        'total_resultados': equipos.count(),
    })


def equipo_detalle(request, slug):
    equipo = get_object_or_404(EquipoInformatico.objects.select_related('categoria'), slug=slug, activo=True)
    relacionados = EquipoInformatico.objects.filter(categoria=equipo.categoria, activo=True).exclude(pk=equipo.pk)[:3]
    return render(request, 'inventario/equipo_detalle.html', {'equipo': equipo, 'relacionados': relacionados})


# --- OPERACIONES BACKOFFICE PROTEGIDAS (CRUD) ---
@login_required
@user_passes_test(es_administrador, login_url='inventario:lista')
def gestion_equipos(request):
    query = request.GET.get('q', '').strip()
    equipos = EquipoInformatico.objects.all().select_related('categoria')
    if query:
        equipos = equipos.filter(Q(nombre__icontains=query) | Q(codigo_sku__icontains=query))
    
    paginador = Paginator(equipos.order_by('-fecha_creacion'), 10)
    pagina = paginador.get_page(request.GET.get('page'))
    return render(request, 'inventario/gestion_equipos.html', {'equipos': pagina, 'query': query})


# OPERACIÓN CREATE (C)
@login_required
@user_passes_test(es_administrador, login_url='inventario:lista')
def equipo_crear(request):
    if request.method == 'POST':
        form = EquipoInformaticoForm(request.POST, request.FILES)
        if form.is_valid():
            equipo = form.save()
            messages.success(request, f"¡Equipo '[{equipo.codigo_sku}] {equipo.nombre}' registrado con éxito!")
            return redirect('inventario:gestion')
    else:
        form = EquipoInformaticoForm()
    return render(request, 'inventario/equipo_form.html', {'form': form, 'titulo_accion': 'Ingresar Nuevo Equipo Informático', 'boton_texto': 'Guardar Equipo'})


# OPERACIÓN UPDATE (U)
@login_required
@user_passes_test(es_administrador, login_url='inventario:lista')
def equipo_editar(request, id):
    equipo = get_object_or_404(EquipoInformatico, id=id)
    if request.method == 'POST':
        form = EquipoInformaticoForm(request.POST, request.FILES, instance=equipo)
        if form.is_valid():
            form.save()
            messages.success(request, f"Equipo '[{equipo.codigo_sku}]' actualizado correctamente.")
            return redirect('inventario:gestion')
    else:
        form = EquipoInformaticoForm(instance=equipo)
    return render(request, 'inventario/equipo_form.html', {'form': form, 'equipo': equipo, 'titulo_accion': 'Editar Equipo Informático', 'boton_texto': 'Actualizar'})


# OPERACIÓN DELETE (D)
@login_required
@user_passes_test(es_administrador, login_url='inventario:lista')
def equipo_eliminar(request, id):
    equipo = get_object_or_404(EquipoInformatico, id=id)
    if request.method == 'POST':
        nombre = equipo.nombre
        equipo.delete()
        messages.success(request, f"Equipo '{nombre}' eliminado del sistema.")
        return redirect('inventario:gestion')
    return render(request, 'inventario/equipo_confirmar_eliminar.html', {'equipo': equipo})