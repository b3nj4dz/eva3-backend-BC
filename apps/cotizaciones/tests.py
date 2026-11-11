from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from apps.inventario.models import CategoriaEquipo, EquipoInformatico
from .models import ItemCotizacion, SolicitudCotizacion


class ConfirmarCotizacionStockTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(username="cliente")
        categoria = CategoriaEquipo.objects.create(nombre="Servidores")
        self.equipo = EquipoInformatico.objects.create(
            codigo_sku="SRV-1",
            nombre="Servidor",
            categoria=categoria,
            especificaciones="Servidor de prueba",
            tarifa_diaria=100,
            precio_venta=500,
            monto_garantia=50,
            stock=5,
        )
        self.client.force_login(self.usuario)

    def _crear_item_carrito(self, modalidad, cantidad=1):
        return {
            "id_key": f"{self.equipo.id}_{modalidad}",
            "equipo_id": self.equipo.id,
            "sku": self.equipo.codigo_sku,
            "nombre": self.equipo.nombre,
            "modalidad": modalidad,
            "tarifa_diaria": 100 if modalidad == "arriendo" else 500,
            "garantia": 50 if modalidad == "arriendo" else 0,
            "cantidad": cantidad,
            "dias": 1,
            "subtotal": (100 if modalidad == "arriendo" else 500) * cantidad,
        }

    def test_confirmar_descuenta_stock_de_arriendo_y_venta(self):
        session = self.client.session
        session["cotizacion"] = {
            f"{self.equipo.id}_arriendo": self._crear_item_carrito("arriendo"),
            f"{self.equipo.id}_venta": self._crear_item_carrito("venta"),
        }
        session.save()

        response = self.client.post(reverse("cotizaciones:guardar"))

        self.assertEqual(response.status_code, 200)
        self.equipo.refresh_from_db()
        self.assertEqual(self.equipo.stock, 3)
        self.assertEqual(SolicitudCotizacion.objects.count(), 1)
        self.assertEqual(ItemCotizacion.objects.count(), 2)
        self.assertNotIn("cotizacion", self.client.session)
        self.assertEqual(response.context["total_sin_deposito_fmt"], "714")
        self.assertEqual(response.context["total_fmt"], "764")
        self.assertContains(response, "Pago inicial estimado:")
        self.assertContains(response, "Se devuelve al entregar el equipo en buen estado.")

    def test_carrito_separa_costo_del_deposito_reembolsable(self):
        session = self.client.session
        session["cotizacion"] = {
            f"{self.equipo.id}_arriendo": self._crear_item_carrito("arriendo"),
        }
        session.save()

        response = self.client.get(reverse("cotizaciones:ver"))

        self.assertEqual(response.context["total_sin_deposito_fmt"], "119")
        self.assertEqual(response.context["total_final_fmt"], "169")
        self.assertContains(response, "Depósito en garantía (reembolsable)")
        self.assertContains(response, "Se devuelve al entregar el equipo en buen estado.")
        self.assertContains(response, "Pago inicial estimado:")

    def test_stock_insuficiente_no_guarda_solicitud_ni_descuenta_parcialmente(self):
        self.equipo.stock = 1
        self.equipo.save(update_fields=["stock"])
        session = self.client.session
        session["cotizacion"] = {
            f"{self.equipo.id}_arriendo": self._crear_item_carrito("arriendo"),
            f"{self.equipo.id}_venta": self._crear_item_carrito("venta"),
        }
        session.save()

        response = self.client.post(reverse("cotizaciones:guardar"))

        self.assertRedirects(response, reverse("cotizaciones:ver"))
        self.equipo.refresh_from_db()
        self.assertEqual(self.equipo.stock, 1)
        self.assertEqual(SolicitudCotizacion.objects.count(), 0)
        self.assertEqual(ItemCotizacion.objects.count(), 0)
        self.assertIn("cotizacion", self.client.session)

    def test_carrito_comparte_stock_entre_arriendo_y_venta(self):
        self.equipo.stock = 1
        self.equipo.save(update_fields=["stock"])
        session = self.client.session
        session["cotizacion"] = {
            f"{self.equipo.id}_arriendo": self._crear_item_carrito("arriendo"),
        }
        session.save()

        response = self.client.get(
            reverse("cotizaciones:agregar", args=[self.equipo.id]),
            {"modalidad": "venta"},
        )

        self.assertRedirects(response, reverse("cotizaciones:ver"))
        self.assertNotIn(f"{self.equipo.id}_venta", self.client.session["cotizacion"])

    def test_agrega_unidad_a_venta_y_actualiza_subtotal(self):
        session = self.client.session
        session["cotizacion"] = {
            f"{self.equipo.id}_venta": self._crear_item_carrito("venta"),
        }
        session.save()

        response = self.client.get(
            reverse(
                "cotizaciones:modificar_cantidad",
                args=[f"{self.equipo.id}_venta", "sumar_unidad"],
            )
        )

        self.assertRedirects(response, reverse("cotizaciones:ver"))
        item = self.client.session["cotizacion"][f"{self.equipo.id}_venta"]
        self.assertEqual(item["cantidad"], 2)
        self.assertEqual(item["subtotal"], 1000)

    def test_quita_unidad_de_arriendo_y_actualiza_subtotal(self):
        item = self._crear_item_carrito("arriendo", cantidad=2)
        item["dias"] = 3
        item["subtotal"] = 600
        session = self.client.session
        session["cotizacion"] = {f"{self.equipo.id}_arriendo": item}
        session.save()

        response = self.client.get(
            reverse(
                "cotizaciones:modificar_cantidad",
                args=[f"{self.equipo.id}_arriendo", "restar_unidad"],
            )
        )

        self.assertRedirects(response, reverse("cotizaciones:ver"))
        item = self.client.session["cotizacion"][f"{self.equipo.id}_arriendo"]
        self.assertEqual(item["cantidad"], 1)
        self.assertEqual(item["dias"], 3)
        self.assertEqual(item["subtotal"], 300)

    def test_no_agrega_unidad_si_supera_stock_compartido(self):
        self.equipo.stock = 1
        self.equipo.save(update_fields=["stock"])
        session = self.client.session
        session["cotizacion"] = {
            f"{self.equipo.id}_arriendo": self._crear_item_carrito("arriendo"),
        }
        session.save()

        response = self.client.get(
            reverse(
                "cotizaciones:modificar_cantidad",
                args=[f"{self.equipo.id}_arriendo", "sumar_unidad"],
            )
        )

        self.assertRedirects(response, reverse("cotizaciones:ver"))
        item = self.client.session["cotizacion"][f"{self.equipo.id}_arriendo"]
        self.assertEqual(item["cantidad"], 1)

    def test_no_agrega_equipo_no_disponible_al_carrito(self):
        self.equipo.estado = "NO_DISPONIBLE"
        self.equipo.save()

        response = self.client.get(
            reverse("cotizaciones:agregar", args=[self.equipo.id]),
            {"modalidad": "venta"},
        )

        self.assertRedirects(response, reverse("cotizaciones:ver"))
        self.assertFalse(self.client.session.get("cotizacion"))

    def test_stock_agotado_deja_equipo_no_disponible(self):
        self.equipo.stock = 2
        self.equipo.save()
        session = self.client.session
        session["cotizacion"] = {
            f"{self.equipo.id}_arriendo": self._crear_item_carrito("arriendo"),
            f"{self.equipo.id}_venta": self._crear_item_carrito("venta"),
        }
        session.save()

        response = self.client.post(reverse("cotizaciones:guardar"))

        self.assertEqual(response.status_code, 200)
        self.equipo.refresh_from_db()
        self.assertEqual(self.equipo.stock, 0)
        self.assertEqual(self.equipo.estado, "NO_DISPONIBLE")

    def test_no_confirma_carrito_si_equipo_ya_no_esta_disponible(self):
        session = self.client.session
        session["cotizacion"] = {
            f"{self.equipo.id}_venta": self._crear_item_carrito("venta"),
        }
        session.save()
        self.equipo.estado = "NO_DISPONIBLE"
        self.equipo.save()

        response = self.client.post(reverse("cotizaciones:guardar"))

        self.assertRedirects(response, reverse("cotizaciones:ver"))
        self.assertEqual(SolicitudCotizacion.objects.count(), 0)
        self.assertIn("cotizacion", self.client.session)
