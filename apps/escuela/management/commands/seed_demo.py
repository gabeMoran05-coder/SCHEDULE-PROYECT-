from datetime import time

from django.core.management.base import BaseCommand

from apps.escuela.models import CicloEscolar, Grupo, Institucion, Materia, Periodo
from apps.horarios.models import BloqueHorario


class Command(BaseCommand):
    help = "Crea datos base para probar el sistema escolar."

    def handle(self, *args, **options):
        institucion, _ = Institucion.objects.get_or_create(
            nombre="Ricardo Flores Magon",
            defaults={"clave_cct": "PENDIENTE", "activa": True},
        )

        ciclo, _ = CicloEscolar.objects.get_or_create(
            institucion=institucion,
            nombre="2025-2026",
            defaults={"activo": True},
        )
        CicloEscolar.objects.exclude(id=ciclo.id).update(activo=False)

        for numero in range(1, 4):
            Periodo.objects.get_or_create(
                ciclo=ciclo,
                numero=numero,
                defaults={"nombre": f"Periodo {numero}"},
            )

        for grado in range(1, 4):
            for letra in ["A", "B", "C", "D", "E"]:
                Grupo.objects.get_or_create(
                    ciclo=ciclo,
                    grado=grado,
                    letra=letra,
                    turno="MATUTINO",
                    defaults={"aula_base": f"Aula {grado}{letra}"},
                )

        materias = [
            ("ESP1", "Espanol", 1),
            ("MAT1", "Matematicas", 1),
            ("CIE1", "Ciencias", 1),
            ("ESP2", "Espanol", 2),
            ("MAT2", "Matematicas", 2),
            ("HIS2", "Historia", 2),
            ("ESP3", "Espanol", 3),
            ("MAT3", "Matematicas", 3),
            ("QUI3", "Quimica", 3),
        ]
        for clave, nombre, grado in materias:
            Materia.objects.get_or_create(clave=clave, defaults={"nombre": nombre, "grado": grado})

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
