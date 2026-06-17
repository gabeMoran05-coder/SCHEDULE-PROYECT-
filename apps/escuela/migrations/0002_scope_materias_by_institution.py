from django.db import migrations, models
import django.db.models.deletion


def assign_existing_materias(apps, schema_editor):
    Institucion = apps.get_model("escuela", "Institucion")
    Materia = apps.get_model("escuela", "Materia")
    institucion = Institucion.objects.order_by("id").first()
    if institucion:
        Materia.objects.filter(institucion__isnull=True).update(institucion=institucion)


class Migration(migrations.Migration):
    dependencies = [
        ("escuela", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="materia",
            name="institucion",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="materias", to="escuela.institucion"),
        ),
        migrations.RunPython(assign_existing_materias, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="materia",
            name="clave",
            field=models.CharField(max_length=20),
        ),
        migrations.AlterUniqueTogether(
            name="materia",
            unique_together={("institucion", "clave")},
        ),
    ]
