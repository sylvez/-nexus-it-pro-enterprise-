CREATE DATABASE IF NOT EXISTS nexus_it_enterprise CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE nexus_it_enterprise;

-- 1. Tabla de Activos de TI (Inventario de equipos de la empresa)
CREATE TABLE activos_ti (
    id INT AUTO_INCREMENT PRIMARY KEY,
    codigo_patrimonial VARCHAR(30) UNIQUE NOT NULL,
    equipo VARCHAR(100) NOT NULL,
    ubicacion VARCHAR(100) NOT NULL,
    estado ENUM('Operativo', 'En Reparación', 'De Baja') DEFAULT 'Operativo',
    actualizado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- 2. Tabla de Tickets de Soporte (Helpdesk)
CREATE TABLE tickets (
    id INT AUTO_INCREMENT PRIMARY KEY,
    titulo VARCHAR(150) NOT NULL,
    descripcion TEXT NOT NULL,
    solicitante VARCHAR(100) NOT NULL,
    prioridad ENUM('Baja', 'Media', 'Alta', 'Crítica') NOT NULL,
    estado ENUM('Abierto', 'En Proceso', 'Resuelto') DEFAULT 'Abierto',
    diagnostico_ia TEXT,
    creado_en TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 3. Tabla de Bitácora de Auditoría (Inmutable para seguridad empresarial)
CREATE TABLE bitacora_auditoria (
    id INT AUTO_INCREMENT PRIMARY KEY,
    tabla_afectada VARCHAR(50) NOT NULL,
    registro_id INT NOT NULL,
    accion VARCHAR(30) NOT NULL,
    detalle_cambio TEXT NOT NULL,
    fecha_evento TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 4. TRIGGERS AUTOMÁTICOS DE AUDITORÍA
DELIMITER //

CREATE TRIGGER trg_ticket_insert
AFTER INSERT ON tickets
FOR EACH ROW
BEGIN
    INSERT INTO bitacora_auditoria (tabla_afectada, registro_id, accion, detalle_cambio)
    VALUES ('tickets', NEW.id, 'CREACIÓN', CONCAT('Ticket creado por ', NEW.solicitante, ' | Prioridad: ', NEW.prioridad));
END //

CREATE TRIGGER trg_ticket_update
AFTER UPDATE ON tickets
FOR EACH ROW
BEGIN
    IF OLD.estado != NEW.estado THEN
        INSERT INTO bitacora_auditoria (tabla_afectada, registro_id, accion, detalle_cambio)
        VALUES ('tickets', NEW.id, 'CAMBIO_ESTADO', CONCAT('Ticket #', NEW.id, ' pasó de [', OLD.estado, '] a [', NEW.estado, ']'));
    END IF;
END //

DELIMITER ;

-- 5. DATOS DE PRUEBA (Para que el sistema se vea lleno desde el inicio)
INSERT INTO activos_ti (codigo_patrimonial, equipo, ubicacion, estado) VALUES
('SRV-GT-001', 'Servidor Dell PowerEdge R740', 'Data Center Principal', 'Operativo'),
('NET-GT-014', 'Nodo Mesh TP-Link Deco X50', 'Laboratorio de Sistemas 2', 'Operativo'),
('PRT-GT-008', 'Impresora Canon G2070 Red', 'Oficina de Administración', 'En Reparación'),
('WKS-GT-045', 'Workstation HP ProDesk + Monitor 120Hz', 'Coordinación Académica', 'Operativo');

INSERT INTO tickets (titulo, descripcion, solicitante, prioridad, estado, diagnostico_ia) VALUES
('Caída de enlace en base de datos local', 'El servidor rechaza conexiones desde las terminales del laboratorio 2 por error de puerto 3306.', 'Carlos Méndez (Docente)', 'Crítica', 'En Proceso', '1. Verificar servicio MySQL activo.\n2. Revisar regla de Firewall en puerto TCP 3306.\n3. Confirmar permisos de host remoto en usuario root/app.'),
('Impresora de administración no imprime en red', 'La Canon G2070 aparece desconectada aunque está encendida y conectada al Wi-Fi.', 'Ana Lucía Gómez (Contabilidad)', 'Media', 'Abierto', '1. Imprimir hoja de configuración de red para verificar IP actual.\n2. Asignar IP estática por MAC en el router principal.\n3. Reiniciar cola de impresión (Spooler) en Windows.'),
('Solicitud de instalación de entorno Docker', 'Se requiere configurar Docker Desktop y WSL2 en el equipo de coordinación.', 'Ing. Roberto Morales', 'Baja', 'Resuelto', '1. Habilitar virtualización en BIOS.\n2. Ejecutar wsl --install en PowerShell como Administrador.\n3. Instalar motor Docker y validar permisos de grupo.');


DELIMITER //

CREATE TRIGGER trg_activo_insert
AFTER INSERT ON activos_ti
FOR EACH ROW
BEGIN
    INSERT INTO bitacora_auditoria (tabla_afectada, registro_id, accion, detalle_cambio)
    VALUES ('activos_ti', NEW.id, 'ALTA_ACTIVO', CONCAT('Equipo registrado: ', NEW.codigo_patrimonial, ' (', NEW.equipo, ') en ', NEW.ubicacion));
END //

CREATE TRIGGER trg_activo_update
AFTER UPDATE ON activos_ti
FOR EACH ROW
BEGIN
    IF OLD.estado != NEW.estado THEN
        INSERT INTO bitacora_auditoria (tabla_afectada, registro_id, accion, detalle_cambio)
        VALUES ('activos_ti', NEW.id, 'ESTADO_ACTIVO', CONCAT('Equipo ', NEW.codigo_patrimonial, ' pasó de [', OLD.estado, '] a [', NEW.estado, ']'));
    END IF;
END //

DELIMITER ;