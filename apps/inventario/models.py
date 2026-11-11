from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify


class CategoriaEquipo(models.Model):
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre de Categoría")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="¿Categoría Activa?")

    class Meta:
        verbose_name = "Categoría de Equipo"
        verbose_name_plural = "Categorías de Equipos"
        ordering = ['nombre']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.nombre


class EquipoInformatico(models.Model):
    ESTADO_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('NO_DISPONIBLE', 'No disponible'),
    ]

    codigo_sku = models.CharField(max_length=50, unique=True, verbose_name="Código SKU")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Equipo")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    categoria = models.ForeignKey(CategoriaEquipo, on_delete=models.PROTECT, related_name="equipos", verbose_name="Categoría")
    especificaciones = models.TextField(verbose_name="Especificaciones Técnicas")
    
    tarifa_diaria = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        validators=[MinValueValidator(0)],
        verbose_name="Tarifa Diaria Arriendo (CLP)"
    )
    precio_venta = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        validators=[MinValueValidator(0)], 
        default=0,
        verbose_name="Precio de Venta Directa (CLP)"
    )
    monto_garantia = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        validators=[MinValueValidator(0)],
        verbose_name="Monto de Garantía Reembolsable (CLP)"
    )
    stock = models.PositiveIntegerField(default=1, verbose_name="Stock Disponible")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='DISPONIBLE', verbose_name="Estado")
    imagen = models.ImageField(upload_to='equipos/', blank=True, null=True, verbose_name="Fotografía")
    destacado = models.BooleanField(default=False, verbose_name="Destacar en portada")
    activo = models.BooleanField(default=True, verbose_name="Activo en catálogo")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Equipo Informático"
        verbose_name_plural = "Equipos Informáticos"
        ordering = ['-fecha_creacion']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.codigo_sku}-{self.nombre}")

        if self.estado == 'NO_DISPONIBLE' or self.stock == 0:
            self.estado = 'NO_DISPONIBLE'
            self.stock = 0

        update_fields = kwargs.get('update_fields')
        if update_fields is not None:
            kwargs['update_fields'] = set(update_fields) | {'estado', 'stock'}

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.nombre} ({self.codigo_sku})"

    # --- MÉTODOS DE FORMATO CON PUNTOS DE MILES ---
    @property
    def precio_formateado(self):
        """Devuelve la tarifa diaria formateada con puntos: $25.000"""
        return f"${int(self.tarifa_diaria):,}".replace(",", ".")

    @property
    def precio_venta_formateado(self):
        """Devuelve el precio de venta formateado con puntos: $399.000"""
        return f"${int(self.precio_venta):,}".replace(",", ".")

    @property
    def garantia_formateada(self):
        """Devuelve la garantía formateada con puntos: $50.000"""
        return f"${int(self.monto_garantia):,}".replace(",", ".")