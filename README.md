# Bienestar Estudiantil — Salud Mental y Pausas Activas

Plataforma web completa de salud mental, bienestar emocional y pausas activas para instituciones educativas.

## Requisitos

- Python 3.12+
- MySQL 8+ o MariaDB
- phpMyAdmin (opcional, para administrar BD visualmente)
- pip

## Instalación

### 1. Configurar MySQL

Crear la base de datos en phpMyAdmin o consola:

```sql
CREATE DATABASE bienestar_estudiantil;
```

O importar directamente `database/schema.sql` desde phpMyAdmin.

### 2. Configurar entorno

```bash
cd bienestar_estudiantil
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # Linux/Mac

pip install -r requirements.txt
```

### 3. Configurar variables de entorno

Copiar `.env.example` a `.env` y configurar:

```
SECRET_KEY=tu-clave-secreta
DATABASE_URL=mysql+pymysql://root:@localhost:3306/bienestar_estudiantil
JWT_SECRET_KEY=tu-clave-jwt
```

### 4. Crear tablas y cargar datos

```bash
python seed.py
```

Esto crea todas las tablas y datos de prueba automáticamente.

### 5. Iniciar servidor

```bash
python run.py
```

### 6. Abrir aplicación

```
http://localhost:5000
```

## Usuarios de prueba

| Rol | Email | Contraseña |
|-----|-------|------------|
| Administrador | admin@colegio.com | admin123 |
| Coordinador | coord@colegio.com | coord123 |
| Docente | doc1@colegio.com | doc123 |
| Profesor | prof@colegio.com | prof123 |
| Director de grupo | director@colegio.com | dir123 |
| Estudiante | est1@colegio.com | est123 |

## Estructura del proyecto

```
bienestar_estudiantil/
├── app/
│   ├── __init__.py          # App factory Flask
│   ├── config.py            # Configuración
│   ├── extensions.py        # SQLAlchemy, Migrate
│   ├── models/              # 18 modelos SQLAlchemy
│   └── routes/              # 12 blueprints API
├── templates/               # 16 archivos HTML
├── static/
│   ├── css/                 # style.css, responsive.css
│   └── js/                  # 9 archivos JavaScript
├── database/
│   └── schema.sql           # Schema para phpMyAdmin
├── seed.py                  # Datos iniciales
├── run.py                   # Punto de entrada
├── .env                     # Variables de entorno
└── README.md
```

## Módulos incluidos

- **Landing Page** pública con hero, servicios y blog
- **Login** con autenticación JWT
- **Dashboard** con estadísticas y gráficos (Chart.js)
- **CRUD Instituciones** y Sedes
- **CRUD Usuarios** con roles y paginación
- **Cursos y Estudiantes** con relación 1:N
- **Actividades** por categoría
- **Pausas Activas** con temporizador
- **Programaciones** de actividades
- **Encuestas** con preguntas, respuestas y resultados
- **Propuestas** de estudiantes
- **Alertas** con sistema de notificaciones
- **Reportes** con gráficos y exportación CSV
- **Auditoría** del sistema
- **Perfil** de usuario
- **Configuración** del sistema
- **Responsive Design** completo
- **Control de permisos** por rol en backend

## API REST

### Auth
- `POST /api/auth/login` — Iniciar sesión
- `POST /api/auth/logout` — Cerrar sesión
- `GET /api/auth/me` — Usuario actual
- `POST /api/auth/change-password` — Cambiar contraseña

### Dashboard
- `GET /api/dashboard` — Estadísticas

### CRUD Endpoints
- `GET/POST /api/usuarios` — Listar/Crear
- `PUT/DELETE /api/usuarios/<id>` — Actualizar/Eliminar
- `GET/POST /api/instituciones` — Listar/Crear
- `GET/POST /api/cursos` — Listar/Crear
- `GET/POST /api/actividades` — Listar/Crear
- `GET/POST /api/programaciones` — Listar/Crear
- `GET/POST /api/encuestas` — Listar/Crear
- `POST /api/encuestas/<id>/responder` — Responder
- `GET/POST /api/propuestas` — Listar/Crear
- `GET/POST /api/alertas` — Listar/Crear
- `GET /api/reportes` — Estadísticas
- `GET /api/reportes/exportar-csv` — Exportar CSV
- `GET /api/auditoria` — Registro de auditoría

## Solución de errores comunes

**Error de conexión MySQL:**
Verificar que MySQL esté ejecutándose y las credenciales en `.env` sean correctas.

**Error `ModuleNotFoundError`:**
Asegurar que el entorno virtual esté activado y las dependencias instaladas.

**Error de puertos:**
Si el puerto 5000 está ocupado, cambiar en `run.py` o usar `python run.py --port 8080`.

**Error de charset:**
Si hay problemas con caracteres especiales, agregar `?charset=utf8mb4` al final de la URL de conexión en `.env`.
