# Modelo de datos propuesto

## Problema central

El director cambia de escuela cada varios anos, pero necesita conservar historico de alumnos, docentes, grupos y horarios por institucion y ciclo escolar.

## Solucion en tablas

- `Institucion`: guarda escuelas como Ricardo Flores Magon o Fernando Moreno Pena.
- `CicloEscolar`: separa ciclos como 2025-2026 por institucion.
- `Periodo`: cada ciclo tiene tres periodos.
- `Docente`: datos unicos del profesor, sin duplicarlo por materia o escuela.
- `ContratoDocente`: une docente, institucion y ciclo, con sus horas semanales.
- `Materia`: catalogo por grado y por institucion, sin duplicar por profesor.
- `AsignacionDocenteMateria`: indica que un profesor da una materia a ciertos grupos.
- `Grupo`: grupos variables por ciclo, por ejemplo 1A, 1B, 2A o 3E.
- `Alumno`: alumno ligado a institucion.
- `Inscripcion`: coloca al alumno en un grupo y ciclo.
- `BloqueHorario`: horas del dia, incluyendo receso.
- `DisponibilidadDocente`: dias y horas en que el docente puede trabajar.
- `FichaAsignacion`: tarjeta visual que se puede arrastrar al tablero.
- `HorarioClase`: clase ya colocada en un dia, bloque, grupo, aula y docente.

## Ventaja

Si el director cambia de escuela, se crea otra `Institucion` y otro `CicloEscolar`. El sistema mantiene el historial anterior sin mezclar alumnos, grupos ni horarios.

## Escuela seleccionada

La barra superior permite seleccionar la escuela activa. Las pantallas de alumnos, docentes, grupos, materias, horarios y tablero usan esa escuela como contexto, para evitar mezclar informacion entre instituciones.
