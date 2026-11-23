-- Autor: Adriana Nicole Guzman Ahuatzi
-- Descripción: Agrega la columna `categoria` a la tabla `jugador`.
--              Ejecutar en MySQL Workbench sobre base_datos_amivd.
--              Solo es necesario si la migración completa (migracion_base_mod.sql)
--              no se ha ejecutado todavía.

-- Agregar categoria si no existe
ALTER TABLE `jugador`
    ADD COLUMN IF NOT EXISTS `categoria` varchar(50) DEFAULT NULL
        COMMENT 'Categoría deportiva: INFANTIL, MENOR INFANTIL, CADETE, JUVENIL, MAYOR, MASTER'
        AFTER `estatura`;

-- Verificar que quedó correctamente
SELECT COLUMN_NAME, DATA_TYPE, COLUMN_DEFAULT, IS_NULLABLE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = DATABASE()
  AND TABLE_NAME   = 'jugador'
  AND COLUMN_NAME  = 'categoria';
