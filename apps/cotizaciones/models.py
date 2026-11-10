from django.db import models
from django.contrib.auth.models import User


class SolicitudCotizacion(models.Model):
    codigo = models.CharField(max_length=100, unique=True, verbose_name="Código de Cotización")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cotizaciones")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=12, decimal_places=0)
    garantia = models.DecimalField(max_digits=12, decimal_places=0)
    iva = models.DecimalField(max_digits=12, decimal_places=0)
    total = models.DecimalField(max_digits=12, decimal_places=0)

    class Meta:
        verbose_name = "Solicitud de Cotización"
        verbose_name_plural = "Solicitudes de Cotización"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.codigo} - {self.usuario.username}"

    # --- FORMATOS CON PUNTO DE MILES ---
    @property
    def total_fmt(self):
        return f"{int(self.total):,}".replace(",", ".")

    @property
    def subtotal_fmt(self):
        return f"{int(self.subtotal):,}".replace(",", ".")

    @property
    def iva_fmt(self):
        return f"{int(self.iva):,}".replace(",", ".")

    @property
    def garantia_fmt(self):
        return f"{int(self.garantia):,}".replace(",", ".")


class ItemCotizacion(models.Model):
    solicitud = models.ForeignKey(SolicitudCotizacion, on_delete=models.CASCADE, related_name="items")
    nombre_equipo = models.CharField(max_length=200)
    codigo_sku = models.CharField(max_length=50)
    dias = models.PositiveIntegerField(default=1)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal_item = models.DecimalField(max_digits=12, decimal_places=0)

    class Meta:
        verbose_name = "Ítem de Cotización"
        verbose_name_plural = "Ítems de Cotización"

    def __str__(self):
        return f"{self.nombre_equipo} (x{self.cantidad})"

    @property
    def subtotal_item_fmt(self):
        return f"{int(self.subtotal_item):,}".replace(",", ".")