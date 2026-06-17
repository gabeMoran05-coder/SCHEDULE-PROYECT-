from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("escuela", "0003_materia_horas_semanales"),
    ]

    operations = [
        migrations.AddField(
            model_name="grupo",
            name="activo",
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name="materia",
            name="activo",
            field=models.BooleanField(default=True),
        ),
    ]
