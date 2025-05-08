USE atopcar;

INSERT INTO tags (codigo, mac, estado, bateria, ultima_comunicacion, observaciones)
VALUES 
('T0001', 'C8:2C:2A:FF:FE:11:06:5E', 'libre', 100, NOW(), 'Tag operativo, asignado a 6A34'),
('T0002', 'C7:3C:2A:FF:FE:11:03:4A', 'libre', 100, NOW(), 'Tag operativo, asignado a FF28'),
('T0003', 'C6:4C:2A:FF:FE:11:16:2B', 'libre', 100, NOW(), 'Tag operativo, asignado a DA9C');

INSERT INTO anchors (nombre, mac, canal_rf, activo)
VALUES 
('5BA3', '34:6A:86:00:12:FF:5B:A3', '5', TRUE),
('2219', '28:FF:0C:01:7F:4E:22:19', '5', TRUE),
('234B', '9C:DA:3E:FF:FE:80:23:4B', '5', TRUE);

-- Crear taller ficticio
INSERT INTO talleres (nombre) VALUES ('Taller Central');

-- Crear zona de trabajo asociada al taller
INSERT INTO zonas (nombre, tipo, color_hex, taller_id)
VALUES ('Zona Espera', 'espera', '#FFA500', 1);

-- Crear 3 usuarios con diferentes roles
INSERT INTO usuarios (username, password_hash, nombre_completo, rol)
VALUES 
('admin1', 'hash_admin1', 'Ana Admin', 'admin'),
('recep1', 'hash_recep1', 'Rosa Recepcionista', 'recepcionista'),
('mecanico1', 'hash_mec1', 'Mario Mecanico', 'mecanico');

-- Crear vehículo y asociarlo al tag T0001
-- Asegúrate de que el ID del tag T0001 sea 1 (o ajusta si no lo es)
INSERT INTO vehiculos (matricula, bastidor, referencia, tag_id, estado)
VALUES ('1255-ABC', 'VF7N1XYZ987654123', 'Citroën C4 azul', null, 'activo');
