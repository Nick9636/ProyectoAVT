-- Autor: Adriana Nicole Guzman Ahuatzi
-- Descripción: Agrega la columna `estado` a la tabla `liga` para
--              poder marcarla como activa o inactiva.
--              Ejecutar en MySQL Workbench sobre base_datos_amivd.

ALTER TABLE `liga`
    ADD COLUMN IF NOT EXISTS `estado` varchar(10) NOT NULL DEFAULT 'activo'
        COMMENT 'Estado de la liga: activo o inactivo'
        AFTER `categoria`;

-- Todas las ligas existentes quedan activas por defecto
UPDATE `liga` SET `estado` = 'activo' WHERE `estado` IS NULL OR `estado` = '';
