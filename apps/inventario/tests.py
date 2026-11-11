from django.test import TestCase
from django.urls import reverse

from .forms import EquipoInformaticoForm
from .models import CategoriaEquipo, EquipoInformatico


class EstadoEquipoTests(TestCase):
    def setUp(self):
        categoria = CategoriaEquipo.objects.create(nombre="Computadores")
        self.equipo = EquipoInformatico.objects.create(
            codigo_sku="PC-TEST",
            nombre="PC de prueba",
            categoria=categoria,
            especificaciones="Equipo de prueba",
            tarifa_diaria=1000,
            precio_venta=100000,
            monto_garantia=5000,
            stock=1,
            estado="NO_DISPONIBLE",
        )

    def test_formulario_ofrece_solo_disponible_y_no_disponible(self):
        choices = list(EquipoInformaticoForm().fields["estado"].choices)

        self.assertEqual(
            choices,
            [("DISPONIBLE", "Disponible"), ("NO_DISPONIBLE", "No disponible")],
        )

    def test_ficha_muestra_estado_no_disponible(self):
        response = self.client.get(
            reverse("inventario:detalle", args=[self.equipo.slug])
        )

        self.assertContains(response, "Estado: No disponible")
        self.assertContains(response, "Stock: 0 un.")
        self.assertContains(response, "Este equipo no está disponible")
        self.assertNotContains(response, "Comprar Equipo Directo")
        self.assertNotContains(response, "Cotizar Arriendo por Días")

    def test_equipo_no_disponible_guarda_stock_cero(self):
        self.equipo.refresh_from_db()

        self.assertEqual(self.equipo.stock, 0)

    def test_stock_cero_actualiza_estado_a_no_disponible(self):
        self.equipo.estado = "DISPONIBLE"
        self.equipo.stock = 0
        self.equipo.save()

        self.assertEqual(self.equipo.estado, "NO_DISPONIBLE")

    def test_catalogo_muestra_no_disponible_en_vez_de_stock_cero(self):
        response = self.client.get(reverse("inventario:lista"))

        self.assertContains(response, "No disponible")
        self.assertNotContains(response, "Stock: 0 un.")
