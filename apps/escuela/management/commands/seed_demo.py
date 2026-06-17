from datetime import time

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from apps.escuela.models import CicloEscolar, Grupo, Institucion, Materia, Periodo
from apps.horarios.models import BloqueHorario


class Command(BaseCommand):
    help = "Crea datos base para probar el sistema escolar."

    def handle(self, *args, **options):
        admin_user, _ = User.objects.update_or_create(
            username="Admin",
            defaults={
                "email": "admin@secundaria.local",
                "is_staff": True,
                "is_superuser": True,
            },
        )
        admin_user.set_password("12345")
        admin_user.save()

        directivo_group, _ = Group.objects.get_or_create(name="Directivo")
        directivo_user, _ = User.objects.update_or_create(
            username="Directivo",
            defaults={
                "email": "directivo@secundaria.local",
                "is_staff": True,
                "is_superuser": False,
            },
        )
        directivo_user.set_password("12345")
        directivo_user.groups.add(directivo_group)
        directivo_user.save()

        institucion, _ = Institucion.objects.get_or_create(
            nombre="Ricardo Flores Magon",
            defaults={"clave_cct": "PENDIENTE", "activa": True},
        )

        ciclo, _ = CicloEscolar.objects.get_or_create(
            institucion=institucion,
            nombre="2025-2026",
            defaults={"activo": True},
        )
        CicloEscolar.objects.filter(institucion=institucion).exclude(id=ciclo.id).update(activo=False)

        for numero in range(1, 4):
            Periodo.objects.get_or_create(
                ciclo=ciclo,
                numero=numero,
                defaults={"nombre": f"Periodo {numero}"},
            )

        grupos_por_grado = {
            1: ["A", "B", "C", "D", "E"],
            2: ["A", "B", "C", "D", "E"],
            3: ["A", "B", "C", "D"],
        }
        for grado, letras in grupos_por_grado.items():
            for letra in letras:
                Grupo.objects.get_or_create(
                    ciclo=ciclo,
                    grado=grado,
                    letra=letra,
                    turno="MATUTINO",
                    defaults={"aula_base": f"Aula {grado}{letra}"},
                )

        materias = [
            ("ESP1", "Espanol", 1, 5),
            ("ING1", "Ingles", 1, 3),
            ("MAT1", "Matematicas", 1, 5),
            ("CIE1", "Ciencias", 1, 4),
            ("GEO1", "Geografia", 1, 4),
            ("HIS1", "Historia", 1, 2),
            ("FCE1", "FCE", 1, 2),
            ("ART1", "Artes", 1, 3),
            ("EDF1", "Educacion fisica", 1, 2),
            ("TUT1", "Tutoria", 1, 1),
            ("TEC1", "Tecnologia", 1, 3),
            ("INT1", "Integracion curricular", 1, 1),
            ("ESP2", "Espanol", 2, 5),
            ("ING2", "Ingles", 2, 3),
            ("MAT2", "Matematicas", 2, 5),
            ("CIE2", "Ciencias", 2, 6),
            ("FCE2", "FCE", 2, 2),
            ("HIS2", "Historia", 2, 4),
            ("ART2", "Artes", 2, 3),
            ("EDF2", "Educacion fisica", 2, 2),
            ("TUT2", "Tutoria", 2, 1),
            ("TEC2", "Tecnologia", 2, 3),
            ("INT2", "Integracion curricular", 2, 1),
            ("ESP3", "Espanol", 3, 5),
            ("ING3", "Ingles", 3, 3),
            ("MAT3", "Matematicas", 3, 5),
            ("CIE3", "Ciencias", 3, 6),
            ("FCE3", "FCE", 3, 2),
            ("HIS3", "Historia", 3, 4),
            ("ART3", "Artes", 3, 3),
            ("EDF3", "Educacion fisica", 3, 2),
            ("TUT3", "Tutoria", 3, 1),
            ("TEC3", "Tecnologia", 3, 3),
            ("INT3", "Integracion curricular", 3, 1),
        ]
        claves_plantilla = {clave for clave, _, _, _ in materias}
        Materia.objects.filter(institucion=institucion, clave__in=["QUI3"]).exclude(clave__in=claves_plantilla).delete()
        for clave, nombre, grado, horas in materias:
            Materia.objects.update_or_create(
                institucion=institucion,
                clave=clave,
                defaults={"nombre": nombre, "grado": grado, "horas_semanales": horas},
            )

        bloques = [
            (1, time(7, 0), time(7, 50), False),
            (2, time(7, 50), time(8, 40), False),
            (3, time(8, 40), time(9, 30), False),
            (4, time(9, 30), time(9, 50), True),
            (5, time(9, 50), time(10, 40), False),
            (6, time(10, 40), time(11, 30), False),
            (7, time(11, 30), time(12, 20), False),
            (8, time(12, 20), time(13, 10), False),
        ]
        for orden, inicio, fin, es_receso in bloques:
            BloqueHorario.objects.get_or_create(
                ciclo=ciclo,
                orden=orden,
                defaults={"hora_inicio": inicio, "hora_fin": fin, "es_receso": es_receso},
            )

        self.stdout.write(self.style.SUCCESS("Datos demo creados correctamente."))
