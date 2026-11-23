-- Run against an existing database after migracion_base_mod.sql.
-- Adds unique registration numbers and sequential internal payment folios.

ALTER TABLE `jugador`
    ADD COLUMN IF NOT EXISTS `numero_registro` varchar(30) DEFAULT NULL;

ALTER TABLE `entrenador`
    ADD COLUMN IF NOT EXISTS `numero_registro` varchar(30) DEFAULT NULL;

ALTER TABLE `arbitro`
    ADD COLUMN IF NOT EXISTS `numero_registro` varchar(30) DEFAULT NULL;

ALTER TABLE `pago`
    ADD COLUMN IF NOT EXISTS `folio_pago` varchar(30) DEFAULT NULL
        COMMENT 'Folio interno secuencial del pago' AFTER `id_pago`;

UPDATE `pago`
SET `folio_pago` = CONCAT('PAG-', LPAD(`id_pago`, 6, '0'))
WHERE `folio_pago` IS NULL;

SET @index_exists = (
    SELECT COUNT(*) FROM information_schema.statistics
    WHERE table_schema = DATABASE() AND table_name = 'jugador'
      AND index_name = 'numero_registro' AND non_unique = 0
);
SET @index_sql = IF(@index_exists = 0,
    'ALTER TABLE `jugador` ADD UNIQUE INDEX `numero_registro` (`numero_registro`)',
    'SELECT 1');
PREPARE index_stmt FROM @index_sql;
EXECUTE index_stmt;
DEALLOCATE PREPARE index_stmt;

SET @index_exists = (
    SELECT COUNT(*) FROM information_schema.statistics
    WHERE table_schema = DATABASE() AND table_name = 'entrenador'
      AND index_name = 'numero_registro' AND non_unique = 0
);
SET @index_sql = IF(@index_exists = 0,
    'ALTER TABLE `entrenador` ADD UNIQUE INDEX `numero_registro` (`numero_registro`)',
    'SELECT 1');
PREPARE index_stmt FROM @index_sql;
EXECUTE index_stmt;
DEALLOCATE PREPARE index_stmt;

SET @index_exists = (
    SELECT COUNT(*) FROM information_schema.statistics
    WHERE table_schema = DATABASE() AND table_name = 'arbitro'
      AND index_name = 'numero_registro' AND non_unique = 0
);
SET @index_sql = IF(@index_exists = 0,
    'ALTER TABLE `arbitro` ADD UNIQUE INDEX `numero_registro` (`numero_registro`)',
    'SELECT 1');
PREPARE index_stmt FROM @index_sql;
EXECUTE index_stmt;
DEALLOCATE PREPARE index_stmt;

SET @index_exists = (
    SELECT COUNT(*) FROM information_schema.statistics
    WHERE table_schema = DATABASE() AND table_name = 'pago'
      AND index_name = 'folio_pago' AND non_unique = 0
);
SET @index_sql = IF(@index_exists = 0,
    'ALTER TABLE `pago` ADD UNIQUE INDEX `folio_pago` (`folio_pago`)',
    'SELECT 1');
PREPARE index_stmt FROM @index_sql;
EXECUTE index_stmt;
DEALLOCATE PREPARE index_stmt;
