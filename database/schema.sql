CREATE DATABASE IF NOT EXISTS bienestar_estudiantil;
USE bienestar_estudiantil;

CREATE TABLE roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) UNIQUE NOT NULL,
    descripcion VARCHAR(200)
) ENGINE=InnoDB;

CREATE TABLE instituciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    nit VARCHAR(20) UNIQUE,
    telefono VARCHAR(20),
    email VARCHAR(120),
    estado VARCHAR(20) DEFAULT 'Activa',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE sedes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(200) NOT NULL,
    direccion VARCHAR(300),
    institucion_id INT NOT NULL,
    telefono VARCHAR(20),
    estado VARCHAR(20) DEFAULT 'Activa',
    FOREIGN KEY (institucion_id) REFERENCES instituciones(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE usuarios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    rol_id INT NOT NULL,
    institucion_id INT,
    estado VARCHAR(20) DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (rol_id) REFERENCES roles(id),
    FOREIGN KEY (institucion_id) REFERENCES instituciones(id)
) ENGINE=InnoDB;

CREATE TABLE cursos (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    grado VARCHAR(20) NOT NULL,
    jornada VARCHAR(30) DEFAULT 'Mañana',
    director_grupo VARCHAR(100),
    estado VARCHAR(20) DEFAULT 'Activo',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE estudiantes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    apellido VARCHAR(100) NOT NULL,
    documento VARCHAR(20) UNIQUE NOT NULL,
    curso_id INT NOT NULL,
    estado VARCHAR(20) DEFAULT 'Activo',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (curso_id) REFERENCES cursos(id)
) ENGINE=InnoDB;

CREATE TABLE categorias_actividad (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) UNIQUE NOT NULL,
    descripcion VARCHAR(200),
    color VARCHAR(20) DEFAULT '#087f8c'
) ENGINE=InnoDB;

CREATE TABLE actividades (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    categoria_id INT NOT NULL,
    duracion INT DEFAULT 30,
    instrucciones TEXT,
    imagen VARCHAR(255),
    estado VARCHAR(20) DEFAULT 'Activa',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (categoria_id) REFERENCES categorias_actividad(id)
) ENGINE=InnoDB;

CREATE TABLE programaciones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    actividad_id INT NOT NULL,
    curso_id INT NOT NULL,
    docente_id INT,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_final TIME,
    lugar VARCHAR(200),
    estado VARCHAR(20) DEFAULT 'Programada',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (actividad_id) REFERENCES actividades(id),
    FOREIGN KEY (curso_id) REFERENCES cursos(id),
    FOREIGN KEY (docente_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

CREATE TABLE actividades_realizadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    programacion_id INT NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME,
    hora_final TIME,
    observaciones TEXT,
    estado VARCHAR(20) DEFAULT 'Realizada',
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (programacion_id) REFERENCES programaciones(id)
) ENGINE=InnoDB;

CREATE TABLE encuestas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    estado VARCHAR(20) DEFAULT 'Activa',
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

CREATE TABLE preguntas_encuesta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    encuesta_id INT NOT NULL,
    texto TEXT NOT NULL,
    tipo VARCHAR(30) NOT NULL,
    orden INT DEFAULT 0,
    requerida BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (encuesta_id) REFERENCES encuestas(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE opciones_pregunta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pregunta_id INT NOT NULL,
    texto VARCHAR(300) NOT NULL,
    valor INT,
    orden INT DEFAULT 0,
    FOREIGN KEY (pregunta_id) REFERENCES preguntas_encuesta(id) ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE TABLE respuestas_encuesta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    encuesta_id INT NOT NULL,
    usuario_id INT NOT NULL,
    fecha_respuesta TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (encuesta_id) REFERENCES encuestas(id),
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

CREATE TABLE respuestas_pregunta (
    id INT AUTO_INCREMENT PRIMARY KEY,
    respuesta_encuesta_id INT NOT NULL,
    pregunta_id INT NOT NULL,
    opcion_id INT,
    valor_texto TEXT,
    valor_numero FLOAT,
    FOREIGN KEY (respuesta_encuesta_id) REFERENCES respuestas_encuesta(id) ON DELETE CASCADE,
    FOREIGN KEY (pregunta_id) REFERENCES preguntas_encuesta(id),
    FOREIGN KEY (opcion_id) REFERENCES opciones_pregunta(id)
) ENGINE=InnoDB;

CREATE TABLE propuestas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT NOT NULL,
    estudiante_id INT NOT NULL,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    estado VARCHAR(20) DEFAULT 'Pendiente',
    observaciones_coordinador TEXT,
    FOREIGN KEY (estudiante_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

CREATE TABLE alertas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(200) NOT NULL,
    descripcion TEXT,
    tipo VARCHAR(50) NOT NULL,
    usuario_id INT NOT NULL,
    leida BOOLEAN DEFAULT FALSE,
    fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

CREATE TABLE auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id INT,
    modulo VARCHAR(50) NOT NULL,
    accion VARCHAR(50) NOT NULL,
    descripcion TEXT,
    ip_address VARCHAR(45),
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
) ENGINE=InnoDB;

CREATE INDEX idx_usuarios_email ON usuarios(email);
CREATE INDEX idx_usuarios_username ON usuarios(username);
CREATE INDEX idx_programaciones_fecha ON programaciones(fecha);
CREATE INDEX idx_alertas_usuario ON alertas(usuario_id, leida);
CREATE INDEX idx_auditoria_fecha ON auditoria(fecha);
