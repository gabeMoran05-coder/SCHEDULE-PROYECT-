from django.conf import settings
from django.db import models


class Institucion(models.Model):
    nombre = models.CharField(max_length=160, unique=True)
    clave_cct = models.CharField("CCT", max_length=20, blank=True)
    direccion = models.CharField(max_length=220, blank=True)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Institucion"
        verbose_name_plural = "Instituciones"

    def __str__(self):
        return self.nombre


class CicloEscolar(models.Model):
    institucion = models.ForeignKey(Institucion, on_delete=models.PROTECT, related_name="ciclos")
    nombre = models.CharField(max_length=9, help_text="Ejemplo: 2025-2026")
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)
    activo = models.BooleanField(default=False)

    class Meta:
        ordering = ["-nombre"]
        unique_together = ["institucion", "nombre"]
        verbose_name = "Ciclo escolar"
        verbose_name_plural = "Ciclos escolares"

    def __str__(self):
        return f"{self.institucion} - {self.nombre}"


class Periodo(models.Model):
    ciclo = models.ForeignKey(CicloEscolar, on_delete=models.CASCADE, related_name="periodos")
    numero = models.PositiveSmallIntegerField()
    nombre = models.CharField(max_length=80)
    fecha_inicio = models.DateField(null=True, blank=True)
    fecha_fin = models.DateField(null=True, blank=True)

    class Meta:
        ordering = ["ciclo", "numero"]
        unique_together = ["ciclo", "numero"]

    def __str__(self):
        return f"{self.ciclo.nombre} - Periodo {self.numero}"


class Tutor(models.Model):
    nombre = models.CharField(max_length=120)
    parentesco = models.CharField(max_length=40, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    telefono_alterno = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)
    direccion = models.CharField(max_length=220, blank=True)
    ocupacion = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.nombre


class Alumno(models.Model):
    class TipoSangre(models.TextChoices):
        A_POS = "A+", "A+"
        A_NEG = "A-", "A-"
        B_POS = "B+", "B+"
        B_NEG = "B-", "B-"
        AB_POS = "AB+", "AB+"
        AB_NEG = "AB-", "AB-"
        O_POS = "O+", "O+"
        O_NEG = "O-", "O-"

    institucion = models.ForeignKey(Institucion, on_delete=models.PROTECT, related_name="alumnos")
    matricula = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.SET_NULL, null=True, blank=True)
    curp = models.CharField("CURP", max_length=18, blank=True)
    genero = models.CharField(max_length=30, blank=True)
    direccion = models.CharField(max_length=220, blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    contacto_emergencia = models.CharField(max_length=120, blank=True)
    telefono_emergencia = models.CharField(max_length=20, blank=True)
    parentesco_emergencia = models.CharField(max_length=40, blank=True)
    tipo_sangre = models.CharField(max_length=3, choices=TipoSangre.choices, blank=True)
    numero_seguridad_social = models.CharField(max_length=30, blank=True)
    institucion_medica = models.CharField(max_length=80, blank=True)
    alergias = models.TextField(blank=True)
    padecimientos = models.TextField(blank=True)
    medicamentos = models.TextField(blank=True)
    observaciones_medicas = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["apellidos", "nombres"]

    def __str__(self):
        return f"{self.matricula} - {self.apellidos} {self.nombres}"


class KardexAlumno(models.Model):
    class TipoMovimiento(models.TextChoices):
        ALTA = "ALTA", "Alta"
        EDICION = "EDICION", "Edicion"
        CAMBIO_GRUPO = "CAMBIO_GRUPO", "Cambio de grupo"
        DOCUMENTO = "DOCUMENTO", "Documento"
        BAJA = "BAJA", "Baja u ocultamiento"
        RESTAURACION = "RESTAURACION", "Restauracion"
        SALUD = "SALUD", "Salud"
        CONTACTO = "CONTACTO", "Contacto"
        OTRO = "OTRO", "Otro"

    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name="kardex")
    inscripcion = models.ForeignKey("Inscripcion", on_delete=models.SET_NULL, null=True, blank=True, related_name="kardex")
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=24, choices=TipoMovimiento.choices)
    referencia = models.CharField(max_length=160, blank=True)
    descripcion = models.TextField(blank=True)
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Kardex alumno"
        verbose_name_plural = "Kardex alumnos"

    def __str__(self):
        return f"{self.alumno} - {self.get_tipo_display()} - {self.fecha:%Y-%m-%d %H:%M}"


class DocumentoAlumno(models.Model):
    class TipoDocumento(models.TextChoices):
        ACTA = "ACTA", "Acta de nacimiento"
        CURP = "CURP", "CURP"
        COMPROBANTE_DOMICILIO = "COMPROBANTE_DOMICILIO", "Comprobante de domicilio"
        CERTIFICADO_MEDICO = "CERTIFICADO_MEDICO", "Certificado medico"
        NSS = "NSS", "Numero de seguridad social"
        BOLETA = "BOLETA", "Boleta o calificaciones"
        IDENTIFICACION_TUTOR = "IDENTIFICACION_TUTOR", "Identificacion del tutor"
        AUTORIZACION = "AUTORIZACION", "Autorizacion"
        OTRO = "OTRO", "Otro"

    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE, related_name="documentos")
    tipo = models.CharField(max_length=32, choices=TipoDocumento.choices)
    nombre = models.CharField(max_length=120)
    archivo = models.FileField(upload_to="alumnos/documentos/")
    notas = models.CharField(max_length=220, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-fecha_subida"]
        verbose_name = "Documento de alumno"
        verbose_name_plural = "Documentos de alumnos"

    def __str__(self):
        return f"{self.alumno} - {self.get_tipo_display()}"


class Docente(models.Model):
    numero_empleado = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=100)
    correo = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
    foto = models.FileField(upload_to="docentes/fotos/", blank=True, null=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["apellidos", "nombres"]

    def __str__(self):
        return f"{self.apellidos} {self.nombres}"


class ContratoDocente(models.Model):
    docente = models.ForeignKey(Docente, on_delete=models.CASCADE, related_name="contratos")
    institucion = models.ForeignKey(Institucion, on_delete=models.PROTECT, related_name="contratos_docentes")
    ciclo = models.ForeignKey(CicloEscolar, on_delete=models.PROTECT, related_name="contratos_docentes")
    horas_semanales = models.PositiveSmallIntegerField(default=0)
    es_tutor = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["docente__apellidos", "docente__nombres"]
        unique_together = ["docente", "institucion", "ciclo"]
        verbose_name = "Contrato docente"
        verbose_name_plural = "Contratos docentes"

    def __str__(self):
        return f"{self.docente} - {self.ciclo.nombre} ({self.horas_semanales} h)"


class Materia(models.Model):
    institucion = models.ForeignKey(Institucion, on_delete=models.PROTECT, related_name="materias", null=True, blank=True)
    clave = models.CharField(max_length=20)
    nombre = models.CharField(max_length=100)
    grado = models.PositiveSmallIntegerField()
    horas_semanales = models.PositiveSmallIntegerField(default=1)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["grado", "nombre"]
        unique_together = ["institucion", "clave"]

    def __str__(self):
        return f"{self.nombre} ({self.grado})"


class Grupo(models.Model):
    TURNO_CHOICES = [
        ("MATUTINO", "Matutino"),
        ("VESPERTINO", "Vespertino"),
    ]

    ciclo = models.ForeignKey(CicloEscolar, on_delete=models.PROTECT, related_name="grupos")
    grado = models.PositiveSmallIntegerField()
    letra = models.CharField(max_length=2)
    turno = models.CharField(max_length=20, choices=TURNO_CHOICES)
    aula_base = models.CharField(max_length=30, blank=True)
    tutor = models.ForeignKey(ContratoDocente, on_delete=models.SET_NULL, null=True, blank=True, related_name="grupos_tutorados")
    activo = models.BooleanField(default=True)

    class Meta:
        unique_together = ["ciclo", "grado", "letra", "turno"]
        ordering = ["ciclo", "grado", "letra"]

    def __str__(self):
        return f"{self.grado}{self.letra} - {self.turno}"


class Inscripcion(models.Model):
    alumno = models.ForeignKey(Alumno, on_delete=models.CASCADE)
    grupo = models.ForeignKey(Grupo, on_delete=models.PROTECT)
    ciclo = models.ForeignKey(CicloEscolar, on_delete=models.PROTECT)
    numero_lista = models.PositiveSmallIntegerField(null=True, blank=True)
    fecha = models.DateField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    class Meta:
        unique_together = ["alumno", "ciclo"]
        ordering = ["grupo__grado", "grupo__letra", "numero_lista", "alumno__apellidos", "alumno__nombres"]

    def __str__(self):
        return f"{self.alumno} en {self.grupo}"


class AsignacionDocenteMateria(models.Model):
    contrato = models.ForeignKey(ContratoDocente, on_delete=models.CASCADE, related_name="asignaciones")
    materia = models.ForeignKey(Materia, on_delete=models.PROTECT, related_name="asignaciones_docentes")
    grupos = models.ManyToManyField(Grupo, blank=True, related_name="asignaciones_docentes")
    horas_semanales = models.PositiveSmallIntegerField(default=1)
    notas = models.CharField(max_length=180, blank=True)

    class Meta:
        ordering = ["contrato__docente__apellidos", "materia__grado", "materia__nombre"]
        verbose_name = "Asignacion docente materia"
        verbose_name_plural = "Asignaciones docente materia"

    def __str__(self):
        return f"{self.contrato.docente} - {self.materia}"


class KardexDocente(models.Model):
    class TipoMovimiento(models.TextChoices):
        ALTA = "ALTA", "Alta"
        CAMBIO_ESCUELA = "CAMBIO_ESCUELA", "Cambio de escuela"
        ASIGNACION = "ASIGNACION", "Asignacion"
        RETIRO = "RETIRO", "Retiro"
        BAJA = "BAJA", "Baja"
        RESTAURACION = "RESTAURACION", "Restauracion"
        AJUSTE = "AJUSTE", "Ajuste"

    class MotivoMovimiento(models.TextChoices):
        INCAPACIDAD = "INCAPACIDAD", "Incapacidad"
        LICENCIA_MEDICA = "LICENCIA_MEDICA", "Licencia medica"
        LICENCIA_SIN_GOCE = "LICENCIA_SIN_GOCE", "Licencia sin goce"
        PERMISO_PERSONAL = "PERMISO_PERSONAL", "Permiso por asuntos personales"
        COMISION = "COMISION", "Comision"
        CAMBIO_ADSCRIPCION = "CAMBIO_ADSCRIPCION", "Cambio de adscripcion"
        REUBICACION = "REUBICACION", "Reubicacion"
        GRAVIDEZ_MATERNIDAD = "GRAVIDEZ_MATERNIDAD", "Gravidez o maternidad"
        PATERNIDAD = "PATERNIDAD", "Paternidad"
        CUIDADOS_FAMILIARES = "CUIDADOS_FAMILIARES", "Cuidados familiares"
        CAPACITACION = "CAPACITACION", "Capacitacion"
        JUBILACION = "JUBILACION", "Jubilacion"
        RENUNCIA = "RENUNCIA", "Renuncia"
        BAJA_DEFINITIVA = "BAJA_DEFINITIVA", "Baja definitiva"
        REINCORPORACION = "REINCORPORACION", "Reincorporacion"
        FIN_LICENCIA = "FIN_LICENCIA", "Fin de licencia"
        OTRO = "OTRO", "Otro"

    docente = models.ForeignKey(Docente, on_delete=models.CASCADE, related_name="kardex")
    contrato = models.ForeignKey(ContratoDocente, on_delete=models.SET_NULL, null=True, blank=True, related_name="kardex")
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=24, choices=TipoMovimiento.choices)
    motivo = models.CharField(max_length=32, choices=MotivoMovimiento.choices, blank=True)
    referencia = models.CharField(max_length=160, blank=True)
    descripcion = models.TextField(blank=True)
    documento_referencia = models.CharField(max_length=80, blank=True)
    horas_antes = models.PositiveSmallIntegerField(default=0)
    horas_despues = models.PositiveSmallIntegerField(default=0)
    horas_movimiento = models.IntegerField(default=0)
    responsable = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Kardex docente"
        verbose_name_plural = "Kardex docentes"

    def __str__(self):
        return f"{self.docente} - {self.get_tipo_display()} - {self.fecha:%Y-%m-%d %H:%M}"
