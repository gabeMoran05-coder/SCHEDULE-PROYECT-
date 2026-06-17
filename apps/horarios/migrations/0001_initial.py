from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("escuela", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="BloqueHorario",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("hora_inicio", models.TimeField()),
                ("hora_fin", models.TimeField()),
                ("orden", models.PositiveSmallIntegerField()),
                ("es_receso", models.BooleanField(default=False)),
                ("ciclo", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="bloques_horario", to="escuela.cicloescolar")),
            ],
            options={
                "verbose_name": "Bloque horario",
                "verbose_name_plural": "Bloques horario",
                "ordering": ["ciclo", "orden"],
                "unique_together": {("ciclo", "orden")},
            },
        ),
        migrations.CreateModel(
            name="FichaAsignacion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("aula", models.CharField(blank=True, max_length=30)),
                ("horas_por_colocar", models.PositiveSmallIntegerField(default=1)),
                ("color", models.CharField(default="#0f766e", max_length=7)),
                ("notas", models.CharField(blank=True, max_length=180)),
                ("asignacion", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="fichas", to="escuela.asignaciondocentemateria")),
                ("grupo", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="fichas_horario", to="escuela.grupo")),
            ],
            options={
                "verbose_name": "Ficha de asignacion",
                "verbose_name_plural": "Fichas de asignacion",
                "ordering": ["asignacion__contrato__docente__apellidos", "grupo__grado", "grupo__letra"],
            },
        ),
        migrations.CreateModel(
            name="DisponibilidadDocente",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("dia", models.CharField(choices=[("LUNES", "Lunes"), ("MARTES", "Martes"), ("MIERCOLES", "Miercoles"), ("JUEVES", "Jueves"), ("VIERNES", "Viernes")], max_length=12)),
                ("disponible", models.BooleanField(default=True)),
                ("observaciones", models.CharField(blank=True, max_length=160)),
                ("bloque", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="horarios.bloquehorario")),
                ("contrato", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="disponibilidades", to="escuela.contratodocente")),
            ],
            options={
                "verbose_name": "Disponibilidad docente",
                "verbose_name_plural": "Disponibilidades docentes",
                "ordering": ["contrato", "dia", "bloque__orden"],
                "unique_together": {("contrato", "dia", "bloque")},
            },
        ),
        migrations.CreateModel(
            name="HorarioClase",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("dia", models.CharField(choices=[("LUNES", "Lunes"), ("MARTES", "Martes"), ("MIERCOLES", "Miercoles"), ("JUEVES", "Jueves"), ("VIERNES", "Viernes")], max_length=12)),
                ("aula", models.CharField(blank=True, max_length=30)),
                ("bloque", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to="horarios.bloquehorario")),
                ("ciclo", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="horarios", to="escuela.cicloescolar")),
                ("contrato", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="horarios", to="escuela.contratodocente")),
                ("ficha", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="clases_colocadas", to="horarios.fichaasignacion")),
                ("grupo", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="escuela.grupo")),
                ("materia", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="escuela.materia")),
                ("periodo", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="horarios", to="escuela.periodo")),
            ],
            options={
                "verbose_name": "Clase en horario",
                "verbose_name_plural": "Clases en horario",
                "ordering": ["grupo", "dia", "bloque__orden"],
                "unique_together": {("grupo", "dia", "bloque")},
            },
        ),
    ]
