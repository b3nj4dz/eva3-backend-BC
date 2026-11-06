from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.inventario.models import CategoriaEquipo, EquipoInformatico


class Command(BaseCommand):
    help = "Pobla la base de datos con categorías, equipos informáticos y usuarios de prueba."

    def handle(self, *args, **kwargs):
        # 1. Crear Usuario Administrador de Prueba
        if not User.objects.filter(username="admin_test").exists():
            admin_user = User.objects.create_superuser("admin_test", "admin@techrental.cl", "admin123")
            admin_user.is_staff = True
            admin_user.save()
            self.stdout.write(self.style.SUCCESS("✓ Superusuario de prueba 'admin_test' (clave: admin123) creado."))

        # 2. Crear Usuario Estándar de Prueba
        if not User.objects.filter(username="cliente_test").exists():
            User.objects.create_user("cliente_test", "cliente@techrental.cl", "cliente123")
            self.stdout.write(self.style.SUCCESS("✓ Usuario estándar 'cliente_test' (clave: cliente123) creado."))

        # 3. Crear 4 Categorías (Entidad de Contexto)
        categorias_data = [
            ("Laptops Portátiles", "Notebooks de alto rendimiento y trabajo en terreno."),
            ("Workstations de Desarrollo", "Estaciones de trabajo pesadas para compilación y renders 3D."),
            ("Servidores y Networking", "Infraestructura rack y torre para centros de datos."),
            ("Componentes de Armado", "Piezas sueltas (GPU, RAM, CPU) para ensamble a medida."),
        ]

        cat_map = {}
        for nombre, desc in categorias_data:
            cat, _ = CategoriaEquipo.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
            cat_map[nombre] = cat

        # 4. Crear 8 Equipos Informáticos Coherentes (Entidad Principal)
        equipos_data = [
            (
                "LAP-I7-16GB",
                "Laptop Asus TUF Core i7 16GB RAM",
                cat_map["Laptops Portátiles"],
                "CPU Intel Core i7, 16GB RAM DDR4, SSD 512GB NVMe, Pantalla 15.6 FHD 144Hz.",
                25000, 50000, 5, "DISPONIBLE", True
            ),
            (
                "LAP-R7-32GB",
                "Laptop Lenovo Legion Ryzen 7 RTX 4060",
                cat_map["Laptops Portátiles"],
                "CPU AMD Ryzen 7, 32GB RAM DDR5, GPU NVIDIA RTX 4060 8GB, SSD 1TB.",
                35000, 70000, 3, "DISPONIBLE", True
            ),
            (
                "WORK-R9-64GB",
                "Workstation Ryzen 9 / RTX 4080 64GB RAM",
                cat_map["Workstations de Desarrollo"],
                "CPU AMD Ryzen 9 7900X, 64GB RAM DDR5, GPU RTX 4080 16GB, Liquid Cooling 360mm.",
                65000, 120000, 2, "DISPONIBLE", True
            ),
            (
                "WORK-I9-128GB",
                "Workstation Intel i9 Extreme Dev Rig",
                cat_map["Workstations de Desarrollo"],
                "CPU Intel Core i9 14900K, 128GB RAM DDR5, GPU RTX 4090 24GB, Dual SSD 2TB NVMe.",
                85000, 150000, 1, "DISPONIBLE", True
            ),
            (
                "SERV-XEON-RACK",
                "Servidor Dell PowerEdge Rack 32 Cores",
                cat_map["Servidores y Networking"],
                "Dual Intel Xeon Silver 32 Cores Total, 128GB RAM ECC, 4x 2TB SAS Hot-Swap RAID 10.",
                110000, 200000, 2, "DISPONIBLE", True
            ),
            (
                "SERV-TORRE-64GB",
                "Servidor Torre HP ProLiant MicroServer",
                cat_map["Servidores y Networking"],
                "Intel Xeon E-2300, 64GB RAM ECC, 4x 4TB SATA Enterprise, Fuente Redundante.",
                45000, 90000, 4, "DISPONIBLE", False
            ),
            (
                "GPU-RTX-4070",
                "Tarjeta de Video NVIDIA RTX 4070 12GB",
                cat_map["Componentes de Armado"],
                "GPU NVIDIA GeForce RTX 4070 12GB GDDR6X, PCIe 4.0, Ray Tracing & DLSS 3.",
                18000, 40000, 6, "DISPONIBLE", False
            ),
            (
                "RAM-KIT-64GB",
                "Kit Memoria RAM 64GB (2x32GB) DDR5 6000MHz",
                cat_map["Componentes de Armado"],
                "Kit Dual Channel Corsair Vengeance DDR5 6000MHz CL36 RGB.",
                10000, 20000, 8, "DISPONIBLE", False
            ),
        ]

        for sku, nom, cat, espec, tarifa, garan, stk, est, dest in equipos_data:
            EquipoInformatico.objects.get_or_create(
                codigo_sku=sku,
                defaults={
                    'nombre': nom,
                    'categoria': cat,
                    'especificaciones': espec,
                    'tarifa_diaria': tarifa,
                    'monto_garantia': garan,
                    'stock': stk,
                    'estado': est,
                    'destacado': dest,
                    'activo': True
                }
            )

        self.stdout.write(self.style.SUCCESS("✓ Catálogo de flota informatica poblado exitosamente (4 categorías, 8 equipos y 2 usuarios)."))