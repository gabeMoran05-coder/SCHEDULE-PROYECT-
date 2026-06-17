from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("horarios", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="HorarioGrupoGuardado",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("actualizado_en", models.DateTimeField(auto_now=True)),
                (
                    "grupo",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="estado_horario",
                        to="escuela.grupo",
                    ),
                ),
            ],
            options={
                "verbose_name": "Estado de guardado de horario",
                "verbose_name_plural": "Estados de guardado de horarios",
            },
        ),
    ]
