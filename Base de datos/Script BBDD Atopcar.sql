DROP DATABASE IF EXISTS atopcar;
CREATE DATABASE IF NOT EXISTS atopcar;
USE atopcar;

-- Tabla de usuarios del sistema
CREATE TABLE usuarios (
  id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  nombre_completo VARCHAR(100),
  rol VARCHAR(20) CHECK (rol IN ('admin', 'recepcionista', 'mecanico', 'supervisor')) NOT NULL,
  activo BOOLEAN DEFAULT TRUE
);

-- Tabla de talleres
CREATE TABLE talleres (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL,
  svg_plano TEXT,
  creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de zonas dentro de un taller
CREATE TABLE zonas (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(50) NOT NULL,
  tipo VARCHAR(20) CHECK (tipo IN ('entrada', 'lavado', 'espera', 'salida', 'elevador', 'otros')),
  color_hex VARCHAR(7),
  taller_id INT REFERENCES talleres(id)
);

-- Tabla de anchors (anclas fijas)
CREATE TABLE anchors (
  id SERIAL PRIMARY KEY,
  nombre VARCHAR(50),
  mac VARCHAR(50) UNIQUE NOT NULL,
  x INT,
  y INT,
  canal_rf VARCHAR(10),
  zona_id INT REFERENCES zonas(id),
  taller_id INT REFERENCES talleres(id),
  activo BOOLEAN DEFAULT TRUE
);

-- Tabla de tags (dispositivos móviles que se asignan a vehículos)
CREATE TABLE tags (
  id SERIAL PRIMARY KEY,
  codigo VARCHAR(10) UNIQUE NOT NULL,  -- T0001, etc.
  mac VARCHAR(50) UNIQUE NOT NULL,
  estado VARCHAR(20) CHECK (estado IN ('libre', 'asignado', 'en_prueba', 'fuera_de_servicio')) NOT NULL,
  bateria INT,
  ultima_comunicacion TIMESTAMP,
  observaciones TEXT
);

-- Tabla de vehículos
CREATE TABLE vehiculos (
  id SERIAL PRIMARY KEY,
  matricula VARCHAR(20),
  bastidor VARCHAR(50) UNIQUE,
  referencia VARCHAR(100),
  tag_id INT REFERENCES tags(id),
  estado VARCHAR(20) CHECK (estado IN ('activo', 'entregado', 'baja')) DEFAULT 'activo'
);

-- Tabla de posiciones (histórico de ubicaciones)
CREATE TABLE posiciones (
  id SERIAL PRIMARY KEY,
  tag_id INT REFERENCES tags(id),
  x INT NOT NULL,
  y INT NOT NULL,
  zona_id INT REFERENCES zonas(id),
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabla de distancias desde un tag a 3 anchors (última medida)
CREATE TABLE distancias (
  id SERIAL PRIMARY KEY,
  tag_id INT UNIQUE REFERENCES tags(id),
  anchor1_id INT REFERENCES anchors(id),
  anchor1_dist FLOAT,
  anchor2_id  INT REFERENCES anchors(id),
  anchor2_dist FLOAT,
  anchor3_id  INT REFERENCES anchors(id),
  anchor3_dist FLOAT
);

-- Tabla de alertas
CREATE TABLE alertas (
  id SERIAL PRIMARY KEY,
  tag_id INT REFERENCES tags(id),
  vehiculo_id INT REFERENCES vehiculos(id),
  tipo VARCHAR(30) CHECK (tipo IN ('desconexion', 'bateria_baja', 'fuera_de_area', 'otros')),
  descripcion TEXT,
  timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  leido BOOLEAN DEFAULT FALSE
);
