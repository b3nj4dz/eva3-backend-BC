from django.db import migrations, models


ESTADOS_NO_DISPONIBLES = ("EN_ARRIENDO", "MANTENCION", "RESERVADO")


def migrar_estados(apps, schema_editor):
    EquipoInformatico = apps.get_model("inventario", "EquipoInformatico")
    EquipoInformatico.objects.using(schema_editor.connection.alias).filter(
        estado__in=ESTADOS_NO_DISPONIBLES,
    ).update(estado="NO_DISPONIBLE")


class Migration(migrations.Migration):

    dependencies = [
        ("inventario", "0003_actualizar_precios_catalogo"),
    ]

    operations = [
        migrations.RunPython(migrar_estados, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="equipoinformatico",
            name="estado",
            field=models.CharField(
                choices=[
                    ("DISPONIBLE", "Disponible"),
                    ("NO_DISPONIBLE", "No disponible"),
                ],
                default="DISPONIBLE",
                max_length=20,
                verbose_name="Estado",
            ),
        ),
    ]
