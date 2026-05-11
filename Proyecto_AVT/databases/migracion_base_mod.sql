-- ══════════════════════════════════════════════════════════════
-- MIGRACIÓN: Actualizar base_datos_amivd según base_mod.sql
-- Autor: Adriana Nicole Guzman Ahuatzi
-- Descripción: Aplica los cambios necesarios a la BD existente
--              sin borrar datos. Ejecutar en MySQL Workbench.
-- ══════════════════════════════════════════════════════════════

SET FOREIGN_KEY_CHECKS = 0;

-- ──────────────────────────────────────────────────────────────
-- 1. TABLA jugador
--    - Cambiar enfermedades_cronicas de tinyint a varchar(200)
--    - Cambiar id_tipo_sangre (FK) a tipo_sangre varchar(5)
--    - Agregar columnas faltantes: numero_registro, vigencia,
--      categoria, rama, club, ligas_participa
-- ──────────────────────────────────────────────────────────────

-- Eliminar FK de tipo_sangre si existe
ALTER TABLE `jugador`
    DROP FOREIGN KEY IF EXISTS `jugador_id_tipo_sangre_foreign`;

-- Cambiar enfermedades_cronicas: tinyint(1) → varchar(200)
ALTER TABLE `jugador`
    MODIFY COLUMN `enfermedades_cronicas` varchar(200) DEFAULT 'NINGUNA'
        COMMENT 'Texto libre: NINGUNA o descripción de la enfermedad';

-- Cambiar medicamentos: text → varchar(200) para consistencia
ALTER TABLE `jugador`
    MODIFY COLUMN `medicamentos` varchar(200) DEFAULT 'NINGUNA';

-- Reemplazar id_tipo_sangre (FK) por tipo_sangre (texto directo)
ALTER TABLE `jugador`
    ADD COLUMN `tipo_sangre` varchar(5) DEFAULT NULL
        COMMENT 'Tipo de sangre: O+, O-, A+, A-, B+, B-, AB+, AB-'
        AFTER `estatura`;

-- Migrar datos existentes de id_tipo_sangre a tipo_sangre
UPDATE `jugador` j
JOIN `cat_tipo_sangre` ts ON ts.id_tipo_sangre = j.id_tipo_sangre
SET j.tipo_sangre = ts.descripcion
WHERE j.id_tipo_sangre IS NOT NULL;

-- Eliminar columna id_tipo_sangre (ya no se necesita)
ALTER TABLE `jugador`
    DROP COLUMN IF EXISTS `id_tipo_sangre`;

-- Agregar columnas deportivas faltantes
ALTER TABLE `jugador`
    ADD COLUMN IF NOT EXISTS `numero_registro` varchar(30) DEFAULT NULL
        COMMENT 'Número de registro del jugador' AFTER `nombres`,
    ADD COLUMN IF NOT EXISTS `vigencia` varchar(50) DEFAULT NULL
        COMMENT 'Año(s) de vigencia' AFTER `curp`,
    ADD COLUMN IF NOT EXISTS `categoria` varchar(50) DEFAULT NULL
        COMMENT 'Categoría deportiva' AFTER `tipo_sangre`,
    ADD COLUMN IF NOT EXISTS `rama` varchar(20) DEFAULT NULL
        COMMENT 'Varonil, Femenil, Mixto' AFTER `categoria`,
    ADD COLUMN IF NOT EXISTS `club` varchar(150) DEFAULT NULL
        COMMENT 'Club o escuela deportiva' AFTER `rama`,
    ADD COLUMN IF NOT EXISTS `ligas_participa` varchar(255) DEFAULT NULL
        COMMENT 'Ligas en las que participa' AFTER `club`;

-- ──────────────────────────────────────────────────────────────
-- 2. TABLA entrenador — agregar si no existe
-- ──────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS `entrenador` (
  `id_entrenador`        bigint NOT NULL AUTO_INCREMENT,
  `id_equipo`            bigint DEFAULT NULL,
  `id_direccion`         bigint DEFAULT NULL,
  `apellido_paterno`     varchar(80) NOT NULL,
  `apellido_materno`     varchar(80) NOT NULL,
  `nombres`              varchar(100) NOT NULL,
  `numero_registro`      varchar(30) DEFAULT NULL,
  `curp`                 varchar(18) NOT NULL,
  `vigencia`             varchar(50) DEFAULT NULL,
  `fecha_nacimiento`     date NOT NULL,
  `lugar_nacimiento`     varchar(100) DEFAULT NULL,
  `nacionalidad`         varchar(50) DEFAULT 'MEXICANA',
  `peso`                 decimal(5,2) DEFAULT NULL,
  `estatura`             decimal(4,2) DEFAULT NULL,
  `tipo_sangre`          varchar(5) DEFAULT NULL,
  `ocupacion`            varchar(100) DEFAULT NULL,
  `escolaridad`          varchar(100) DEFAULT NULL,
  `escuela`              varchar(150) DEFAULT NULL,
  `telefono`             varchar(20) DEFAULT NULL,
  `celular`              varchar(20) DEFAULT NULL,
  `correo_electronico`   varchar(150) DEFAULT NULL,
  `enfermedades_cronicas` varchar(200) DEFAULT 'NINGUNA',
  `medicamentos`         varchar(200) DEFAULT 'NINGUNA',
  `club`                 varchar(150) DEFAULT NULL,
  `categoria`            varchar(50) DEFAULT NULL,
  `rama`                 varchar(20) DEFAULT NULL,
  `ligas_participa`      varchar(255) DEFAULT NULL,
  `cedula`               varchar(50) DEFAULT NULL,
  `especialidad`         varchar(100) DEFAULT NULL,
  `fotografia`           varchar(500) DEFAULT NULL,
  `fecha_registro`       datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_entrenador`),
  UNIQUE KEY `curp` (`curp`),
  KEY `id_equipo` (`id_equipo`),
  KEY `id_direccion` (`id_direccion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ──────────────────────────────────────────────────────────────
-- 3. TABLA arbitro — agregar si no existe
-- ──────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS `arbitro` (
  `id_arbitro`           bigint NOT NULL AUTO_INCREMENT,
  `id_equipo`            bigint DEFAULT NULL,
  `id_direccion`         bigint DEFAULT NULL,
  `apellido_paterno`     varchar(80) NOT NULL,
  `apellido_materno`     varchar(80) NOT NULL,
  `nombres`              varchar(100) NOT NULL,
  `numero_registro`      varchar(30) DEFAULT NULL,
  `curp`                 char(18) NOT NULL,
  `vigencia`             varchar(50) DEFAULT NULL,
  `fecha_nacimiento`     date NOT NULL,
  `lugar_nacimiento`     varchar(100) DEFAULT NULL,
  `nacionalidad`         varchar(50) DEFAULT 'MEXICANA',
  `peso`                 decimal(5,2) DEFAULT NULL,
  `estatura`             decimal(4,2) DEFAULT NULL,
  `tipo_sangre`          varchar(5) DEFAULT NULL,
  `ocupacion`            varchar(100) DEFAULT NULL,
  `escolaridad`          varchar(100) DEFAULT NULL,
  `escuela`              varchar(150) DEFAULT NULL,
  `telefono`             varchar(20) DEFAULT NULL,
  `celular`              varchar(20) DEFAULT NULL,
  `correo_electronico`   varchar(150) DEFAULT NULL,
  `enfermedades_cronicas` varchar(200) DEFAULT 'NINGUNA',
  `medicamentos`         varchar(200) DEFAULT 'NINGUNA',
  `club`                 varchar(150) DEFAULT NULL,
  `categoria`            varchar(50) DEFAULT NULL,
  `rama`                 varchar(20) DEFAULT NULL,
  `zona`                 varchar(100) DEFAULT NULL,
  `licencia`             varchar(50) DEFAULT NULL,
  `ligas_participa`      varchar(255) DEFAULT NULL,
  `fotografia`           varchar(500) DEFAULT NULL,
  `fecha_registro`       datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_arbitro`),
  UNIQUE KEY `curp` (`curp`),
  KEY `id_equipo` (`id_equipo`),
  KEY `id_direccion` (`id_direccion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ──────────────────────────────────────────────────────────────
-- 4. TABLA equipo — agregar si no existe
-- ──────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS `equipo` (
  `id_equipo`     bigint NOT NULL AUTO_INCREMENT,
  `id_liga`       bigint NOT NULL,
  `nombre_equipo` varchar(150) NOT NULL,
  `categoria`     varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_equipo`),
  KEY `id_liga` (`id_liga`),
  CONSTRAINT `equipo_ibfk_1` FOREIGN KEY (`id_liga`) REFERENCES `liga` (`id_liga`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ──────────────────────────────────────────────────────────────
-- 5. TABLA direccion
--    Agregar columna nombre_municipio para guardar el nombre
--    además del id, con FK opcional a cat_municipio
-- ──────────────────────────────────────────────────────────────

ALTER TABLE `direccion`
    ADD COLUMN IF NOT EXISTS `nombre_municipio` varchar(100) DEFAULT NULL
        COMMENT 'Nombre del municipio (texto). Si existe en cat_municipio se enlaza por id_municipio'
        AFTER `id_municipio`;

-- Poblar nombre_municipio con datos existentes de cat_municipio
UPDATE `direccion` d
JOIN `cat_municipio` m ON m.id_municipio = d.id_municipio
SET d.nombre_municipio = m.nombre
WHERE d.nombre_municipio IS NULL;

-- ──────────────────────────────────────────────────────────────
-- 6. TABLA usuario — ampliar enum de rol
-- ──────────────────────────────────────────────────────────────

ALTER TABLE `usuario`
    MODIFY COLUMN `rol` enum('Presidente','Secretaria','Administrador','Delegado') DEFAULT NULL;

-- ──────────────────────────────────────────────────────────────
-- 7. TABLA autorizacion_pendiente — agregar columnas de base_mod
-- ──────────────────────────────────────────────────────────────

ALTER TABLE `autorizacion_pendiente`
    ADD COLUMN IF NOT EXISTS `email_solicitante`      varchar(150) DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS `nombre_solicitante`     varchar(150) DEFAULT NULL,
    ADD COLUMN IF NOT EXISTS `id_usuario_autorizador` bigint DEFAULT NULL;

-- ──────────────────────────────────────────────────────────────
-- 8. TABLA tutor_padre — agregar si no existe
-- ──────────────────────────────────────────────────────────────

CREATE TABLE IF NOT EXISTS `tutor_padre` (
  `id_tutor`           bigint NOT NULL AUTO_INCREMENT,
  `id_jugador`         bigint DEFAULT NULL,
  `nombre_completo`    varchar(150) DEFAULT NULL,
  `celular`            varchar(20) DEFAULT NULL,
  `correo_electronico` varchar(150) DEFAULT NULL,
  `curp_tutor`         varchar(18) DEFAULT NULL,
  `fotografia_ine`     varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_tutor`),
  KEY `id_jugador` (`id_jugador`),
  CONSTRAINT `tutor_padre_ibfk_1` FOREIGN KEY (`id_jugador`) REFERENCES `jugador` (`id_jugador`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ──────────────────────────────────────────────────────────────
-- 9. Datos de cat_municipio si está vacía
-- ──────────────────────────────────────────────────────────────

INSERT IGNORE INTO `cat_estado` (`id_estado`, `nombre`) VALUES
  (1,'Puebla'),(2,'Ciudad de México'),(3,'Veracruz'),(4,'Tlaxcala'),(5,'Hidalgo');

INSERT IGNORE INTO `cat_municipio` (`id_municipio`, `id_estado`, `nombre`) VALUES
  (1,1,'Puebla'),(2,1,'Cholula'),(3,1,'Atlixco'),(4,1,'Tehuacán'),
  (5,2,'Benito Juárez'),(6,2,'Coyoacán'),
  (7,3,'Veracruz'),
  (8,4,'Tlaxcala'),
  (9,5,'Pachuca');

SET FOREIGN_KEY_CHECKS = 1;
