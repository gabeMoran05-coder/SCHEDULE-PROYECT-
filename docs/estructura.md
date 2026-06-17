# Estructura del sistema

El proyecto esta separado por aplicaciones Django dentro de `apps/` y por vistas HTML dentro de `templates/`.

## Modulos iniciales

- Usuarios: autenticacion y perfil.
- Escuela: instituciones, ciclos, periodos, alumnos, docentes, contratos, grupos, materias e inscripciones.
- Horarios: bloques, disponibilidad docente, fichas arrastrables y asignacion de clases por grupo.

## Siguiente crecimiento recomendado

- Agregar app `calificaciones`.
- Agregar app `asistencias`.
- Agregar app `reportes`.
- Agregar permisos por rol: administrador, coordinador, docente y alumno.
- Guardar movimientos del tablero por AJAX para persistir cada arrastre.
- Exportar horarios a Excel con `openpyxl`.
