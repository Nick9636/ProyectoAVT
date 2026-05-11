-- Autor: Adriana Nicole Guzman Ahuatzi
-- Descripción: Agrega la columna `estado` a la tabla `equipo`.
--              Ejecutar en MySQL Workbench sobre base_datos_amivd.

ALTER TABLE `equipo`
    ADD COLUMN IF NOT EXISTS `estado` varchar(10) NOT NULL DEFAULT 'activo'
        COMMENT 'Estado del equipo: activo o inactivo'
        AFTER `categoria`;

-- Todos los equipos existentes quedan activos por defecto
UPDATE `equipo` SET `estado` = 'activo' WHERE `estado` IS NULL OR `estado` = '';
