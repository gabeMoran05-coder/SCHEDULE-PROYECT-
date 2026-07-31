from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("escuela", "0008_alumno_alergias_alumno_contacto_emergencia_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="docente",
            name="foto",
            field=models.FileField(blank=True, null=True, upload_to="docentes/fotos/"),
        ),
    ]
