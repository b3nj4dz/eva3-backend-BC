from django.db import migrations


def normalizar_disponibilidad(apps, schema_editor):
    EquipoInformatico = apps.get_model("inventario", "EquipoInformatico")
    equipos = EquipoInformatico.objects.using(schema_editor.connection.alias)
    equipos.filter(estado="NO_DISPONIBLE").update(stock=0)
    equipos.filter(stock=0).update(estado="NO_DISPONIBLE")


class Migration(migrations.Migration):

    dependencies = [
        ("inventario", "0004_simplificar_estado_equipo"),
    ]

    operations = [
        migrations.RunPython(normalizar_disponibilidad, migrations.RunPython.noop),
    ]
