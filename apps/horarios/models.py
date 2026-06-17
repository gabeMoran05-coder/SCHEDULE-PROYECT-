from django.db import models

from apps.escuela.models import AsignacionDocenteMateria, CicloEscolar, ContratoDocente, Grupo, Materia, Periodo


class DiaSemana(models.TextChoices):
    LUNES = "LUNES", "Lunes"
    MARTES = "MARTES", "Martes"
    MIERCOLES = "MIERCOLES", "Miercoles"
    JUEVES = "JUEVES", "Jueves"
    VIERNES = "VIERNES", "Viernes"


class BloqueHorario(models.Model):
    ciclo = models.ForeignKey(CicloEscolar, on_delete=models.CASCADE, related_name="bloques_horario")
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()
    orden = models.PositiveSmallIntegerField()
    es_receso = models.BooleanField(default=False)

    class Meta:
        ordering = ["ciclo", "orden"]
        unique_together = ["ciclo", "orden"]
        verbose_name = "Bloque horario"
        verbose_name_plural = "Bloques horario"

    def __str__(self):
        return f"{self.hora_inicio} - {self.hora_fin}"


class DisponibilidadDocente(models.Model):
    contrato = models.ForeignKey(ContratoDocente, on_delete=models.CASCADE, related_name="disponibilidades")
    dia = models.CharField(max_length=12, choices=DiaSemana.choices)
    bloque = models.ForeignKey(BloqueHorario, on_delete=models.CASCADE)
    disponible = models.BooleanField(default=True)
    observaciones = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ["contrato", "dia", "bloque__orden"]
        unique_together = ["contrato", "dia", "bloque"]
        verbose_name = "Disponibilidad docente"
        verbose_name_plural = "Disponibilidades docentes"

    def __str__(self):
        return f"{self.contrato.docente} - {self.get_dia_display()} - {self.bloque}"


class FichaAsignacion(models.Model):
    asignacion = models.ForeignKey(AsignacionDocenteMateria, on_delete=models.CASCADE, related_name="fichas")
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE, related_name="fichas_horario")
    aula = models.CharField(max_length=30, blank=True)
    horas_por_colocar = models.PositiveSmallIntegerField(default=1)
    color = models.CharField(max_length=7, default="#0f766e")
    notas = models.CharField(max_length=180, blank=True)

    class Meta:
        ordering = ["asignacion__contrato__docente__apellidos", "grupo__grado", "grupo__letra"]
        verbose_name = "Ficha de asignacion"
        verbose_name_plural = "Fichas de asignacion"

    def __str__(self):
        return f"{self.asignacion.contrato.docente} - {self.asignacion.materia} - {self.grupo}"


class HorarioClase(models.Model):
    DIAS = [
        DiaSemana.LUNES,
        DiaSemana.MARTES,
        DiaSemana.MIERCOLES,
        DiaSemana.JUEVES,
        DiaSemana.VIERNES,
    ]

    periodo = models.ForeignKey(Periodo, on_delete=models.PROTECT, null=True, blank=True, related_name="horarios")
    ciclo = models.ForeignKey(CicloEscolar, on_delete=models.PROTECT, related_name="horarios")
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    materia = models.ForeignKey(Materia, on_delete=models.PROTECT)
    contrato = models.ForeignKey(ContratoDocente, on_delete=models.PROTECT, related_name="horarios")
    ficha = models.ForeignKey(FichaAsignacion, on_delete=models.SET_NULL, null=True, blank=True, related_name="clases_colocadas")
    dia = models.CharField(max_length=12, choices=DiaSemana.choices)
    bloque = models.ForeignKey(BloqueHorario, on_delete=models.PROTECT, null=True, blank=True)
    aula = models.CharField(max_length=30, blank=True)

    class Meta:
        ordering = ["grupo", "dia", "bloque__orden"]
        unique_together = ["grupo", "dia", "bloque"]
        verbose_name = "Clase en horario"
        verbose_name_plural = "Clases en horario"

    def __str__(self):
        return f"{self.grupo} - {self.materia} - {self.dia}"
