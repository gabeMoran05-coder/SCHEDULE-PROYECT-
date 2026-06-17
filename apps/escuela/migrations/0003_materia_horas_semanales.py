from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("escuela", "0002_scope_materias_by_institution"),
    ]

    operations = [
        migrations.AddField(
            model_name="materia",
            name="horas_semanales",
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
