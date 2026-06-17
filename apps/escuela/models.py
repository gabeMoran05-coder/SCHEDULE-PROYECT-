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
    telefono = models.CharField(max_length=20, blank=True)
    correo = models.EmailField(blank=True)

    def __str__(self):
        return self.nombre


class Alumno(models.Model):
    institucion = models.ForeignKey(Institucion, on_delete=models.PROTECT, related_name="alumnos")
    matricula = models.CharField(max_length=20, unique=True)
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    tutor = models.ForeignKey(Tutor, on_delete=models.SET_NULL, null=True, blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ["apellidos", "nombres"]

    def __str__(self):
        return f"{self.matricula} - {self.apellidos} {self.nombres}"


class Docente(models.Model):
    numero_empleado = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=100)
    correo = models.EmailField(blank=True)
    telefono = models.CharField(max_length=20, blank=True)
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
    fecha = models.DateField(auto_now_add=True)
    activa = models.BooleanField(default=True)

    class Meta:
        unique_together = ["alumno", "ciclo"]

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
