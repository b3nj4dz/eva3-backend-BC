import uuid
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from apps.inventario.models import EquipoInformatico
from .models import SolicitudCotizacion, ItemCotizacion


def _fmt(valor):
    """Función auxiliar para formatear números con punto de miles (ej: 399000 -> 399.000)"""
    return f"{int(valor):,}".replace(",", ".")


def _obtener_cotizacion(request):
    """Auxiliar para obtener o inicializar la cotización en sesión"""
    return request.session.setdefault('cotizacion', {})


# 1. Vista de la Canasta / Presupuesto en Sesión
def cotizacion_ver(request):
    cotizacion = _obtener_cotizacion(request)
    
    subtotal_general = sum(item['subtotal'] for item in cotizacion.values())
    total_garantia = sum(item['garantia'] * item['cantidad'] for item in cotizacion.values())
    iva = int(subtotal_general * 0.19)
    total_sin_deposito = subtotal_general + iva
    total_final = total_sin_deposito + total_garantia

    # Formatear elementos individuales para la plantilla
    items_formateados = []
    for item in cotizacion.values():
        item_copy = item.copy()
        item_copy['tarifa_diaria_fmt'] = _fmt(item['tarifa_diaria'])
        item_copy['subtotal_fmt'] = _fmt(item['subtotal'])
        items_formateados.append(item_copy)

    return render(request, 'cotizaciones/cotizacion.html', {
        'items_cotizacion': items_formateados,
        'subtotal_arriendo': subtotal_general,
        'subtotal_arriendo_fmt': _fmt(subtotal_general),
        'total_garantia': total_garantia,
        'total_garantia_fmt': _fmt(total_garantia),
        'iva': iva,
        'iva_fmt': _fmt(iva),
        'total_sin_deposito_fmt': _fmt(total_sin_deposito),
        'total_final': total_final,
        'total_final_fmt': _fmt(total_final),
        'esta_vacio': len(cotizacion) == 0,
    })


# 2. Agregar Equipo a la Sesión (Arriendo o Venta)
def cotizacion_agregar(request, id):
    equipo = get_object_or_404(EquipoInformatico, id=id, activo=True)
    cotizacion = _obtener_cotizacion(request)
    modalidad = request.GET.get('modalidad', 'arriendo')  # 'arriendo' o 'venta'

    if equipo.estado != 'DISPONIBLE' or equipo.stock == 0:
        messages.warning(request, f"'{equipo.nombre}' no está disponible para compra o arriendo.")
        return redirect(request.META.get('HTTP_REFERER') or 'cotizaciones:ver')
    
    item_key = f"{equipo.id}_{modalidad}"

    dias_actuales = cotizacion.get(item_key, {}).get('dias', 1)
    cantidad_actual = cotizacion.get(item_key, {}).get('cantidad', 0)
    cantidad_total = sum(
        item.get('cantidad', 0)
        for item in cotizacion.values()
        if item.get('equipo_id') == equipo.id
    )
    nueva_cantidad = cantidad_actual + 1

    if cantidad_total + 1 > equipo.stock:
        messages.warning(request, f"Límite de stock alcanzado ({equipo.stock} unidades) para '{equipo.nombre}'.")
        return redirect('cotizaciones:ver')

    imagen_url = equipo.imagen.url if equipo.imagen else ''

    if modalidad == 'venta':
        precio_unitario = int(equipo.precio_venta)
        garantia_unitario = 0
        dias_aplicados = 1
        subtotal_item = precio_unitario * nueva_cantidad
    else:
        precio_unitario = int(equipo.tarifa_diaria)
        garantia_unitario = int(equipo.monto_garantia)
        dias_aplicados = dias_actuales
        subtotal_item = precio_unitario * nueva_cantidad * dias_aplicados

    cotizacion[item_key] = {
        'id_key': item_key,
        'equipo_id': equipo.id,
        'sku': equipo.codigo_sku,
        'nombre': equipo.nombre,
        'slug': equipo.slug,
        'categoria': equipo.categoria.nombre,
        'modalidad': modalidad,
        'tarifa_diaria': precio_unitario,
        'garantia': garantia_unitario,
        'cantidad': nueva_cantidad,
        'dias': dias_aplicados,
        'subtotal': subtotal_item,
        'imagen_url': imagen_url,
    }

    request.session.modified = True
    messages.success(request, f"'{equipo.nombre}' ({modalidad.capitalize()}) agregado al presupuesto.")
    return redirect(request.META.get('HTTP_REFERER') or 'cotizaciones:ver')


# 3. Modificar Días de Arriendo
def cotizacion_modificar_dias(request, id, accion):
    cotizacion = _obtener_cotizacion(request)
    item_key = str(id)
    
    if item_key in cotizacion:
        if cotizacion[item_key]['modalidad'] == 'arriendo':
            if accion == 'sumar_dia':
                cotizacion[item_key]['dias'] += 1
            elif accion == 'restar_dia' and cotizacion[item_key]['dias'] > 1:
                cotizacion[item_key]['dias'] -= 1
            
            cotizacion[item_key]['subtotal'] = (
                cotizacion[item_key]['tarifa_diaria'] * 
                cotizacion[item_key]['cantidad'] * 
                cotizacion[item_key]['dias']
            )
            request.session.modified = True
    return redirect('cotizaciones:ver')


# 4. Modificar Unidades de Compra o Arriendo
def cotizacion_modificar_cantidad(request, id, accion):
    cotizacion = _obtener_cotizacion(request)
    item_key = str(id)
    item = cotizacion.get(item_key)

    if item is None:
        return redirect('cotizaciones:ver')

    if accion == 'sumar_unidad':
        equipo = EquipoInformatico.objects.filter(id=item['equipo_id']).first()
        if equipo is None or not equipo.activo:
            messages.error(request, "Este equipo ya no está disponible.")
            return redirect('cotizaciones:ver')

        cantidad_total = sum(
            carrito_item.get('cantidad', 0)
            for carrito_item in cotizacion.values()
            if carrito_item.get('equipo_id') == equipo.id
        )
        if cantidad_total >= equipo.stock:
            messages.warning(
                request,
                f"Stock máximo alcanzado ({equipo.stock} unidades) para '{equipo.nombre}'.",
            )
            return redirect('cotizaciones:ver')
        item['cantidad'] += 1
    elif accion == 'restar_unidad' and item['cantidad'] > 1:
        item['cantidad'] -= 1
    else:
        return redirect('cotizaciones:ver')

    dias = item['dias'] if item['modalidad'] == 'arriendo' else 1
    item['subtotal'] = item['tarifa_diaria'] * item['cantidad'] * dias
    request.session.modified = True
    return redirect('cotizaciones:ver')


# 4. Eliminar Elemento Individual
def cotizacion_eliminar(request, id):
    cotizacion = _obtener_cotizacion(request)
    item_key = str(id)
    if item_key in cotizacion:
        del cotizacion[item_key]
        request.session.modified = True
        messages.warning(request, "Equipo eliminado del presupuesto.")
    return redirect('cotizaciones:ver')


# 5. Vaciar Sesión
def cotizacion_limpiar(request):
    if 'cotizacion' in request.session:
        del request.session['cotizacion']
        request.session.modified = True
    return redirect('cotizaciones:ver')


# 6. Comprobante Simulado
@login_required
@require_POST
def comprobante_simulado(request):
    cotizacion = _obtener_cotizacion(request)
    if not cotizacion:
        return redirect('inventario:lista')

    cantidades_por_equipo = {}
    for item in cotizacion.values():
        equipo_id = item['equipo_id']
        cantidades_por_equipo[equipo_id] = (
            cantidades_por_equipo.get(equipo_id, 0) + item['cantidad']
        )

    subtotal_general = sum(item['subtotal'] for item in cotizacion.values())
    total_garantia = sum(item['garantia'] * item['cantidad'] for item in cotizacion.values())
    iva = int(subtotal_general * 0.19)
    total_sin_deposito = subtotal_general + iva
    total_final = total_sin_deposito + total_garantia
    items_cotizados = list(cotizacion.values())
    items_para_plantilla = [dict(i, subtotal_fmt=_fmt(i['subtotal'])) for i in items_cotizados]

    codigo_generado = f"COT-TR-{request.user.id}-{uuid.uuid4().hex[:6].upper()}"

    with transaction.atomic():
        equipos = {
            equipo.id: equipo
            for equipo in EquipoInformatico.objects.select_for_update()
            .filter(id__in=cantidades_por_equipo)
            .order_by('id')
        }

        for equipo_id, cantidad in cantidades_por_equipo.items():
            equipo = equipos.get(equipo_id)
            if equipo is None or not equipo.activo or equipo.estado != 'DISPONIBLE':
                messages.error(request, "Uno de los equipos ya no está disponible. Actualiza tu presupuesto.")
                return redirect('cotizaciones:ver')
            if equipo.stock < cantidad:
                messages.error(
                    request,
                    f"Stock insuficiente para '{equipo.nombre}'. "
                    f"Disponibles: {equipo.stock}; solicitadas: {cantidad}.",
                )
                return redirect('cotizaciones:ver')

        for equipo_id, cantidad in cantidades_por_equipo.items():
            equipo = equipos[equipo_id]
            equipo.stock -= cantidad
            if equipo.stock == 0:
                equipo.estado = 'NO_DISPONIBLE'
            equipo.save(update_fields=['stock', 'fecha_actualizacion'])

        solicitud = SolicitudCotizacion.objects.create(
            codigo=codigo_generado,
            usuario=request.user,
            subtotal=subtotal_general,
            garantia=total_garantia,
            iva=iva,
            total=total_final
        )

        for item in items_cotizados:
            ItemCotizacion.objects.create(
                solicitud=solicitud,
                nombre_equipo=f"{item['nombre']} ({item['modalidad'].capitalize()})",
                codigo_sku=item['sku'],
                dias=item['dias'],
                cantidad=item['cantidad'],
                subtotal_item=item['subtotal']
            )

    del request.session['cotizacion']
    request.session.modified = True

    return render(request, 'cotizaciones/comprobante_exito.html', {
        'items': items_para_plantilla,
        'subtotal_fmt': _fmt(subtotal_general),
        'garantia_fmt': _fmt(total_garantia),
        'total_garantia': total_garantia,
        'iva_fmt': _fmt(iva),
        'total_sin_deposito_fmt': _fmt(total_sin_deposito),
        'total_fmt': _fmt(total_final),
        'codigo_cotizacion': codigo_generado,
    })