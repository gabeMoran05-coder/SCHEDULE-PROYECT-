from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("escuela", "0005_kardexdocente"),
    ]

    operations = [
        migrations.AddField(
            model_name="kardexdocente",
            name="documento_referencia",
            field=models.CharField(blank=True, max_length=80),
        ),
        migrations.AddField(
            model_name="kardexdocente",
            name="motivo",
            field=models.CharField(
                blank=True,
                choices=[
                    ("INCAPACIDAD", "Incapacidad"),
                    ("LICENCIA_MEDICA", "Licencia medica"),
                    ("LICENCIA_SIN_GOCE", "Licencia sin goce"),
                    ("PERMISO_PERSONAL", "Permiso por asuntos personales"),
                    ("COMISION", "Comision"),
                    ("CAMBIO_ADSCRIPCION", "Cambio de adscripcion"),
                    ("REUBICACION", "Reubicacion"),
                    ("GRAVIDEZ_MATERNIDAD", "Gravidez o maternidad"),
                    ("PATERNIDAD", "Paternidad"),
                    ("CUIDADOS_FAMILIARES", "Cuidados familiares"),
                    ("CAPACITACION", "Capacitacion"),
                    ("JUBILACION", "Jubilacion"),
                    ("RENUNCIA", "Renuncia"),
                    ("BAJA_DEFINITIVA", "Baja definitiva"),
                    ("REINCORPORACION", "Reincorporacion"),
                    ("FIN_LICENCIA", "Fin de licencia"),
                    ("OTRO", "Otro"),
                ],
                max_length=32,
            ),
        ),
    ]
