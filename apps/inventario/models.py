from django.db import models
from django.utils.text import slugify
from django.core.validators import MinValueValidator


class CategoriaEquipo(models.Model):
    """Entidad de Contexto / Agrupación (ej: Laptops, Servidores, Componentes PC)"""
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Categoría o Gama")
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    activo = models.BooleanField(default=True, verbose_name="¿Categoría Activa?")

    class Meta:
        verbose_name = "Categoría de Equipo"
        verbose_name_plural = "Categorías de Equipos"
        ordering = ['nombre']

    def __str__(self):
        return self.nombre

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)


class EquipoInformatico(models.Model):
    """Entidad Principal Gestionable"""
    ESTADO_CHOICES = [
        ('DISPONIBLE', 'Disponible'),
        ('EN_ARRIENDO', 'En Arriendo / Cotizado'),
        ('MANTENCION', 'En Mantenimiento'),
        
    ]

    codigo_sku = models.CharField(max_length=50, unique=True, verbose_name="Código SKU / Identificador")
    nombre = models.CharField(max_length=200, verbose_name="Nombre del Equipo / Componente")
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    categoria = models.ForeignKey(CategoriaEquipo, on_delete=models.PROTECT, related_name="equipos", verbose_name="Categoría")
    especificaciones = models.TextField(verbose_name="Especificaciones Técnicas (CPU, GPU, RAM, etc.)")
    
    tarifa_diaria = models.DecimalField(
        max_digits=10, 
        decimal_places=0, 
        validators=[MinValueValidator(0)], 
        verbose_name="Tarifa de Arriendo Diaria (CLP)"
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
        verbose_name="Garantía / Ensamble (CLP)"
    )
    stock = models.PositiveIntegerField(default=1, verbose_name="Stock Disponible")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='DISPONIBLE', verbose_name="Estado Operativo")
    imagen = models.ImageField(upload_to="equipos/", blank=True, null=True, verbose_name="Fotografía del Equipo")
    destacado = models.BooleanField(default=False, verbose_name="¿Destacado en Portada?")
    activo = models.BooleanField(default=True, verbose_name="¿Vigente / Activo?")
    
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Equipo Informático"
        verbose_name_plural = "Equipos Informáticos"
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"[{self.codigo_sku}] {self.nombre}"

    @property
    def precio_formateado(self):
        return f"${self.tarifa_diaria:,.0f}".replace(",", ".")

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.codigo_sku}-{self.nombre}")
            self.slug = base_slug
        super().save(*args, **kwargs)
