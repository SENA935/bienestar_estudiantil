# Bienestar Estudiantil

Plataforma web institucional de bienestar estudiantil para el SENA. Gestiona actividades de bienestar, encuestas, propuestas, alertas y reportes.

## Requisitos

- Python 3.12+
- PostgreSQL 14+
- pip

## Instalación

### 1. Instalar PostgreSQL

Descargar e instalar PostgreSQL desde https://www.postgresql.org/download/

### 2. Crear base de datos

```sql
CREATE DATABASE bienestar_estudiantil;
```

O ejecutar desde consola:
```bash
psql -U postgres -c "CREATE DATABASE bienestar_estudiantil;"
```

### 3. Clonar el proyecto

```bash
cd bienestar_estudiantil
```

### 4. Crear entorno virtual

```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac
```

### 5. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 6. Configurar variables de entorno

Copiar `.env.example` a `.env` y configurar:

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/bienestar_estudiantil
SECRET_KEY=tu-clave-secreta-aqui
JWT_SECRET_KEY=tu-jwt-secreto-aqui
```

### 7. Crear tablas y datos iniciales

```bash
python seed.py
```

### 8. Iniciar servidor

```bash
python run.py
```

### 9. Abrir aplicación

Visitar: http://localhost:5000

## Credenciales de prueba

| Usuario | Contraseña | Rol |
|---------|-----------|-----|
| admin | admin123 | Administrador |
| coordinador | coord123 | Coordinador |
| docente1 | doc123 | Docente |
| docente2 | doc123 | Docente |
| est1 | est123 | Estudiante |
| est2 | est123 | Estudiante |

## Estructura del proyecto

```
bienestar_estudiantil/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   ├── extensions.py
│   │   ├── models/
│   │   └── routes/
│   ├── run.py
│   ├── seed.py
│   └── requirements.txt
├── frontend/
│   ├── templates/
│   └── static/
│       ├── css/
│       └── js/
├── database/
├── .env
└── README.md
```

## API disponible

### Autenticación
- `POST /api/auth/login` - Iniciar sesión
- `POST /api/auth/logout` - Cerrar sesión
- `GET /api/auth/me` - Usuario actual

### Dashboard
- `GET /api/dashboard` - Datos del dashboard

### Usuarios
- `GET /api/usuarios` - Listar usuarios (paginado)
- `POST /api/usuarios` - Crear usuario
- `PUT /api/usuarios/:id` - Actualizar usuario
- `DELETE /api/usuarios/:id` - Eliminar usuario
- `PUT /api/usuarios/:id/toggle` - Activar/desactivar

### Instituciones
- `GET /api/instituciones` - Listar
- `POST /api/instituciones` - Crear
- `PUT /api/instituciones/:id` - Actualizar
- `DELETE /api/instituciones/:id` - Eliminar
- `GET /api/instituciones/:id/sedes` - Sedes
- `POST /api/instituciones/:id/sedes` - Crear sede

### Cursos
- `GET /api/cursos` - Listar
- `POST /api/cursos` - Crear
- `PUT /api/cursos/:id` - Actualizar
- `DELETE /api/cursos/:id` - Eliminar
- `GET /api/cursos/:id/estudiantes` - Estudiantes del curso
- `POST /api/cursos/:id/estudiantes` - Agregar estudiante

### Actividades
- `GET /api/actividades` - Listar (paginado)
- `POST /api/actividades` - Crear
- `PUT /api/actividades/:id` - Actualizar
- `DELETE /api/actividades/:id` - Eliminar
- `GET /api/actividades/all` - Todas las activas

### Programaciones
- `GET /api/programaciones` - Listar (paginado)
- `POST /api/programaciones` - Crear
- `PUT /api/programaciones/:id` - Actualizar
- `DELETE /api/programaciones/:id` - Eliminar

### Encuestas
- `GET /api/encuestas` - Listar
- `POST /api/encuestas` - Crear
- `GET /api/encuestas/:id` - Detalle con preguntas
- `PUT /api/encuestas/:id` - Actualizar
- `DELETE /api/encuestas/:id` - Eliminar
- `POST /api/encuestas/:id/responder` - Responder encuesta
- `GET /api/encuestas/:id/resultados` - Ver resultados

### Propuestas
- `GET /api/propuestas` - Listar
- `POST /api/propuestas` - Crear
- `PUT /api/propuestas/:id` - Actualizar estado

### Alertas
- `GET /api/alertas` - Listar
- `PUT /api/alertas/:id/leer` - Marcar como leída
- `PUT /api/alertas/leer-todas` - Marcar todas

### Reportes
- `GET /api/reportes` - Estadísticas con filtros

### Auditoría
- `GET /api/auditoria` - Registro de auditoría

### Perfil
- `GET /api/perfil` - Ver perfil
- `PUT /api/perfil` - Actualizar perfil
- `PUT /api/perfil/cambiar-password` - Cambiar contraseña

### Configuración
- `GET /api/configuracion/periodos` - Periodos académicos
- `POST /api/configuracion/periodos` - Crear periodo
- `GET /api/configuracion/categorias` - Categorías
- `POST /api/configuracion/categorias` - Crear categoría
- `GET /api/configuracion/roles` - Roles

## Despliegue en Render

El repositorio incluye `render.yaml` (Blueprint). Opciones:

1. **Desde el dashboard (recomendado):** New → Web Service → conectar el repo de GitHub.
   - Build command: `pip install -r backend/requirements.txt`
   - Start command: `cd backend && gunicorn run:app`
   - Predeploy: ejecutar `cd backend && python provision.py` (crea tablas y datos si están vacíos)
   - Variables de entorno: `SECRET_KEY`, `JWT_SECRET_KEY`, `DATABASE_URL`
   - Crear una base de datos **PostgreSQL** en Render y usar su `connection string` en `DATABASE_URL`.

2. **Con Blueprint:** subir el repo y en Render → New → Blueprint → elegir el repo. Render usará `render.yaml` automáticamente (crea el servicio web + la base de datos PostgreSQL).

## Tecnologías

- **Backend:** Python, Flask, SQLAlchemy, Flask-JWT-Extended
- **Frontend:** HTML5, CSS3, JavaScript ES6+, Chart.js, Font Awesome
- **Base de datos:** PostgreSQL
- **Autenticación:** JWT (JSON Web Tokens)
