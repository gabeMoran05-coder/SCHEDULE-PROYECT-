from datetime import time

from django.contrib.auth.models import Group, User
from django.core.management.base import BaseCommand

from apps.escuela.models import (
    AsignacionDocenteMateria,
    CicloEscolar,
    ContratoDocente,
    Docente,
    Grupo,
    Institucion,
    Materia,
    Periodo,
)
from apps.horarios.models import BloqueHorario, FichaAsignacion


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

        grupos_por_codigo = {f"{grupo.grado}{grupo.letra}": grupo for grupo in Grupo.objects.filter(ciclo=ciclo)}
        materias_por_clave = {materia.clave: materia for materia in Materia.objects.filter(institucion=institucion)}

        asignaciones_plantilla = [
            ("DANIELA YORDANKA LUVINOFF HERNANDEZ", "ESP1", ["1A", "1B", "1C", "1D"]),
            ("OMAR ALEJANDRO AGUILAR SAUCEDO", "ESP1", ["1E"]),
            ("ANA VICTORIA GALVEZ MENESES", "ING1", ["1A", "1B", "1C", "1D", "1E"]),
            ("ABEL ARNOLDO PUENTE NAVA", "MAT1", ["1A", "1B", "1C", "1D"]),
            ("ANDREA STEPHANIE BARRERA MORENO", "MAT1", ["1E"]),
            ("SILVIA MARIA TOLAZA SOTELO", "CIE1", ["1A", "1B", "1C", "1D"]),
            ("JUDITH DEL CARMEN ALIANO EVARISTO", "CIE1", ["1E"]),
            ("EDGAR NOE PEREZ GARCIA", "GEO1", ["1A", "1E"]),
            ("JESICA CAROLINA GUERRERO PEREZ", "GEO1", ["1B"]),
            ("LUIS ENRIQUE ALVARADO CHAVEZ", "GEO1", ["1C", "1D"]),
            ("TOMAS VAZQUEZ CERVANTES", "HIS1", ["1A", "1E"]),
            ("EDGAR NOE PEREZ GARCIA", "HIS1", ["1B", "1C", "1D"]),
            ("YURIDIA NAYELI MARQUEZ ESQUEDA", "FCE1", ["1A", "1B"]),
            ("JESICA CAROLINA GUERRERO PEREZ", "FCE1", ["1C", "1D", "1E"]),
            ("JUAN MIGUEL FIGUEROA GARCIA", "ART1", ["1A", "1B", "1C", "1D", "1E"]),
            ("CESAR ALEJANDRO ROBLES MORA", "EDF1", ["1A", "1B", "1C", "1D", "1E"]),
            ("JUAN MIGUEL FIGUEROA GARCIA", "TUT1", ["1A", "1C"]),
            ("JESICA CAROLINA GUERRERO PEREZ", "TUT1", ["1B"]),
            ("JUDITH DEL CARMEN ALIANO EVARISTO", "TUT1", ["1D"]),
            ("LUIS ENRIQUE ALVARADO CHAVEZ", "TUT1", ["1E"]),
            ("ALFREDO TOLAZA SOTELO", "TEC1", ["1A"]),
            ("ENRIQUE ROMERO BEAS", "TEC1", ["1B", "1C", "1D"]),
            ("SERGIO MISAEL SANTANA RAMIREZ", "TEC1", ["1E"]),
            ("JUDITH DEL CARMEN ALIANO EVARISTO", "INT1", ["1A"]),
            ("YURIDIA NAYELI MARQUEZ ESQUEDA", "INT1", ["1B"]),
            ("ALFREDO VALENCIA DELGADO", "INT1", ["1C", "1D", "1E"]),
            ("RUBEN RODRIGUEZ VIDRIO", "ESP2", ["2A", "2B", "2C", "2D"]),
            ("OMAR ALEJANDRO AGUILAR SAUCEDO", "ESP2", ["2E"]),
            ("ANGEL IGNACIO LOPEZ RIVERA", "ING2", ["2A", "2B", "2C", "2D", "2E"]),
            ("ANDREA STEPHANIE BARRERA MORENO", "MAT2", ["2A", "2B"]),
            ("CITLALI VALDEZ LEON", "MAT2", ["2C", "2D"]),
            ("JOSE HERIBERTO MOLINA DELGADO", "MAT2", ["2E"]),
            ("RICARDO HAUCHBAUM CERVANTES", "CIE2", ["2A", "2B", "2C", "2D"]),
            ("SILVIA MARIA TOLAZA SOTELO", "CIE2", ["2E"]),
            ("JESICA CAROLINA GUERRERO PEREZ", "FCE2", ["2A", "2B", "2C", "2D", "2E"]),
            ("TOMAS VAZQUEZ CERVANTES", "HIS2", ["2A", "2B", "2C", "2D", "2E"]),
            ("CINTHYA YURIANA MANCILLA GONZALEZ", "ART2", ["2A", "2B", "2C", "2D", "2E"]),
            ("DANIEL CARRASCO VEGA", "EDF2", ["2A", "2B", "2C", "2D", "2E"]),
            ("ALFREDO TOLAZA SOTELO", "TUT2", ["2A"]),
            ("MA. FRANCISCA FIGUEROA HERNANDEZ", "TUT2", ["2B", "2C"]),
            ("ANGEL IGNACIO LOPEZ RIVERA", "TUT2", ["2D"]),
            ("SERGIO MISAEL SANTANA RAMIREZ", "TUT2", ["2E"]),
            ("ALFREDO TOLAZA SOTELO", "TEC2", ["2A", "2B"]),
            ("ENRIQUE ROMERO BEAS", "TEC2", ["2C", "2E"]),
            ("IVAN ERNESTO VEGA CEDEÑO", "TEC2", ["2D"]),
            ("CINTHYA YURIANA MANCILLA GONZALEZ", "INT2", ["2A"]),
            ("ALFREDO TOLAZA SOTELO", "INT2", ["2B"]),
            ("ALFREDO VALENCIA DELGADO", "INT2", ["2C", "2D", "2E"]),
            ("OMAR ALEJANDRO AGUILAR SAUCEDO", "ESP3", ["3A", "3B", "3C", "3D"]),
            ("EDITH LOPEZ TEJEDA", "ING3", ["3A", "3B", "3C"]),
            ("ANGEL IGNACIO LOPEZ RIVERA", "ING3", ["3D"]),
            ("ANDREA STEPHANIE BARRERA MORENO", "MAT3", ["3A", "3B", "3C", "3D"]),
            ("CESAR DANIEL TORRES CANTERO", "CIE3", ["3A", "3B", "3C"]),
            ("SILVIA MARIA TOLAZA SOTELO", "CIE3", ["3D"]),
            ("JESICA CAROLINA GUERRERO PEREZ", "FCE3", ["3A", "3B", "3C", "3D"]),
            ("EDGAR NOE PEREZ GARCIA", "HIS3", ["3A", "3B", "3C", "3D"]),
            ("HAYDEE JOSEFINA NUÑEZ MUÑOZ", "ART3", ["3A", "3B", "3C"]),
            ("CARLOS ALBERTO MUÑOZ AGUILAR", "ART3", ["3D"]),
            ("CESAR ALEJANDRO ROBLES MORA", "EDF3", ["3A", "3B"]),
            ("DANIEL CARRASCO VEGA", "EDF3", ["3C"]),
            ("FRYCER DAVID TINTOS GUTIERREZ", "EDF3", ["3D"]),
            ("ALFREDO TOLAZA SOTELO", "TUT3", ["3A"]),
            ("SERGIO MISAEL SANTANA RAMIREZ", "TUT3", ["3B"]),
            ("HAYDEE JOSEFINA NUÑEZ MUÑOZ", "TUT3", ["3C"]),
            ("EDGAR NOE PEREZ GARCIA", "TUT3", ["3D"]),
            ("ALFREDO TOLAZA SOTELO", "TEC3", ["3A"]),
            ("IVAN ERNESTO VEGA CEDEÑO", "TEC3", ["3B", "3D"]),
            ("SERGIO MISAEL SANTANA RAMIREZ", "TEC3", ["3C"]),
            ("YURIDIA NAYELI MARQUEZ ESQUEDA", "INT3", ["3A", "3B", "3D"]),
            ("SERGIO MISAEL SANTANA RAMIREZ", "INT3", ["3C"]),
        ]

        contratos = {}
        for indice, nombre_docente in enumerate(sorted({nombre for nombre, _, _ in asignaciones_plantilla}), start=1):
            docente, _ = Docente.objects.update_or_create(
                numero_empleado=f"TPL-{indice:03d}",
                defaults={
                    "nombres": "",
                    "apellidos": nombre_docente.title(),
                    "correo": "",
                    "telefono": "",
                    "activo": True,
                },
            )
            contrato, _ = ContratoDocente.objects.update_or_create(
                docente=docente,
                institucion=institucion,
                ciclo=ciclo,
                defaults={"activo": True, "es_tutor": False},
            )
            contratos[nombre_docente] = contrato

        horas_por_contrato = {contrato.id: 0 for contrato in contratos.values()}
        for nombre_docente, clave_materia, codigos_grupo in asignaciones_plantilla:
            contrato = contratos[nombre_docente]
            materia = materias_por_clave[clave_materia]
            grupos = [grupos_por_codigo[codigo] for codigo in codigos_grupo if codigo in grupos_por_codigo]
            asignacion = AsignacionDocenteMateria.objects.filter(contrato=contrato, materia=materia).first()
            if asignacion is None:
                asignacion = AsignacionDocenteMateria.objects.create(
                    contrato=contrato,
                    materia=materia,
                    horas_semanales=materia.horas_semanales,
                    notas="Cargado desde plantilla 2025-2026.",
                )
            else:
                asignacion.horas_semanales = materia.horas_semanales
                asignacion.notas = "Cargado desde plantilla 2025-2026."
                asignacion.save()

            asignacion.grupos.set(grupos)
            FichaAsignacion.objects.filter(asignacion=asignacion).exclude(grupo__in=grupos).delete()
            for grupo in grupos:
                FichaAsignacion.objects.update_or_create(
                    asignacion=asignacion,
                    grupo=grupo,
                    defaults={"aula": grupo.aula_base, "horas_por_colocar": materia.horas_semanales},
                )
            horas_por_contrato[contrato.id] += materia.horas_semanales * len(grupos)

        for contrato in contratos.values():
            contrato.horas_semanales = horas_por_contrato[contrato.id]
            contrato.save(update_fields=["horas_semanales"])

        self.stdout.write(self.style.SUCCESS("Datos demo creados correctamente."))
