from django.db import migrations


PRECIOS_POR_SKU = {
    "LAP-I7-16GB": (28000, 1099990),
    "BUILD-GAMER-RTX": (45000, 2699990),
    "LAP-R7-32GB": (40000, 1899990),
    "BUILD-EDIT-3D": (70000, 3899990),
    "WORK-R9-64GB": (65000, 3699990),
    "BUILD-STARTER-PC": (14000, 599990),
    "SERV-XEON-RACK": (65000, 1499990),
    "WORK-I9-128GB": (95000, 5499990),
}


def actualizar_precios(apps, schema_editor):
    EquipoInformatico = apps.get_model("inventario", "EquipoInformatico")
    for codigo_sku, (tarifa_diaria, precio_venta) in PRECIOS_POR_SKU.items():
        EquipoInformatico.objects.using(schema_editor.connection.alias).filter(
            codigo_sku=codigo_sku,
        ).update(
            tarifa_diaria=tarifa_diaria,
            precio_venta=precio_venta,
        )


class Migration(migrations.Migration):

    dependencies = [
        ("inventario", "0002_equipoinformatico_precio_venta"),
    ]

    operations = [
        migrations.RunPython(actualizar_precios, migrations.RunPython.noop),
    ]
