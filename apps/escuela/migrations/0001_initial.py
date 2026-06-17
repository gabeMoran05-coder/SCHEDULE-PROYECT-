from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CicloEscolar",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(help_text="Ejemplo: 2025-2026", max_length=9)),
                ("fecha_inicio", models.DateField(blank=True, null=True)),
                ("fecha_fin", models.DateField(blank=True, null=True)),
                ("activo", models.BooleanField(default=False)),
            ],
            options={"verbose_name": "Ciclo escolar", "verbose_name_plural": "Ciclos escolares", "ordering": ["-nombre"]},
        ),
        migrations.CreateModel(
            name="Docente",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("numero_empleado", models.CharField(blank=True, max_length=20, null=True, unique=True)),
                ("nombres", models.CharField(max_length=80)),
                ("apellidos", models.CharField(max_length=100)),
                ("correo", models.EmailField(blank=True, max_length=254)),
                ("telefono", models.CharField(blank=True, max_length=20)),
                ("activo", models.BooleanField(default=True)),
            ],
            options={"ordering": ["apellidos", "nombres"]},
        ),
        migrations.CreateModel(
            name="Grupo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("grado", models.PositiveSmallIntegerField()),
                ("letra", models.CharField(max_length=2)),
                ("turno", models.CharField(choices=[("MATUTINO", "Matutino"), ("VESPERTINO", "Vespertino")], max_length=20)),
                ("aula_base", models.CharField(blank=True, max_length=30)),
            ],
            options={"ordering": ["ciclo", "grado", "letra"]},
        ),
        migrations.CreateModel(
            name="Institucion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=160, unique=True)),
                ("clave_cct", models.CharField(blank=True, max_length=20, verbose_name="CCT")),
                ("direccion", models.CharField(blank=True, max_length=220)),
                ("activa", models.BooleanField(default=True)),
            ],
            options={"verbose_name": "Institucion", "verbose_name_plural": "Instituciones", "ordering": ["nombre"]},
        ),
        migrations.CreateModel(
            name="Materia",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("clave", models.CharField(max_length=20, unique=True)),
                ("nombre", models.CharField(max_length=100)),
                ("grado", models.PositiveSmallIntegerField()),
            ],
            options={"ordering": ["grado", "nombre"]},
        ),
        migrations.CreateModel(
            name="Tutor",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("nombre", models.CharField(max_length=120)),
                ("telefono", models.CharField(blank=True, max_length=20)),
                ("correo", models.EmailField(blank=True, max_length=254)),
            ],
        ),
        migrations.AddField(
            model_name="cicloescolar",
            name="institucion",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="ciclos", to="escuela.institucion"),
        ),
        migrations.CreateModel(
            name="Periodo",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("numero", models.PositiveSmallIntegerField()),
                ("nombre", models.CharField(max_length=80)),
                ("fecha_inicio", models.DateField(blank=True, null=True)),
                ("fecha_fin", models.DateField(blank=True, null=True)),
                ("ciclo", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="periodos", to="escuela.cicloescolar")),
            ],
            options={"ordering": ["ciclo", "numero"], "unique_together": {("ciclo", "numero")}},
        ),
        migrations.CreateModel(
            name="ContratoDocente",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("horas_semanales", models.PositiveSmallIntegerField(default=0)),
                ("es_tutor", models.BooleanField(default=False)),
                ("activo", models.BooleanField(default=True)),
                ("ciclo", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="contratos_docentes", to="escuela.cicloescolar")),
                ("docente", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="contratos", to="escuela.docente")),
                ("institucion", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="contratos_docentes", to="escuela.institucion")),
            ],
            options={
                "verbose_name": "Contrato docente",
                "verbose_name_plural": "Contratos docentes",
                "ordering": ["docente__apellidos", "docente__nombres"],
                "unique_together": {("docente", "institucion", "ciclo")},
            },
        ),
        migrations.AddField(
            model_name="grupo",
            name="ciclo",
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="grupos", to="escuela.cicloescolar"),
        ),
        migrations.AddField(
            model_name="grupo",
            name="tutor",
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="grupos_tutorados", to="escuela.contratodocente"),
        ),
        migrations.CreateModel(
            name="Alumno",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("matricula", models.CharField(max_length=20, unique=True)),
                ("nombres", models.CharField(max_length=80)),
                ("apellidos", models.CharField(max_length=100)),
                ("fecha_nacimiento", models.DateField(blank=True, null=True)),
                ("activo", models.BooleanField(default=True)),
                ("institucion", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="alumnos", to="escuela.institucion")),
                ("tutor", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to="escuela.tutor")),
            ],
            options={"ordering": ["apellidos", "nombres"]},
        ),
        migrations.CreateModel(
            name="AsignacionDocenteMateria",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("horas_semanales", models.PositiveSmallIntegerField(default=1)),
                ("notas", models.CharField(blank=True, max_length=180)),
                ("contrato", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="asignaciones", to="escuela.contratodocente")),
                ("grupos", models.ManyToManyField(blank=True, related_name="asignaciones_docentes", to="escuela.grupo")),
                ("materia", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="asignaciones_docentes", to="escuela.materia")),
            ],
            options={
                "verbose_name": "Asignacion docente materia",
                "verbose_name_plural": "Asignaciones docente materia",
                "ordering": ["contrato__docente__apellidos", "materia__grado", "materia__nombre"],
            },
        ),
        migrations.CreateModel(
            name="Inscripcion",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("fecha", models.DateField(auto_now_add=True)),
                ("activa", models.BooleanField(default=True)),
                ("alumno", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="escuela.alumno")),
                ("ciclo", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="escuela.cicloescolar")),
                ("grupo", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to="escuela.grupo")),
            ],
            options={"unique_together": {("alumno", "ciclo")}},
        ),
        migrations.AlterUniqueTogether(name="cicloescolar", unique_together={("institucion", "nombre")}),
        migrations.AlterUniqueTogether(name="grupo", unique_together={("ciclo", "grado", "letra", "turno")}),
    ]
