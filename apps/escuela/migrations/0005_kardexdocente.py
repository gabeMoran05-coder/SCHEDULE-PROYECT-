import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("escuela", "0004_grupo_materia_activo"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="KardexDocente",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha", models.DateTimeField(auto_now_add=True)),
                (
                    "tipo",
                    models.CharField(
                        choices=[
                            ("ALTA", "Alta"),
                            ("CAMBIO_ESCUELA", "Cambio de escuela"),
                            ("ASIGNACION", "Asignacion"),
                            ("RETIRO", "Retiro"),
                            ("BAJA", "Baja"),
                            ("RESTAURACION", "Restauracion"),
                            ("AJUSTE", "Ajuste"),
                        ],
                        max_length=24,
                    ),
                ),
                ("referencia", models.CharField(blank=True, max_length=160)),
                ("descripcion", models.TextField(blank=True)),
                ("horas_antes", models.PositiveSmallIntegerField(default=0)),
                ("horas_despues", models.PositiveSmallIntegerField(default=0)),
                ("horas_movimiento", models.IntegerField(default=0)),
                (
                    "contrato",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="kardex",
                        to="escuela.contratodocente",
                    ),
                ),
                (
                    "docente",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="kardex",
                        to="escuela.docente",
                    ),
                ),
                (
                    "responsable",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={
                "verbose_name": "Kardex docente",
                "verbose_name_plural": "Kardex docentes",
                "ordering": ["-fecha"],
            },
        ),
    ]
