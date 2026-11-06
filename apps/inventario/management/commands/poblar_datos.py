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
            self.stdout.write(self.style.SUCCESS("✓ Superusuario 'admin_test' creado."))

        # 2. Crear Usuario Estándar de Prueba (Cliente Particular/Empresa)
        if not User.objects.filter(username="cliente_test").exists():
            User.objects.create_user("cliente_test", "cliente@techrental.cl", "cliente123")
            self.stdout.write(self.style.SUCCESS("✓ Usuario estándar 'cliente_test' creado."))

        # 3. Crear Categorías Adaptadas a Todo Público
        categorias_data = [
            ("Laptops y Notebooks", "Notebooks para estudiantes, teletrabajo y uso diario o profesional."),
            ("PCs Gamer y Computadores Ensamblados", "Equipos armados a medida para juegos, streaming y edición de video."),
            ("Workstations y Alto Rendimiento", "Estaciones de trabajo de gran potencia para diseño 3D, programación y arquitectura."),
            ("Servidores y Equipamiento TI", "Infraestructura en torre y rack para proyectos de desarrollo y empresas."),
        ]

        cat_map = {}
        for nombre, desc in categorias_data:
            cat, _ = CategoriaEquipo.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
            cat_map[nombre] = cat

        # 4. Crear Equipos (Uso Particular y Profesional)
        equipos_data = [
            (
                "LAP-I7-16GB",
                "Laptop Asus TUF Core i7 16GB RAM",
                cat_map["Laptops y Notebooks"],
                "Ideal para estudio o trabajo: CPU Intel Core i7, 16GB RAM DDR4, SSD 512GB NVMe, Pantalla 15.6 144Hz.",
                25000, 50000, 5, "DISPONIBLE", True
            ),
            (
                "BUILD-GAMER-RTX",
                "PC Custom Gamer: Ryzen 7 + RTX 4070",
                cat_map["PCs Gamer y Computadores Ensamblados"],
                "PC Armado a Medida: Excelente para jugar en 1440p o hacer streaming. Ryzen 7 7800X3D, 32GB RAM DDR5, RTX 4070 12GB, SSD 1TB NVMe.",
                40000, 80000, 4, "DISPONIBLE", True
            ),
            (
                "LAP-R7-32GB",
                "Laptop Lenovo Legion Ryzen 7 RTX 4060",
                cat_map["Laptops y Notebooks"],
                "Para diseño, edición y juegos pesados: AMD Ryzen 7, 32GB RAM DDR5, GPU NVIDIA RTX 4060 8GB, SSD 1TB.",
                35000, 70000, 3, "DISPONIBLE", True
            ),
            (
                "BUILD-EDIT-3D",
                "PC Custom Render & Edición i9 + 64GB",
                cat_map["PCs Gamer y Computadores Ensamblados"],
                "PC Armado a Pedido: Pensado para creadores de contenido y renders. Intel i9 14900K, 64GB DDR5, RTX 4080 16GB, SSD 2TB.",
                55000, 100000, 2, "DISPONIBLE", True
            ),
            (
                "WORK-R9-64GB",
                "Workstation Ryzen 9 / RTX 4080",
                cat_map["Workstations y Alto Rendimiento"],
                "Para desarrollo pesado y simulación: AMD Ryzen 9 7900X, 64GB RAM DDR5, GPU RTX 4080 16GB, Liquid Cooling.",
                65000, 120000, 2, "DISPONIBLE", True
            ),
            (
                "BUILD-STARTER-PC",
                "PC Custom Home & Office Ryzen 5",
                cat_map["PCs Gamer y Computadores Ensamblados"],
                "PC de entrada armado para multitarea y estudio: AMD Ryzen 5 5600G con Vega Graphics, 16GB RAM, SSD 512GB.",
                15000, 30000, 6, "DISPONIBLE", False
            ),
            (
                "SERV-XEON-RACK",
                "Servidor Dell PowerEdge Rack 32 Cores",
                cat_map["Servidores y Equipamiento TI"],
                "Para entornos de pruebas, proyectos universitarios o servidores de datos: Dual Xeon 32 Cores, 128GB RAM ECC, 4x 2TB SAS.",
                110000, 200000, 2, "DISPONIBLE", True
            ),
            (
                "WORK-I9-128GB",
                "Workstation Intel i9 Extreme Rig",
                cat_map["Workstations y Alto Rendimiento"],
                "Máxima potencia: Intel i9 14900K, 128GB RAM DDR5, GPU RTX 4090 24GB, Dual SSD 2TB NVMe.",
                85000, 150000, 1, "DISPONIBLE", False
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

        self.stdout.write(self.style.SUCCESS("✓ Base de datos poblada para usuarios particulares y empresas."))