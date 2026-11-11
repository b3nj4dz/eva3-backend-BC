from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.cotizaciones.models import ItemCotizacion, SolicitudCotizacion


class PerfilUsuarioTests(TestCase):
    def test_historial_muestra_dias_solo_para_arriendos(self):
        usuario = User.objects.create_user(username="cliente")
        solicitud = SolicitudCotizacion.objects.create(
            codigo="COT-TEST",
            usuario=usuario,
            subtotal=100,
            garantia=0,
            iva=19,
            total=119,
        )
        ItemCotizacion.objects.create(
            solicitud=solicitud,
            nombre_equipo="Servidor (Arriendo)",
            codigo_sku="RENT-1",
            dias=3,
            cantidad=1,
            subtotal_item=100,
        )
        ItemCotizacion.objects.create(
            solicitud=solicitud,
            nombre_equipo="Servidor (Venta)",
            codigo_sku="SALE-1",
            dias=1,
            cantidad=1,
            subtotal_item=100,
        )
        self.client.force_login(usuario)

        response = self.client.get(reverse("usuarios:perfil"))

        self.assertContains(response, "SKU: RENT-1 | 1 un. | 3 día(s)")
        self.assertContains(response, "SKU: SALE-1 | 1 un.")
        self.assertNotContains(response, "SKU: SALE-1 | 1 un. | 1 día(s)")
