from django.db import models
from django.contrib.auth.models import User


class SolicitudCotizacion(models.Model):
    codigo = models.CharField(max_length=50, unique=True, verbose_name="Código de Cotización")
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name="cotizaciones", verbose_name="Usuario")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Emisión")
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Subtotal (CLP)")
    garantia = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Garantía (CLP)")
    iva = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="IVA 19% (CLP)")
    total = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="Total (CLP)")

    class Meta:
        verbose_name = "Solicitud de Cotización"
        verbose_name_plural = "Solicitudes de Cotizaciones"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"{self.codigo} - {self.usuario.username}"


class ItemCotizacion(models.Model):
    solicitud = models.ForeignKey(SolicitudCotizacion, on_delete=models.CASCADE, related_name="items")
    nombre_equipo = models.CharField(max_length=200)
    codigo_sku = models.CharField(max_length=50)
    dias = models.PositiveIntegerField(default=1)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal_item = models.DecimalField(max_digits=12, decimal_places=0)

    def __str__(self):
        return f"{self.cantidad}x {self.nombre_equipo} ({self.dias}d)"