# Sistema de Base de Datos para Escuela Secundaria

Cascaron inicial para un sistema escolar con login, Django, PostgreSQL, Docker, JavaScript, templates y archivos estaticos.

La idea principal es que el director pueda cambiar de institucion cada cierto tiempo sin perder el historial. Por eso la informacion se organiza por institucion, ciclo escolar y tres periodos.

## Estructura

- `apps/usuarios`: login, logout y perfil inicial.
- `apps/escuela`: instituciones, ciclos, periodos, alumnos, docentes, contratos, grupos, materias e inscripciones.
- `apps/horarios`: bloques de hora, disponibilidad docente, fichas arrastrables y clases colocadas.
- `templates/`: vistas HTML organizadas por ventana/modulo.
- `static/`: CSS y JavaScript del sistema.
- `BaseDeDatos/`: SQL inicial para PostgreSQL.
- `secundaria/`: configuracion principal del proyecto Django.

## Levantar el proyecto

```bash
docker compose up --build
```

Despues abre:

```text
http://localhost:8000
```

Usuario inicial:

```text
admin
admin12345
```

El arranque tambien crea datos demo:

- Institucion: Ricardo Flores Magon.
- Ciclo activo: 2025-2026.
- Periodos: 1, 2 y 3.
- Grupos: 1A a 3E.
- Bloques de horario de 07:00 a 13:10 con receso.

## Flujo recomendado

1. Crear o seleccionar institucion.
2. Crear ciclo escolar, por ejemplo `2025-2026`.
3. Crear sus tres periodos.
4. Registrar profesores y su contrato por ciclo con horas semanales.
5. Registrar materias por grado sin duplicar profesores.
6. Relacionar profesor, materia y grupos mediante asignaciones.
7. Generar fichas y arrastrarlas en el tablero de horarios.
8. Imprimir horarios por grupo, grado o profesor.

## Comandos utiles

```bash
docker compose run --rm web python manage.py makemigrations
docker compose run --rm web python manage.py migrate
docker compose run --rm web python manage.py createsuperuser
```
