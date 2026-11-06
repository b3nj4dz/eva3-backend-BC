def cotizacion_context(request):
    """Inyecta el contador de equipos en cotización en todas las plantillas"""
    cotizacion = request.session.get('cotizacion', {})
    total_items = sum(item.get('cantidad', 0) for item in cotizacion.values())
    return {
        'cotizacion_total_items': total_items
    }