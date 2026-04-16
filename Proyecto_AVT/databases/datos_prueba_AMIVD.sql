-- ============================================================
-- DATOS DE PRUEBA - base_datos_amivd
-- 30 registros reales para verificar el funcionamiento
-- ============================================================

USE base_datos_amivd;

SET FOREIGN_KEY_CHECKS = 0;

-- ------------------------------------------------------------
-- 1. cat_tipo_sangre (catálogo)
-- ------------------------------------------------------------
INSERT INTO `cat_tipo_sangre` (`descripcion`) VALUES
('A+'), ('A-'), ('B+'), ('B-'), ('AB+'), ('AB-'), ('O+'), ('O-');

-- ------------------------------------------------------------
-- 2. cat_estado (catálogo)
-- ------------------------------------------------------------
INSERT INTO `cat_estado` (`nombre`) VALUES
('Puebla'), ('Ciudad de México'), ('Veracruz'), ('Tlaxcala'), ('Hidalgo');

-- ------------------------------------------------------------
-- 3. cat_municipio (catálogo)
-- ------------------------------------------------------------
INSERT INTO `cat_municipio` (`id_estado`, `nombre`) VALUES
(1, 'Puebla'),
(1, 'Cholula'),
(1, 'Atlixco'),
(1, 'Tehuacán'),
(2, 'Benito Juárez'),
(2, 'Coyoacán'),
(3, 'Veracruz'),
(4, 'Tlaxcala'),
(5, 'Pachuca');

-- ------------------------------------------------------------
-- 4. vigencias (catálogo)
-- ------------------------------------------------------------
INSERT INTO `vigencias` (`descripcion`) VALUES
('Anual'),
('Semestral');

-- ------------------------------------------------------------
-- 5. liga
-- ------------------------------------------------------------
INSERT INTO `liga` (`nombre_liga`, `categoria`) VALUES
('Liga AMIVD Puebla', 'Primera Fuerza'),
('Liga AMIVD Cholula', 'Juvenil'),
('Liga AMIVD Atlixco', 'Veteranos');

-- ------------------------------------------------------------
-- 6. club
-- ------------------------------------------------------------
INSERT INTO `club` (`id_liga`, `nombre_club`, `nombre_equipo`, `categoria`, `rama`) VALUES
(1, 'Club Volcanes', 'Volcanes FC', 'Primera Fuerza', 'Varonil'),
(1, 'Club Estrellas Puebla', 'Estrellas Femenil', 'Primera Fuerza', 'Femenil'),
(2, 'Club Pirámides', 'Pirámides Juvenil', 'Juvenil', 'Varonil'),
(2, 'Club San Andrés', 'San Andrés Mixto', 'Juvenil', 'Mixto'),
(3, 'Club Veteranos Atlixco', 'Atlixco Masters', 'Veteranos', 'Varonil');

-- ------------------------------------------------------------
-- 7. usuario
-- ------------------------------------------------------------
INSERT INTO `usuario` (`nombre_usuario`, `password`, `rol`, `nombre_completo`, `email`, `activo`) VALUES
('jgomez', '$2y$10$xH5JDZ1qZ6mYkLwA3eVpYuR9T2nBvOsI4pQdC7aEfMgNhKlWrXo.', 'Presidente',  'Jorge Gómez Hernández',   'jorge.gomez@amivd.mx',    1),
('mlopez', '$2y$10$xH5JDZ1qZ6mYkLwA3eVpYuR9T2nBvOsI4pQdC7aEfMgNhKlWrXo.', 'Secretaria', 'María López Sánchez',     'maria.lopez@amivd.mx',    1);

-- ------------------------------------------------------------
-- 8. jugador (30 jugadores)
-- ------------------------------------------------------------
INSERT INTO `jugador`
  (`apellido_paterno`,`apellido_materno`,`nombres`,`curp`,`fecha_nacimiento`,`lugar_nacimiento`,
   `nacionalidad`,`peso`,`estatura`,`id_tipo_sangre`,`ocupacion`,`escolaridad`,`escuela`,
   `telefono`,`celular`,`correo_electronico`,`enfermedades_cronicas`,`medicamentos`)
VALUES
('Martínez','Pérez','Carlos Eduardo','MAPC990315HPLERS01','1999-03-15','Puebla, Pue.','Mexicana',72.50,1.75,7,'Estudiante','Preparatoria','BUAP',NULL,'2221001001','cmartinez@gmail.com',0,NULL),
('González','Ramírez','Luis Antonio','GORL010720HPLNMS02','2001-07-20','Cholula, Pue.','Mexicana',68.00,1.70,1,'Estudiante','Secundaria','CECyTE',NULL,'2221001002','lgonzalez@gmail.com',0,NULL),
('Hernández','Torres','Ana Sofía','HETA030512MPLLNS03','2003-05-12','Puebla, Pue.','Mexicana',55.00,1.62,3,'Estudiante','Preparatoria','UDLAP',NULL,'2221001003','ahernandez@gmail.com',0,NULL),
('López','Flores','Miguel Ángel','LOFM980825HPLPLS04','1998-08-25','Atlixco, Pue.','Mexicana',80.00,1.80,7,'Empleado','Universidad','UPAEP',NULL,'2221001004','mlopez@hotmail.com',0,NULL),
('Sánchez','Vega','Gabriela','SAVG020110MPLNBS05','2002-01-10','Puebla, Pue.','Mexicana',57.50,1.65,1,'Estudiante','Preparatoria','Prepa Ibero',NULL,'2221001005','gsanchez@gmail.com',0,NULL),
('Ramírez','Castillo','José Ángel','RACJ000904HPLSNS06','2000-09-04','Tehuacán, Pue.','Mexicana',75.00,1.77,5,'Técnico','Universidad','ITESM',NULL,'2221001006','jramirez@gmail.com',0,NULL),
('Torres','Morales','Diana Paola','TOMD041218MPLRNS07','2004-12-18','Puebla, Pue.','Mexicana',53.00,1.60,2,'Estudiante','Secundaria','Sec. Téc. 1',NULL,'2221001007','dtorres@gmail.com',0,NULL),
('Flores','Jiménez','Roberto','FLOJR970306HPLRBS08','1997-03-06','Cholula, Pue.','Mexicana',82.00,1.82,7,'Docente','Universidad','BUAP',NULL,'2221001008','rflores@gmail.com',0,NULL),
('Morales','Cruz','Fernanda','MOCF010522MPLRNS09','2001-05-22','Puebla, Pue.','Mexicana',60.00,1.68,3,'Estudiante','Preparatoria','CECEP',NULL,'2221001009','fmorales@gmail.com',0,NULL),
('Jiménez','Ortiz','Alejandro','JIOA990714HPLMLS10','1999-07-14','Atlixco, Pue.','Mexicana',77.00,1.79,7,'Mecánico','Preparatoria','CONALEP',NULL,'2221001010','ajimenez@gmail.com',0,NULL),
('Cruz','Méndez','Valeria','CUMV030228MPLRLS11','2003-02-28','Puebla, Pue.','Mexicana',56.00,1.63,4,'Estudiante','Secundaria','Sec. Fed. 15',NULL,'2221001011','vcruz@gmail.com',0,NULL),
('Ortiz','Reyes','Erick David','ORED980416HPLRCS12','1998-04-16','Tehuacán, Pue.','Mexicana',74.00,1.76,1,'Contador','Universidad','UNAM',NULL,'2221001012','eortiz@gmail.com',0,NULL),
('Reyes','Gutiérrez','Paola','REGP020630MPLRLS13','2002-06-30','Cholula, Pue.','Mexicana',58.00,1.64,7,'Estudiante','Preparatoria','Prepa UIA',NULL,'2221001013','preyes@gmail.com',0,NULL),
('Gutiérrez','Vargas','Juan Pablo','GUVJ001115HPLRNS14','2000-11-15','Puebla, Pue.','Mexicana',79.00,1.81,3,'Ingeniero','Universidad','UDLAP',NULL,'2221001014','jgutierrez@gmail.com',0,NULL),
('Vargas','Medina','Lucía','VAML040301MPLRGS15','2004-03-01','Atlixco, Pue.','Mexicana',54.00,1.61,5,'Estudiante','Secundaria','Sec. Priv. Tepeyac',NULL,'2221001015','lvargas@gmail.com',0,NULL),
('Medina','Aguilar','Sergio','MEAS970820HPLRDS16','1997-08-20','Puebla, Pue.','Mexicana',83.00,1.83,7,'Administrador','Universidad','BUAP',NULL,'2221001016','smedina@gmail.com',0,NULL),
('Aguilar','Castro','Daniela','AGCD010403MPLGLS17','2001-04-03','Tehuacán, Pue.','Mexicana',61.00,1.66,1,'Estudiante','Preparatoria','Prepa 1 BUAP',NULL,'2221001017','daguilar@gmail.com',0,NULL),
('Castro','Ríos','Iván','CARI990908HPLSNS18','1999-09-08','Cholula, Pue.','Mexicana',76.00,1.78,2,'Electricista','Preparatoria','CONALEP',NULL,'2221001018','icastro@gmail.com',0,NULL),
('Ríos','Domínguez','Stephanie','RIDS030117MPLRLS19','2003-01-17','Puebla, Pue.','Mexicana',59.00,1.65,7,'Estudiante','Preparatoria','Colegio Pedagógico',NULL,'2221001019','srios@gmail.com',0,NULL),
('Domínguez','Espinoza','Omar','DOEO000723HPLMLS20','2000-07-23','Atlixco, Pue.','Mexicana',78.00,1.80,3,'Ventas','Universidad','UPAEP',NULL,'2221001020','odominguez@gmail.com',0,NULL),
('Espinoza','Lara','Andrea','ESLA020914MPLRNS21','2002-09-14','Puebla, Pue.','Mexicana',55.50,1.62,1,'Estudiante','Preparatoria','ITESM',NULL,'2221001021','aespinoza@gmail.com',0,NULL),
('Lara','Núñez','Óscar','LANO981201HPLRRS22','1998-12-01','Tehuacán, Pue.','Mexicana',81.00,1.82,7,'Bombero','Universidad','BUAP',NULL,'2221001022','olara@gmail.com',0,NULL),
('Núñez','Pacheco','Brenda','NUPB010826MPLRCS23','2001-08-26','Cholula, Pue.','Mexicana',62.00,1.67,5,'Enfermera','Universidad','UNAM',NULL,'2221001023','bnunez@gmail.com',0,NULL),
('Pacheco','Rojas','Erick','PARE000511HPLRCS24','2000-05-11','Puebla, Pue.','Mexicana',73.00,1.74,7,'Diseñador','Universidad','UDLAP',NULL,'2221001024','epacheco@gmail.com',0,NULL),
('Rojas','Salazar','Karina','ROSK040706MPLRJS25','2004-07-06','Atlixco, Pue.','Mexicana',52.00,1.59,3,'Estudiante','Secundaria','Esc. Sec. 10',NULL,'2221001025','krojas@gmail.com',0,NULL),
('Salazar','Mendoza','Héctor','SAMH971019HPLRLS26','1997-10-19','Puebla, Pue.','Mexicana',85.00,1.84,1,'Veterinario','Universidad','BUAP',NULL,'2221001026','hsalazar@gmail.com',0,NULL),
('Mendoza','Peña','Itzel','MEPI030322MPLRNS27','2003-03-22','Tehuacán, Pue.','Mexicana',57.00,1.63,4,'Estudiante','Preparatoria','Prepa ICEL',NULL,'2221001027','imendoza@gmail.com',0,NULL),
('Peña','Contreras','Axel','PECA020215HPLRXS28','2002-02-15','Cholula, Pue.','Mexicana',70.00,1.73,7,'Estudiante','Preparatoria','UPAEP Prepa',NULL,'2221001028','apena@gmail.com',0,NULL),
('Contreras','Guerrero','Monserrat','COGM010630MPLRNS29','2001-06-30','Puebla, Pue.','Mexicana',60.50,1.66,2,'Nutrióloga','Universidad','IBERO',NULL,'2221001029','mcontreras@gmail.com',0,NULL),
('Guerrero','Ibáñez','Rodrigo','GUIR990104HPLRDS30','1999-01-04','Atlixco, Pue.','Mexicana',76.50,1.79,7,'Psicólogo','Universidad','UNAM',NULL,'2221001030','rguerrero@gmail.com',0,NULL);

-- ------------------------------------------------------------
-- 9. direccion (30 direcciones, una por jugador)
-- ------------------------------------------------------------
INSERT INTO `direccion` (`id_jugador`,`id_municipio`,`calle`,`numero_exterior`,`colonia`,`codigo_postal`,`tipo_direccion`) VALUES
(1, 1,'Av. Reforma','101','Col. Centro','72000','Principal'),
(2, 2,'Calle Hidalgo','45','Col. San Andrés','72810','Principal'),
(3, 1,'Blvd. Atlixcáyotl','230','Lomas de Angelópolis','72453','Principal'),
(4, 3,'Calle Morelos','12','Col. Progreso','74270','Principal'),
(5, 1,'Av. Juárez','88','Col. La Paz','72160','Principal'),
(6, 4,'Calle Moctezuma','33','Col. Centro','75700','Principal'),
(7, 1,'Calle 5 de Mayo','17','Col. Insurgentes','72410','Principal'),
(8, 2,'Av. San Andrés','92','Col. Santa Cruz','72815','Principal'),
(9, 1,'Av. 11 Oriente','56','Col. Huexotitla','72534','Principal'),
(10,3,'Blvd. Manuel Ávila Camacho','8','Col. Primavera','91910','Principal'),
(11,1,'Calle 4 Sur','201','Col. La Libertad','72120','Principal'),
(12,4,'Calle Hidalgo','76','Col. Barrio San Marcos','75700','Principal'),
(13,2,'Calle Emiliano Zapata','14','Col. San Miguel','72760','Principal'),
(14,1,'Priv. Las Flores','3','Fracc. Bugambilias','72580','Principal'),
(15,3,'Calle Constitución','55','Col. Veracruzana','91700','Principal'),
(16,1,'Av. 20 Poniente','130','Col. Analco','72400','Principal'),
(17,4,'Blvd. Norte','22','Col. Las Palmas','75703','Principal'),
(18,2,'Calle San Pedro','67','Col. San Cristóbal','72760','Principal'),
(19,1,'Calle 8 Norte','400','Col. El Mirador','72490','Principal'),
(20,3,'Av. Ejército Mexicano','15','Col. Jardines','74270','Principal'),
(21,1,'Blvd. Valsequillo','500','Fracc. Jardines del Sur','72590','Principal'),
(22,4,'Calle Guerrero','9','Col. Constitución','75700','Principal'),
(23,2,'Av. San Rafael','77','Col. Cholula','72760','Principal'),
(24,1,'Calle 2 Oriente','320','Col. Centro Histórico','72000','Principal'),
(25,3,'Calle Tláloc','18','Col. Azteca','74270','Principal'),
(26,1,'Av. Los Fuertes','44','Col. El Refugio','72560','Principal'),
(27,4,'Priv. Girasoles','7','Col. Prados del Sur','75720','Principal'),
(28,2,'Calle Ocotlán','29','Col. Tlaxcalancingo','72824','Principal'),
(29,1,'Blvd. Héroes del 5 de Mayo','112','Fracc. Real del Bosque','72310','Principal'),
(30,3,'Calle Independencia','200','Col. Del Puerto','91700','Principal');

-- ------------------------------------------------------------
-- 10. expediente (30 expedientes)
-- ------------------------------------------------------------
INSERT INTO `expediente` (`id_jugador`, `fecha_creacion`, `estatus`) VALUES
(1,'2024-01-10','Activo'),(2,'2024-01-12','Activo'),(3,'2024-01-15','Activo'),
(4,'2024-01-18','Activo'),(5,'2024-01-20','Activo'),(6,'2024-01-22','Activo'),
(7,'2024-02-01','Activo'),(8,'2024-02-03','Activo'),(9,'2024-02-05','Activo'),
(10,'2024-02-07','Activo'),(11,'2024-02-10','Activo'),(12,'2024-02-12','Activo'),
(13,'2024-02-14','Activo'),(14,'2024-02-16','Activo'),(15,'2024-02-18','Activo'),
(16,'2024-03-01','Activo'),(17,'2024-03-03','Activo'),(18,'2024-03-05','Activo'),
(19,'2024-03-07','Activo'),(20,'2024-03-09','Activo'),(21,'2024-03-11','Activo'),
(22,'2024-03-13','Activo'),(23,'2024-03-15','Activo'),(24,'2024-03-17','Activo'),
(25,'2024-03-19','Activo'),(26,'2024-04-01','Activo'),(27,'2024-04-03','Activo'),
(28,'2024-04-05','Activo'),(29,'2024-04-07','Activo'),(30,'2024-04-09','Activo');

-- ------------------------------------------------------------
-- 11. jugador_liga (30 inscripciones)
-- ------------------------------------------------------------
INSERT INTO `jugador_liga` (`id_jugador`, `id_liga`, `fecha_inscripcion`) VALUES
(1,1,'2024-01-10'),(2,1,'2024-01-12'),(3,1,'2024-01-15'),(4,1,'2024-01-18'),
(5,1,'2024-01-20'),(6,1,'2024-01-22'),(7,1,'2024-02-01'),(8,1,'2024-02-03'),
(9,1,'2024-02-05'),(10,1,'2024-02-07'),(11,2,'2024-02-10'),(12,2,'2024-02-12'),
(13,2,'2024-02-14'),(14,2,'2024-02-16'),(15,2,'2024-02-18'),(16,2,'2024-03-01'),
(17,2,'2024-03-03'),(18,2,'2024-03-05'),(19,2,'2024-03-07'),(20,2,'2024-03-09'),
(21,3,'2024-03-11'),(22,3,'2024-03-13'),(23,3,'2024-03-15'),(24,3,'2024-03-17'),
(25,3,'2024-03-19'),(26,3,'2024-04-01'),(27,3,'2024-04-03'),(28,3,'2024-04-05'),
(29,3,'2024-04-07'),(30,3,'2024-04-09');

-- ------------------------------------------------------------
-- 12. afiliacion (30 afiliaciones)
-- ------------------------------------------------------------
INSERT INTO `afiliacion`
  (`id_jugador`,`id_club`,`id_vigencia`,`numero_registro`,`ano_vigencia`,
   `fecha_afiliacion`,`fecha_vencimiento`,`estatus`)
VALUES
(1, 1,1,'AMIVD-2024-0001',2024,'2024-01-10','2024-12-31','Activa'),
(2, 1,1,'AMIVD-2024-0002',2024,'2024-01-12','2024-12-31','Activa'),
(3, 2,1,'AMIVD-2024-0003',2024,'2024-01-15','2024-12-31','Activa'),
(4, 1,2,'AMIVD-2024-0004',2024,'2024-01-18','2024-07-18','Vencida'),
(5, 2,1,'AMIVD-2024-0005',2024,'2024-01-20','2024-12-31','Activa'),
(6, 1,1,'AMIVD-2024-0006',2024,'2024-01-22','2024-12-31','Activa'),
(7, 3,1,'AMIVD-2024-0007',2024,'2024-02-01','2024-12-31','Activa'),
(8, 1,1,'AMIVD-2024-0008',2024,'2024-02-03','2024-12-31','Activa'),
(9, 2,2,'AMIVD-2024-0009',2024,'2024-02-05','2024-08-05','Vencida'),
(10,1,1,'AMIVD-2024-0010',2024,'2024-02-07','2024-12-31','Activa'),
(11,3,1,'AMIVD-2024-0011',2024,'2024-02-10','2024-12-31','Activa'),
(12,4,1,'AMIVD-2024-0012',2024,'2024-02-12','2024-12-31','Activa'),
(13,3,2,'AMIVD-2024-0013',2024,'2024-02-14','2024-08-14','Vencida'),
(14,4,1,'AMIVD-2024-0014',2024,'2024-02-16','2024-12-31','Activa'),
(15,3,1,'AMIVD-2024-0015',2024,'2024-02-18','2024-12-31','Activa'),
(16,4,1,'AMIVD-2025-0016',2025,'2025-01-10','2025-12-31','Activa'),
(17,5,1,'AMIVD-2025-0017',2025,'2025-01-12','2025-12-31','Activa'),
(18,4,2,'AMIVD-2025-0018',2025,'2025-01-15','2025-07-15','Vencida'),
(19,5,1,'AMIVD-2025-0019',2025,'2025-01-18','2025-12-31','Activa'),
(20,4,1,'AMIVD-2025-0020',2025,'2025-01-20','2025-12-31','Activa'),
(21,5,1,'AMIVD-2025-0021',2025,'2025-02-01','2025-12-31','Activa'),
(22,5,1,'AMIVD-2025-0022',2025,'2025-02-03','2025-12-31','Activa'),
(23,5,2,'AMIVD-2025-0023',2025,'2025-02-05','2025-08-05','Vencida'),
(24,5,1,'AMIVD-2025-0024',2025,'2025-02-07','2025-12-31','Activa'),
(25,3,1,'AMIVD-2025-0025',2025,'2025-03-01','2025-12-31','Activa'),
(26,1,1,'AMIVD-2025-0026',2025,'2025-03-05','2025-12-31','Activa'),
(27,2,1,'AMIVD-2025-0027',2025,'2025-03-10','2025-12-31','Activa'),
(28,3,2,'AMIVD-2025-0028',2025,'2025-03-15','2025-09-15','Activa'),
(29,4,1,'AMIVD-2025-0029',2025,'2025-04-01','2025-12-31','Activa'),
(30,5,1,'AMIVD-2025-0030',2025,'2025-04-05','2025-12-31','Activa');

-- ------------------------------------------------------------
-- 13. pago (30 pagos, uno por afiliación)
-- ------------------------------------------------------------
INSERT INTO `pago` (`id_afiliacion`,`fecha_pago`,`estatus`,`metodo_pago`,`referencia`) VALUES
(1, '2024-01-10','Completado','Efectivo','EFE-001'),
(2, '2024-01-12','Completado','Transferencia','TRF-00234'),
(3, '2024-01-15','Completado','Efectivo','EFE-003'),
(4, '2024-01-18','Completado','Tarjeta','TDC-04811'),
(5, '2024-01-20','Completado','Transferencia','TRF-00541'),
(6, '2024-01-22','Completado','Efectivo','EFE-006'),
(7, '2024-02-01','Completado','Efectivo','EFE-007'),
(8, '2024-02-03','Completado','Transferencia','TRF-00821'),
(9, '2024-02-05','Completado','Tarjeta','TDC-09013'),
(10,'2024-02-07','Completado','Efectivo','EFE-010'),
(11,'2024-02-10','Completado','Transferencia','TRF-01100'),
(12,'2024-02-12','Completado','Efectivo','EFE-012'),
(13,'2024-02-14','Completado','Transferencia','TRF-01342'),
(14,'2024-02-16','Completado','Tarjeta','TDC-14500'),
(15,'2024-02-18','Completado','Efectivo','EFE-015'),
(16,'2025-01-10','Completado','Transferencia','TRF-02016'),
(17,'2025-01-12','Completado','Efectivo','EFE-017'),
(18,'2025-01-15','Completado','Tarjeta','TDC-18001'),
(19,'2025-01-18','Completado','Efectivo','EFE-019'),
(20,'2025-01-20','Completado','Transferencia','TRF-02034'),
(21,'2025-02-01','Completado','Efectivo','EFE-021'),
(22,'2025-02-03','Pendiente',NULL,NULL),
(23,'2025-02-05','Completado','Transferencia','TRF-02345'),
(24,'2025-02-07','Completado','Efectivo','EFE-024'),
(25,'2025-03-01','Completado','Tarjeta','TDC-25100'),
(26,'2025-03-05','Completado','Efectivo','EFE-026'),
(27,'2025-03-10','Pendiente',NULL,NULL),
(28,'2025-03-15','Completado','Transferencia','TRF-02801'),
(29,'2025-04-01','Completado','Efectivo','EFE-029'),
(30,'2025-04-05','Completado','Tarjeta','TDC-30099');

-- ------------------------------------------------------------
-- 14. padre_tutor (para jugadores menores de edad — ids 3,7,11,15,25,27)
-- ------------------------------------------------------------
INSERT INTO `padre_tutor`
  (`id_jugador`,`nombre_completo`,`celular`,`correo_electronico`,`curp_tutor`,`fotografia_ine`)
VALUES
(3, 'Laura Torres Jiménez',   '2221009003','ltorres@gmail.com', 'TOJL750215MPLRRS01', NULL),
(7, 'Rosa Morales Ríos',      '2221009007','rmorales@gmail.com','MORG780310MPLRSS02', NULL),
(11,'Marco Reyes Sánchez',    '2221009011','mreyes@gmail.com',  'RESM810422HPLRCS03', NULL),
(15,'Patricia Medina Castro', '2221009015','pmedina@gmail.com', 'MECP761108MPLRDS04', NULL),
(25,'Sandra Salazar Bravo',   '2221009025','ssalazar@gmail.com','SABS800615MPLRLS05', NULL),
(27,'Arturo Mendoza Luna',    '2221009027','amendoza@gmail.com','MELA790920HPLRRS06', NULL);

-- ------------------------------------------------------------
-- 15. sanciones (5 sanciones de ejemplo)
-- ------------------------------------------------------------
INSERT INTO `sanciones`
  (`id_jugador`,`id_liga`,`tipo_sancion`,`fecha_sancion`,`fecha_fin_sancion`,`motivo`,`estatus`)
VALUES
(4, 1,'Suspensión','2024-03-10','2024-04-10','Conducta antideportiva en partido','Cumplida'),
(8, 1,'Amonestación','2024-05-15',NULL,'Vocabulario inapropiado hacia árbitro','Activa'),
(13,2,'Multa','2024-04-20',NULL,'No presentación a partido programado','Activa'),
(20,2,'Suspensión','2024-06-01','2024-07-01','Agresión física a jugador rival','Cumplida'),
(26,3,'Amonestación','2025-02-10',NULL,'Acumulación de tarjetas amarillas','Activa');

-- ------------------------------------------------------------
-- 16. autorizacion_pendiente (5 solicitudes)
-- ------------------------------------------------------------
INSERT INTO `autorizacion_pendiente`
  (`tipo_solicitud`,`id_referencia`,`fecha_solicitud`,`estatus`,`comentarios`)
VALUES
('Jugador', 22,'2025-02-03','Pendiente',  'Verificar CURP y documentos'),
('Jugador', 27,'2025-03-10','Pendiente',  'Falta foto de INE del tutor'),
('Club',    3, '2025-01-05','Aprobada',   'Club validado correctamente'),
('Club',    5, '2025-01-20','Aprobada',   'Documentación completa'),
('Jugador', 30,'2025-04-05','Pendiente',  'Pago pendiente de verificar');

-- ------------------------------------------------------------
-- 17. notificacion (5 notificaciones para los usuarios)
-- ------------------------------------------------------------
INSERT INTO `notificacion` (`id_usuario`,`mensaje`,`fecha`,`leida`,`fecha_eliminacion`) VALUES
(1,'Nueva solicitud de afiliación pendiente de autorizar (Jugador ID 22).','2025-02-03 09:00:00',0,'2025-03-03 09:00:00'),
(2,'El pago TRF-02016 fue registrado correctamente.','2025-01-10 10:30:00',1,'2025-02-10 10:30:00'),
(1,'Sanción aplicada al jugador Erick David Ortiz (ID 8).','2024-05-15 15:00:00',1,'2024-06-15 15:00:00'),
(2,'Nueva solicitud de club pendiente de aprobación (Club ID 3).','2025-01-05 08:00:00',1,'2025-02-05 08:00:00'),
(1,'Afiliación AMIVD-2025-0030 requiere verificación de pago.','2025-04-05 11:00:00',0,'2025-05-05 11:00:00');

-- ------------------------------------------------------------
-- 18. registro_externo (5 registros de portales externos)
-- ------------------------------------------------------------
INSERT INTO `registro_externo`
  (`tipo`,`nombre_completo`,`curp`,`email`,`telefono`,`fecha_nacimiento`,`estatus`)
VALUES
('Jugador','Tomás Serrano Blanco','SEBT050812HPLRLS01','tserrano@gmail.com','2221110001','2005-08-12','Pendiente'),
('Arbitro','Luis Enrique Palacios','PALL800310HPLRLS02','lepalacios@gmail.com','2221110002','1980-03-10','Revisado'),
('Entrenador','Andrés Velázquez Mora','VEMA750422HPLRMS03','avelazquez@gmail.com','2221110003','1975-04-22','Revisado'),
('Jugador','Sofía Carrillo Díaz','CADS040601MPLRRS04','scarrillo@gmail.com','2221110004','2004-06-01','Pendiente'),
('Arbitro','Carmen Juárez López','JULC850919MPLRRS05','cjuarez@gmail.com','2221110005','1985-09-19','Pendiente');

-- ------------------------------------------------------------
-- 19. sesion (2 sesiones activas)
-- ------------------------------------------------------------
INSERT INTO `sesion` (`id_usuario`,`token`,`fecha_inicio`,`fecha_expiracion`,`ip_address`) VALUES
(1,'tok_a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6','2026-04-15 08:00:00','2026-04-15 20:00:00','192.168.1.10'),
(2,'tok_z9y8x7w6v5u4t3s2r1q0p9o8n7m6l5k4','2026-04-15 09:15:00','2026-04-15 21:15:00','192.168.1.11');

-- ------------------------------------------------------------
-- 20. formato_digital (5 documentos)
-- ------------------------------------------------------------
INSERT INTO `formato_digital`
  (`id_jugador`,`id_expediente`,`nombre_archivo`,`ruta`,`tipo`,`fecha_subida`)
VALUES
(1, 1, 'curp_cmartinez.pdf',  '/docs/jugadores/1/curp_cmartinez.pdf',  'CURP', '2024-01-10'),
(2, 2, 'acta_lgonzalez.pdf',  '/docs/jugadores/2/acta_lgonzalez.pdf',  'Acta de Nacimiento','2024-01-12'),
(5, 5, 'ine_gsanchez.jpg',    '/docs/jugadores/5/ine_gsanchez.jpg',    'INE',  '2024-01-20'),
(8, 8, 'foto_rflores.jpg',    '/docs/jugadores/8/foto_rflores.jpg',    'Fotografía','2024-02-03'),
(16,16,'curp_smedina.pdf',    '/docs/jugadores/16/curp_smedina.pdf',   'CURP', '2025-01-10');

SET FOREIGN_KEY_CHECKS = 1;

-- ============================================================
-- FIN DE DATOS DE PRUEBA
-- Total: 30 jugadores + catálogos + relaciones completas
-- ============================================================
