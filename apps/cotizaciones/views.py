from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.inventario.models import EquipoInformatico


def _obtener_cotizacion(request):
    """Auxiliar para obtener o inicializar el diccionario de cotización en sesión"""
    return request.session.setdefault('cotizacion', {})


# 1. Vista de la Canasta / Cotizador en Sesión
def cotizacion_ver(request):
    cotizacion = _obtener_cotizacion(request)
    
    subtotal_arriendo = sum(item['subtotal'] for item in cotizacion.values())
    total_garantia = sum(item['garantia'] * item['cantidad'] for item in cotizacion.values())
    iva = int(subtotal_arriendo * 0.19)
    total_final = subtotal_arriendo + iva + total_garantia

    return render(request, 'cotizaciones/cotizacion.html', {
        'items_cotizacion': cotizacion.values(),
        'subtotal_arriendo': subtotal_arriendo,
        'total_garantia': total_garantia,
        'iva': iva,
        'total_final': total_final,
        'esta_vacio': len(cotizacion) == 0,
    })


# 2. Agregar Equipo a la Sesión (con control de stock/disponibilidad)
def cotizacion_agregar(request, id):
    equipo = get_object_or_404(EquipoInformatico, id=id, activo=True)
    cotizacion = _obtener_cotizacion(request)
    str_id = str(equipo.id)

    dias_actuales = cotizacion.get(str_id, {}).get('dias', 1)
    cantidad_actual = cotizacion.get(str_id, {}).get('cantidad', 0)
    nueva_cantidad = cantidad_actual + 1

    # Validación de cupos / stock exigida por la pauta
    if nueva_cantidad > equipo.stock:
        messages.warning(request, f"Límite de stock disponible alcanzado ({equipo.stock} unidades) para '{equipo.nombre}'.")
        return redirect('cotizaciones:ver')

    imagen_url = equipo.imagen.url if equipo.imagen else ''
    cotizacion[str_id] = {
        'id': equipo.id,
        'sku': equipo.codigo_sku,
        'nombre': equipo.nombre,
        'slug': equipo.slug,
        'categoria': equipo.categoria.nombre,
        'tarifa_diaria': int(equipo.tarifa_diaria),
        'garantia': int(equipo.monto_garantia),
        'cantidad': nueva_cantidad,
        'dias': dias_actuales,
        'subtotal': int(equipo.tarifa_diaria) * nueva_cantidad * dias_actuales,
        'imagen_url': imagen_url,
    }

    request.session.modified = True
    messages.success(request, f"'{equipo.nombre}' agregado al cotizador.")
    return redirect(request.META.get('HTTP_REFERER') or 'cotizaciones:ver')


# 3. Modificar Parámetros Cuantitativos (Aumentar / Disminuer días o unidades)
def cotizacion_modificar_dias(request, id, accion):
    cotizacion = _obtener_cotizacion(request)
    str_id = str(id)
    
    if str_id in cotizacion:
        if accion == 'sumar_dia':
            cotizacion[str_id]['dias'] += 1
        elif accion == 'restar_dia' and cotizacion[str_id]['dias'] > 1:
            cotizacion[str_id]['dias'] -= 1
        
        # Recalcular subtotal
        cotizacion[str_id]['subtotal'] = (
            cotizacion[str_id]['tarifa_diaria'] * 
            cotizacion[str_id]['cantidad'] * 
            cotizacion[str_id]['dias']
        )
        request.session.modified = True
    return redirect('cotizaciones:ver')


# 4. Eliminar Elemento Individual
def cotizacion_eliminar(request, id):
    cotizacion = _obtener_cotizacion(request)
    str_id = str(id)
    if str_id in cotizacion:
        del cotizacion[str_id]
        request.session.modified = True
        messages.warning(request, "Equipo eliminado del presupuesto.")
    return redirect('cotizaciones:ver')


# 5. Vaciar Sesión
def cotizacion_limpiar(request):
    if 'cotizacion' in request.session:
        del request.session['cotizacion']
        request.session.modified = True
    return redirect('cotizaciones:ver')


# 6. Vista de Resumen de Solicitud (Checkout Simulado)
@login_required
def comprobante_simulado(request):
    cotizacion = _obtener_cotizacion(request)
    if not cotizacion:
        return redirect('inventario:lista')

    subtotal_arriendo = sum(item['subtotal'] for item in cotizacion.values())
    total_garantia = sum(item['garantia'] * item['cantidad'] for item in cotizacion.values())
    iva = int(subtotal_arriendo * 0.19)
    total_final = subtotal_arriendo + iva + total_garantia
    items_cotizados = list(cotizacion.values())

    # Vaciar la sesión tras generar el comprobante
    del request.session['cotizacion']
    request.session.modified = True

    return render(request, 'cotizaciones/comprobante_exito.html', {
        'items': items_cotizados,
        'subtotal': subtotal_arriendo,
        'garantia': total_garantia,
        'iva': iva,
        'total': total_final,
        'codigo_cotizacion': f"COT-TR-{request.user.id}-2026",
    })