import hashlib
import os
import re
import sys
import unicodedata
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import django

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "secundaria.settings")
django.setup()

from apps.escuela.models import Alumno, CicloEscolar, Grupo, Inscripcion, Institucion  # noqa: E402


NS = {
    "a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}

FILES = [
    Path("BaseDeDatos/imports/primer_grado_periodo_3.xlsx"),
    Path("BaseDeDatos/imports/segundo_grado_periodo_3.xlsx"),
]


def _cell_column(ref):
    return re.match(r"([A-Z]+)", ref).group(1)


def _plain_key(value):
    value = unicodedata.normalize("NFKD", value)
    value = "".join(ch for ch in value if not unicodedata.combining(ch))
    return re.sub(r"\s+", " ", value.upper()).strip()


def _pretty_name(value):
    replacements = {
        " De ": " de ",
        " Del ": " del ",
        " La ": " la ",
        " Las ": " las ",
        " Los ": " los ",
        " Y ": " y ",
    }
    pretty = _plain_key(value).title()
    for old, new in replacements.items():
        pretty = pretty.replace(old, new)
    return pretty


def _matricula(ciclo, grupo, nombre):
    digest = hashlib.sha1(_plain_key(nombre).encode("utf-8")).hexdigest()[:6].upper()
    ciclo_tag = ciclo.nombre.split("-")[0][-2:]
    return f"RFM{ciclo_tag}-{grupo}-{digest}"


def _read_workbook(path):
    result = {}
    with zipfile.ZipFile(path) as archive:
        shared = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            shared = [
                "".join(t.text or "" for t in item.findall(".//a:t", NS))
                for item in root.findall("a:si", NS)
            ]

        workbook = ET.fromstring(archive.read("xl/workbook.xml"))
        rels = ET.fromstring(archive.read("xl/_rels/workbook.xml.rels"))
        rid_to_target = {rel.attrib["Id"]: rel.attrib["Target"] for rel in rels}

        for sheet in workbook.findall("a:sheets/a:sheet", NS):
            sheet_name = sheet.attrib["name"].strip()
            if not re.match(r"^[123][A-Z]$", sheet_name):
                continue

            rel_id = sheet.attrib["{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id"]
            target = rid_to_target[rel_id].lstrip("/")
            sheet_path = f"xl/{target}" if not target.startswith("xl/") else target
            root = ET.fromstring(archive.read(sheet_path))
            names = []

            for row in root.findall("a:sheetData/a:row", NS):
                cells = {}
                for cell in row.findall("a:c", NS):
                    value = cell.find("a:v", NS)
                    if value is None:
                        continue
                    text = value.text or ""
                    if cell.attrib.get("t") == "s":
                        text = shared[int(text)] if text.isdigit() and int(text) < len(shared) else text
                    cells[_cell_column(cell.attrib["r"])] = str(text).strip()

                alumno = cells.get("C", "")
                if cells.get("B", "").isdigit() and alumno and "ALUMNO" not in alumno.upper():
                    names.append(alumno)

            result[sheet_name] = sorted(set(names), key=_plain_key)
    return result


def main():
    institucion, _ = Institucion.objects.get_or_create(
        nombre="Ricardo Flores Magon",
        defaults={"clave_cct": "06DES0006E", "direccion": "Manzanillo, Colima", "activa": True},
    )
    ciclo, _ = CicloEscolar.objects.get_or_create(
        institucion=institucion,
        nombre="2025-2026",
        defaults={"activo": True},
    )
    for numero in range(1, 4):
        ciclo.periodos.get_or_create(numero=numero, defaults={"nombre": f"Periodo {numero}"})

    created_students = 0
    updated_students = 0
    created_inscriptions = 0
    updated_inscriptions = 0

    for file_path in FILES:
        for sheet_name, names in _read_workbook(file_path).items():
            grado = int(sheet_name[0])
            letra = sheet_name[1]
            grupo, _ = Grupo.objects.get_or_create(
                ciclo=ciclo,
                grado=grado,
                letra=letra,
                turno="MATUTINO",
                defaults={"aula_base": f"Aula {sheet_name}", "activo": True},
            )

            for numero_lista, nombre_original in enumerate(names, start=1):
                nombre = _pretty_name(nombre_original)
                matricula = _matricula(ciclo, sheet_name, nombre_original)
                alumno, created = Alumno.objects.update_or_create(
                    matricula=matricula,
                    defaults={
                        "institucion": institucion,
                        "apellidos": nombre,
                        "nombres": "",
                        "activo": True,
                    },
                )
                created_students += int(created)
                updated_students += int(not created)

                _, inscription_created = Inscripcion.objects.update_or_create(
                    alumno=alumno,
                    ciclo=ciclo,
                    defaults={
                        "grupo": grupo,
                        "numero_lista": numero_lista,
                        "activa": True,
                    },
                )
                created_inscriptions += int(inscription_created)
                updated_inscriptions += int(not inscription_created)

            print(f"{sheet_name}: {len(names)} alumno(s) importados con lista alfabetica")

    print(
        {
            "alumnos_creados": created_students,
            "alumnos_actualizados": updated_students,
            "inscripciones_creadas": created_inscriptions,
            "inscripciones_actualizadas": updated_inscriptions,
        }
    )


if __name__ == "__main__":
    main()
