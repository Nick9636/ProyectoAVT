-- MySQL dump 10.13  Distrib 8.0.45, for Win64 (x86_64)
--
-- Host: localhost    Database: base_datos_amivd
-- ------------------------------------------------------
-- Server version	8.0.45

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `afiliacion`
--

DROP TABLE IF EXISTS `afiliacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `afiliacion` (
  `id_afiliacion` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la afiliación',
  `id_jugador` bigint NOT NULL COMMENT 'Referencia al jugador afiliado',
  `id_club` bigint NOT NULL COMMENT 'Referencia al club al que se afilia',
  `id_vigencia` bigint NOT NULL COMMENT 'Referencia al tipo de vigencia',
  `numero_registro` varchar(50) NOT NULL COMMENT 'Número único de registro de afiliación',
  `ano_vigencia` int NOT NULL COMMENT 'Año de vigencia de la afiliación',
  `fecha_afiliacion` date NOT NULL COMMENT 'Fecha en que se realizó la afiliación',
  `fecha_vencimiento` date NOT NULL COMMENT 'Fecha en que vence la afiliación',
  `estatus` varchar(20) DEFAULT 'Activa' COMMENT 'Estatus de la afiliación (Activa, Vencida, Suspendida)',
  PRIMARY KEY (`id_afiliacion`),
  UNIQUE KEY `numero_registro` (`numero_registro`),
  KEY `afiliacion_id_jugador_foreign` (`id_jugador`),
  KEY `afiliacion_id_club_foreign` (`id_club`),
  KEY `afiliacion_id_vigencia_foreign` (`id_vigencia`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `afiliacion`
--

LOCK TABLES `afiliacion` WRITE;
/*!40000 ALTER TABLE `afiliacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `afiliacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `arbitro`
--

DROP TABLE IF EXISTS `arbitro`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `arbitro` (
  `id_arbitro` bigint NOT NULL AUTO_INCREMENT,
  `id_equipo` bigint DEFAULT NULL,
  `id_direccion` bigint DEFAULT NULL,
  `apellido_paterno` varchar(80) NOT NULL,
  `apellido_materno` varchar(80) NOT NULL,
  `nombres` varchar(100) NOT NULL,
  `numero_registro` varchar(30) DEFAULT NULL,
  `curp` char(18) NOT NULL,
  `vigencia` varchar(50) DEFAULT NULL,
  `fecha_nacimiento` date NOT NULL,
  `lugar_nacimiento` varchar(100) DEFAULT NULL,
  `nacionalidad` varchar(50) DEFAULT 'MEXICANA',
  `peso` decimal(5,2) DEFAULT NULL,
  `estatura` decimal(4,2) DEFAULT NULL,
  `tipo_sangre` varchar(5) DEFAULT NULL,
  `ocupacion` varchar(100) DEFAULT NULL,
  `escolaridad` varchar(100) DEFAULT NULL,
  `escuela` varchar(150) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `celular` varchar(20) DEFAULT NULL,
  `correo_electronico` varchar(150) DEFAULT NULL,
  `enfermedades_cronicas` varchar(200) DEFAULT 'NINGUNA',
  `medicamentos` varchar(200) DEFAULT 'NINGUNA',
  `club` varchar(150) DEFAULT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  `rama` varchar(20) DEFAULT NULL,
  `zona` varchar(100) DEFAULT NULL,
  `licencia` varchar(50) DEFAULT NULL,
  `ligas_participa` varchar(255) DEFAULT NULL,
  `fotografia` varchar(500) DEFAULT NULL,
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_arbitro`),
  UNIQUE KEY `curp` (`curp`),
  KEY `id_equipo` (`id_equipo`),
  KEY `id_direccion` (`id_direccion`),
  CONSTRAINT `arbitro_ibfk_1` FOREIGN KEY (`id_equipo`) REFERENCES `equipo` (`id_equipo`),
  CONSTRAINT `arbitro_ibfk_2` FOREIGN KEY (`id_direccion`) REFERENCES `direccion` (`id_direccion`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `arbitro`
--

LOCK TABLES `arbitro` WRITE;
/*!40000 ALTER TABLE `arbitro` DISABLE KEYS */;
INSERT INTO `arbitro` VALUES (1,1,8,'LÓPEZ','HERNÁNDEZ','MARÍA','002','LOHM920215MTLXRSB2','2026','2005-01-11','TLAXCALA','MEXICANA',65.00,1.65,'O-','CONTADORA','LICENCIATURA','INSTITUTO TECNOLÓGICO DE APIZACO','2462345678','2468765432','maria.lopez@mail.com','NINGUNA','NINGUNA','DRAGONES','JUVENIL',NULL,NULL,NULL,'LIGA PANOTLA',NULL,'2026-04-16 00:26:21'),(2,21,5,'TORRES','RUIZ','SOFÍA','006','TORS990623MTLXRTG6','2026','1999-06-26','TLAXCALA','MEXICANA',52.00,1.62,'A-','ESTUDIANTE','LICENCIATURA','UNIVERSIDAD POLITÉCNICA DE TLAXCALA','2466789012','2462109876','sofia.t@mail.com','NINGUNA','NINGUNA','MAPACHES','MAYOR','FEMENIL','tlaxcala','estatal','LIGA AMIVD ATLIXCO',NULL,'2026-04-16 00:57:55');
/*!40000 ALTER TABLE `arbitro` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `autorizacion_pendiente`
--

DROP TABLE IF EXISTS `autorizacion_pendiente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `autorizacion_pendiente` (
  `id_autorizacion` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la autorización',
  `tipo_solicitud` varchar(50) NOT NULL COMMENT 'Tipo de solicitud (Jugador, Club, etc.)',
  `id_referencia` bigint NOT NULL COMMENT 'ID del registro que se está solicitando autorizar',
  `fecha_solicitud` date NOT NULL COMMENT 'Fecha en que se hizo la solicitud',
  `estatus` varchar(20) DEFAULT 'Pendiente' COMMENT 'Estatus de la autorización (Pendiente, Aprobada, Rechazada)',
  `comentarios` text COMMENT 'Comentarios adicionales sobre la solicitud',
  `email_solicitante` varchar(150) DEFAULT NULL,
  `nombre_solicitante` varchar(150) DEFAULT NULL,
  `id_usuario_autorizador` bigint DEFAULT NULL,
  PRIMARY KEY (`id_autorizacion`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `autorizacion_pendiente`
--

LOCK TABLES `autorizacion_pendiente` WRITE;
/*!40000 ALTER TABLE `autorizacion_pendiente` DISABLE KEYS */;
INSERT INTO `autorizacion_pendiente` VALUES (1,'jugador',38,'2026-04-22','Rechazado','f f',NULL,NULL,NULL),(2,'jugador',41,'2026-04-22','Autorizado',NULL,NULL,NULL,NULL);
/*!40000 ALTER TABLE `autorizacion_pendiente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cat_estado`
--

DROP TABLE IF EXISTS `cat_estado`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cat_estado` (
  `id_estado` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del estado',
  `nombre` varchar(50) NOT NULL COMMENT 'Nombre del estado',
  PRIMARY KEY (`id_estado`),
  UNIQUE KEY `nombre` (`nombre`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cat_estado`
--

LOCK TABLES `cat_estado` WRITE;
/*!40000 ALTER TABLE `cat_estado` DISABLE KEYS */;
INSERT INTO `cat_estado` VALUES (2,'Ciudad de México'),(5,'Hidalgo'),(1,'Puebla'),(4,'Tlaxcala'),(3,'Veracruz');
/*!40000 ALTER TABLE `cat_estado` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cat_municipio`
--

DROP TABLE IF EXISTS `cat_municipio`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cat_municipio` (
  `id_municipio` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del municipio',
  `id_estado` int NOT NULL COMMENT 'Referencia al estado al que pertenece el municipio',
  `nombre` varchar(100) NOT NULL COMMENT 'Nombre del municipio',
  PRIMARY KEY (`id_municipio`),
  KEY `cat_municipio_id_estado_foreign` (`id_estado`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cat_municipio`
--

LOCK TABLES `cat_municipio` WRITE;
/*!40000 ALTER TABLE `cat_municipio` DISABLE KEYS */;
INSERT INTO `cat_municipio` VALUES (1,1,'Puebla'),(2,1,'Cholula'),(3,1,'Atlixco'),(4,1,'Tehuacán'),(5,2,'Benito Juárez'),(6,2,'Coyoacán'),(7,3,'Veracruz'),(8,4,'Tlaxcala'),(9,5,'Pachuca');
/*!40000 ALTER TABLE `cat_municipio` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cat_tipo_sangre`
--

DROP TABLE IF EXISTS `cat_tipo_sangre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cat_tipo_sangre` (
  `id_tipo_sangre` int NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del tipo de sangre',
  `descripcion` varchar(10) NOT NULL COMMENT 'Descripción del tipo de sangre (A+, O-, B+, etc.)',
  PRIMARY KEY (`id_tipo_sangre`),
  UNIQUE KEY `descripcion` (`descripcion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cat_tipo_sangre`
--

LOCK TABLES `cat_tipo_sangre` WRITE;
/*!40000 ALTER TABLE `cat_tipo_sangre` DISABLE KEYS */;
/*!40000 ALTER TABLE `cat_tipo_sangre` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `club`
--

DROP TABLE IF EXISTS `club`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `club` (
  `id_club` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del club',
  `id_liga` bigint NOT NULL COMMENT 'Referencia a la liga a la que pertenece el club',
  `nombre_club` varchar(100) NOT NULL COMMENT 'Nombre del club deportivo',
  `nombre_equipo` varchar(100) DEFAULT NULL COMMENT 'Nombre del equipo específico dentro del club',
  `categoria` varchar(50) DEFAULT NULL COMMENT 'Categoría del equipo',
  `rama` varchar(20) DEFAULT NULL COMMENT 'Rama del equipo (Varonil, Femenil, Mixto)',
  PRIMARY KEY (`id_club`),
  KEY `club_id_liga_foreign` (`id_liga`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `club`
--

LOCK TABLES `club` WRITE;
/*!40000 ALTER TABLE `club` DISABLE KEYS */;
/*!40000 ALTER TABLE `club` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `direccion`
--

DROP TABLE IF EXISTS `direccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `direccion` (
  `id_direccion` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la dirección',
  `id_jugador` bigint NOT NULL COMMENT 'Referencia al jugador al que pertenece la dirección',
  `id_municipio` int NOT NULL COMMENT 'Referencia al municipio donde está ubicada',
  `calle` varchar(100) NOT NULL COMMENT 'Nombre de la calle',
  `numero_exterior` varchar(20) DEFAULT NULL COMMENT 'Número exterior del domicilio',
  `colonia` varchar(100) NOT NULL COMMENT 'Nombre de la colonia',
  `codigo_postal` varchar(10) NOT NULL COMMENT 'Código postal del domicilio',
  `tipo_direccion` varchar(20) DEFAULT 'Principal' COMMENT 'Tipo de dirección (Principal, Secundaria, Fiscal)',
  PRIMARY KEY (`id_direccion`),
  KEY `direccion_id_jugador_foreign` (`id_jugador`),
  KEY `direccion_id_municipio_foreign` (`id_municipio`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `direccion`
--

LOCK TABLES `direccion` WRITE;
/*!40000 ALTER TABLE `direccion` DISABLE KEYS */;
INSERT INTO `direccion` VALUES (1,38,1,'PRIV.MAXIMO','','ATLAHAPA','90811','Principal'),(2,41,1,'PRIV.MAXIMO','','ATLAHAPA','90811','Principal');
/*!40000 ALTER TABLE `direccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `entrenador`
--

DROP TABLE IF EXISTS `entrenador`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `entrenador` (
  `id_entrenador` bigint NOT NULL AUTO_INCREMENT,
  `id_equipo` bigint DEFAULT NULL,
  `id_direccion` bigint DEFAULT NULL,
  `apellido_paterno` varchar(80) NOT NULL,
  `apellido_materno` varchar(80) NOT NULL,
  `nombres` varchar(100) NOT NULL,
  `numero_registro` varchar(30) DEFAULT NULL,
  `curp` varchar(18) NOT NULL,
  `vigencia` varchar(50) DEFAULT NULL,
  `fecha_nacimiento` date NOT NULL,
  `lugar_nacimiento` varchar(100) DEFAULT NULL,
  `nacionalidad` varchar(50) DEFAULT 'MEXICANA',
  `peso` decimal(5,2) DEFAULT NULL,
  `estatura` decimal(4,2) DEFAULT NULL,
  `tipo_sangre` varchar(5) DEFAULT NULL,
  `ocupacion` varchar(100) DEFAULT NULL,
  `escolaridad` varchar(100) DEFAULT NULL,
  `escuela` varchar(150) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `celular` varchar(20) DEFAULT NULL,
  `correo_electronico` varchar(150) DEFAULT NULL,
  `enfermedades_cronicas` varchar(200) DEFAULT 'NINGUNA',
  `medicamentos` varchar(200) DEFAULT 'NINGUNA',
  `club` varchar(150) DEFAULT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  `rama` varchar(20) DEFAULT NULL,
  `ligas_participa` varchar(255) DEFAULT NULL,
  `cedula` varchar(50) DEFAULT NULL,
  `especialidad` varchar(100) DEFAULT NULL,
  `fotografia` varchar(500) DEFAULT NULL,
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_entrenador`),
  UNIQUE KEY `curp` (`curp`),
  KEY `id_equipo` (`id_equipo`),
  KEY `id_direccion` (`id_direccion`),
  CONSTRAINT `entrenador_ibfk_1` FOREIGN KEY (`id_equipo`) REFERENCES `equipo` (`id_equipo`),
  CONSTRAINT `entrenador_ibfk_2` FOREIGN KEY (`id_direccion`) REFERENCES `direccion` (`id_direccion`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `entrenador`
--

LOCK TABLES `entrenador` WRITE;
/*!40000 ALTER TABLE `entrenador` DISABLE KEYS */;
INSERT INTO `entrenador` VALUES (1,20,2,'SÁNCHEZ','MARTÍNEZ','CARLOS','003','AMC880310HTLXRTC3','2026','1988-03-10','TLAXCALA','MEXICANA',80.00,1.75,'B+','COMERCIANTE','BACHILLERATO','COBAT','2463456789','2469876543','carlos.s@mail.com','NINGUNA','NINGUNA','LEONES','JUVENIL','VARONIL','LIGA AMIVD ATLIXCO','001','MAYOR',NULL,'2026-04-16 00:48:05'),(2,18,7,'CASTILLO','JIMÉNEZ','LAURA','008','CAJL940912MTLXRRI8','2026','1994-09-12','TLAXCALA','MEXICANA',58.00,1.65,'B-','DISEÑADORA','LICENCIATURA','UNIVERSIDAD DEL VALLE DE TLAXCALA','2468901234','2464321098','laura.c@mail.com','NINGUNA','NINGUNA','GARZAS','INFANTIL','FEMENIL','LIGA AMIVD ATLIXCO','002','Mayor',NULL,'2026-04-16 01:04:30');
/*!40000 ALTER TABLE `entrenador` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `equipo`
--

DROP TABLE IF EXISTS `equipo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `equipo` (
  `id_equipo` bigint NOT NULL AUTO_INCREMENT,
  `id_liga` bigint NOT NULL,
  `nombre_equipo` varchar(150) NOT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id_equipo`),
  KEY `id_liga` (`id_liga`),
  CONSTRAINT `equipo_ibfk_1` FOREIGN KEY (`id_liga`) REFERENCES `liga` (`id_liga`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `equipo`
--

LOCK TABLES `equipo` WRITE;
/*!40000 ALTER TABLE `equipo` DISABLE KEYS */;
INSERT INTO `equipo` VALUES (1,1,'Volcanes FC','Primera Fuerza'),(2,1,'Estrellas Femenil','Primera Fuerza'),(3,2,'Pirámides Juvenil','Juvenil'),(4,2,'San Andrés Mixto','Juvenil'),(5,3,'Atlixco Masters','Veteranos');
/*!40000 ALTER TABLE `equipo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `expediente`
--

DROP TABLE IF EXISTS `expediente`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `expediente` (
  `id_expediente` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del expediente',
  `id_jugador` bigint NOT NULL COMMENT 'Referencia al jugador dueño del expediente',
  `fecha_creacion` date NOT NULL COMMENT 'Fecha en que se creó el expediente',
  `estatus` varchar(20) DEFAULT 'Activo' COMMENT 'Estatus del expediente (Activo, Cerrado)',
  PRIMARY KEY (`id_expediente`),
  KEY `expediente_id_jugador_foreign` (`id_jugador`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `expediente`
--

LOCK TABLES `expediente` WRITE;
/*!40000 ALTER TABLE `expediente` DISABLE KEYS */;
INSERT INTO `expediente` VALUES (1,38,'2026-04-22','activo'),(2,41,'2026-04-22','activo');
/*!40000 ALTER TABLE `expediente` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `formato_digital`
--

DROP TABLE IF EXISTS `formato_digital`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `formato_digital` (
  `id_formato` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del formato digital',
  `id_jugador` bigint NOT NULL COMMENT 'Referencia al jugador dueño del documento',
  `id_expediente` bigint DEFAULT NULL COMMENT 'Referencia al expediente al que pertenece (opcional)',
  `nombre_archivo` varchar(255) NOT NULL COMMENT 'Nombre original del archivo',
  `ruta` varchar(500) NOT NULL COMMENT 'Ruta donde está guardado el archivo en el servidor',
  `tipo` varchar(50) NOT NULL COMMENT 'Tipo de documento (INE, CURP, Acta, etc.)',
  `fecha_subida` date NOT NULL COMMENT 'Fecha en que se subió el documento',
  PRIMARY KEY (`id_formato`),
  KEY `formato_digital_id_jugador_foreign` (`id_jugador`),
  KEY `formato_digital_id_expediente_foreign` (`id_expediente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `formato_digital`
--

LOCK TABLES `formato_digital` WRITE;
/*!40000 ALTER TABLE `formato_digital` DISABLE KEYS */;
/*!40000 ALTER TABLE `formato_digital` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jugador`
--

DROP TABLE IF EXISTS `jugador`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jugador` (
  `id_jugador` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del jugador',
  `apellido_paterno` varchar(50) NOT NULL COMMENT 'Apellido paterno del jugador',
  `apellido_materno` varchar(50) DEFAULT NULL COMMENT 'Apellido materno del jugador (opcional)',
  `nombres` varchar(100) NOT NULL COMMENT 'Nombres del jugador',
  `curp` varchar(18) NOT NULL COMMENT 'CURP del jugador (única por persona)',
  `fecha_nacimiento` date NOT NULL COMMENT 'Fecha de nacimiento del jugador',
  `lugar_nacimiento` varchar(100) DEFAULT NULL COMMENT 'Lugar donde nació el jugador',
  `nacionalidad` varchar(50) DEFAULT 'Mexicana' COMMENT 'Nacionalidad del jugador',
  `peso` decimal(5,2) DEFAULT NULL COMMENT 'Peso del jugador en kilogramos',
  `estatura` decimal(5,2) DEFAULT NULL COMMENT 'Estatura del jugador en metros',
  `id_tipo_sangre` int DEFAULT NULL COMMENT 'Referencia al tipo de sangre del jugador',
  `ocupacion` varchar(100) DEFAULT NULL COMMENT 'Ocupación del jugador',
  `escolaridad` varchar(100) DEFAULT NULL COMMENT 'Nivel de escolaridad del jugador',
  `escuela` varchar(100) DEFAULT NULL COMMENT 'Escuela donde estudia el jugador',
  `telefono` varchar(20) DEFAULT NULL COMMENT 'Teléfono fijo del jugador',
  `celular` varchar(20) DEFAULT NULL COMMENT 'Teléfono celular del jugador',
  `correo_electronico` varchar(150) DEFAULT NULL COMMENT 'Correo electrónico del jugador',
  `fotografia` varchar(255) DEFAULT NULL COMMENT 'Ruta donde se guarda la foto del jugador',
  `enfermedades_cronicas` tinyint(1) DEFAULT '0' COMMENT 'Indica si el jugador padece enfermedades crónicas',
  `medicamentos` text COMMENT 'Descripción de los medicamentos que toma el jugador',
  PRIMARY KEY (`id_jugador`),
  UNIQUE KEY `curp` (`curp`),
  KEY `jugador_id_tipo_sangre_foreign` (`id_tipo_sangre`)
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jugador`
--

LOCK TABLES `jugador` WRITE;
/*!40000 ALTER TABLE `jugador` DISABLE KEYS */;
INSERT INTO `jugador` VALUES (8,'Hernandez','Garcia','Luis Alberto','HEGL900315HPLRRN01','1990-03-15','Puebla','Mexicana',72.50,1.75,1,'Estudiante','Universidad','BUAP','2221234567','2227654321','luis1@gmail.com','/fotos/luis1.jpg',0,NULL),(9,'Martinez','Lopez','Carlos Eduardo','MALC880712HDFTRR02','1988-07-12','CDMX','Mexicana',80.20,1.80,2,'Empleado','Preparatoria','CONALEP','2221111111','2222222222','carlos2@gmail.com','/fotos/carlos2.jpg',0,NULL),(10,'Perez','Sanchez','Juan Pablo','PESJ950101HPLRNN03','1995-01-01','Puebla','Mexicana',68.40,1.70,3,'Estudiante','Universidad','BUAP','2223333333','2224444444','juan3@gmail.com','/fotos/juan3.jpg',0,NULL),(11,'Torres','Ramirez','Miguel Angel','TORM920430HDFRMG04','1992-04-30','CDMX','Mexicana',75.00,1.78,4,'Empleado','Licenciatura','IPN','2225555555','2226666666','miguel4@gmail.com','/fotos/miguel4.jpg',0,NULL),(12,'Gomez','Diaz','Jorge Luis','GODJ870921HPLMZR05','1987-09-21','Puebla','Mexicana',82.30,1.82,1,'Comerciante','Secundaria','N/A','2227777777','2228888888','jorge5@gmail.com','/fotos/jorge5.jpg',0,NULL),(13,'Flores','Vazquez','Pedro Antonio','FOVP930215HDFLRR06','1993-02-15','CDMX','Mexicana',70.10,1.74,2,'Empleado','Preparatoria','CBTIS','2229999999','2220000000','pedro6@gmail.com','/fotos/pedro6.jpg',0,NULL),(14,'Morales','Castro','Ricardo','MOCR910808HPLRSD07','1991-08-08','Puebla','Mexicana',78.00,1.77,3,'Ingeniero','Universidad','BUAP','2221010101','2222020202','ricardo7@gmail.com','/fotos/ricardo7.jpg',0,NULL),(15,'Ortiz','Ruiz','Fernando','OURF890602HDFRTN08','1989-06-02','CDMX','Mexicana',85.00,1.85,4,'Empleado','Preparatoria','UNAM','2223030303','2224040404','fernando8@gmail.com','/fotos/fernando8.jpg',0,NULL),(16,'Chavez','Rojas','Daniel','CARD940110HPLHNS09','1994-01-10','Puebla','Mexicana',69.50,1.72,1,'Estudiante','Universidad','BUAP','2225050505','2226060606','daniel9@gmail.com','/fotos/daniel9.jpg',0,NULL),(17,'Mendoza','Silva','Eduardo','MESE860325HDFNLR10','1986-03-25','CDMX','Mexicana',88.20,1.83,2,'Empleado','Secundaria','N/A','2227070707','2228080808','eduardo10@gmail.com','/fotos/eduardo10.jpg',0,NULL),(18,'Vargas','Cruz','Oscar','VACO920714HPLRRS11','1992-07-14','Puebla','Mexicana',76.30,1.79,3,'Empleado','Preparatoria','CBTIS','2229090909','2220101010','oscar11@gmail.com','/fotos/oscar11.jpg',0,NULL),(19,'Ramos','Herrera','Alejandro','RAHA900905HDFMLR12','1990-09-05','CDMX','Mexicana',79.00,1.81,4,'Ingeniero','Universidad','IPN','2221212121','2222323232','alejandro12@gmail.com','/fotos/alejandro12.jpg',0,NULL),(20,'Jimenez','Navarro','Andres','JINA950420HPLMND13','1995-04-20','Puebla','Mexicana',67.80,1.69,1,'Estudiante','Universidad','BUAP','2223434343','2224545454','andres13@gmail.com','/fotos/andres13.jpg',0,NULL),(21,'Santos','Campos','Hector','SACH880111HDFNTC14','1988-01-11','CDMX','Mexicana',83.50,1.84,2,'Empleado','Preparatoria','CONALEP','2225656565','2226767676','hector14@gmail.com','/fotos/hector14.jpg',0,NULL),(22,'Aguilar','Ortega','Victor','AUOV910303HPLGRT15','1991-03-03','Puebla','Mexicana',74.20,1.76,3,'Empleado','Secundaria','N/A','2227878787','2228989898','victor15@gmail.com','/fotos/victor15.jpg',0,NULL),(23,'Reyes','Salazar','Manuel','RESM930622HDFYNL16','1993-06-22','CDMX','Mexicana',77.70,1.78,4,'Empleado','Preparatoria','UNAM','2221112233','2223344556','manuel16@gmail.com','/fotos/manuel16.jpg',0,NULL),(24,'Castillo','Nunez','Raul','CANR870819HPLSTZ17','1987-08-19','Puebla','Mexicana',81.00,1.82,1,'Comerciante','Secundaria','N/A','2224455667','2225566778','raul17@gmail.com','/fotos/raul17.jpg',0,NULL),(25,'Delgado','Pineda','Francisco','DEPF940731HDFLNR18','1994-07-31','CDMX','Mexicana',72.00,1.75,2,'Estudiante','Universidad','IPN','2226677889','2227788990','francisco18@gmail.com','/fotos/francisco18.jpg',0,NULL),(26,'Cortes','Valencia','Roberto','COVR900512HPLRRB19','1990-05-12','Puebla','Mexicana',86.00,1.86,3,'Empleado','Preparatoria','CBTIS','2228899001','2229900112','roberto19@gmail.com','/fotos/roberto19.jpg',0,NULL),(27,'Guerrero','Ibarra','Sergio','GUIS920228HDFRRR20','1992-02-28','CDMX','Mexicana',73.00,1.74,4,'Empleado','Secundaria','N/A','2221011121','2222122232','sergio20@gmail.com','/fotos/sergio20.jpg',0,NULL),(28,'Navarro','Fuentes','Arturo','NAFA890917HPLRNT21','1989-09-17','Puebla','Mexicana',78.00,1.80,1,'Empleado','Preparatoria','BUAP','2223233343','2224344454','arturo21@gmail.com','/fotos/arturo21.jpg',0,NULL),(29,'Rios','Molina','Julio','RIMJ910624HDFTRR22','1991-06-24','CDMX','Mexicana',75.00,1.77,2,'Empleado','Secundaria','N/A','2225455565','2226566676','julio22@gmail.com','/fotos/julio22.jpg',0,NULL),(30,'Ponce','Escobar','Diego','POED950805HPLRNS23','1995-08-05','Puebla','Mexicana',68.00,1.71,3,'Estudiante','Universidad','BUAP','2227677787','2228788898','diego23@gmail.com','/fotos/diego23.jpg',0,NULL),(31,'Luna','Miranda','Emilio','LUME930109HDFNRR24','1993-01-09','CDMX','Mexicana',79.50,1.82,4,'Empleado','Preparatoria','UNAM','2229899009','2220900110','emilio24@gmail.com','/fotos/emilio24.jpg',0,NULL),(32,'Salinas','Cabrera','Alberto','SACA880417HPLTRR25','1988-04-17','Puebla','Mexicana',84.00,1.85,1,'Empleado','Secundaria','N/A','2221113344','2222224455','alberto25@gmail.com','/fotos/alberto25.jpg',0,NULL),(33,'Padilla','Leon','Rafael','PALR920701HDFRNL26','1992-07-01','CDMX','Mexicana',76.00,1.79,2,'Empleado','Preparatoria','IPN','2223335566','2224446677','rafael26@gmail.com','/fotos/rafael26.jpg',0,NULL),(34,'Flores','Fragoso','Gerardo','FOFG900210HPLRGR27','1990-02-10','Puebla','Mexicana',82.00,1.83,3,'Estudiante','Universidad','BUAP','2225557788','2226668899','gerardo27@gmail.com','/fotos/gerardo27.jpg',0,NULL),(35,'Solis','Mejia','Ivan','SOMI940918HDFLJV28','1994-09-18','CDMX','Mexicana',70.00,1.73,4,'Empleado','Preparatoria','CONALEP','2227779900','2228880011','ivan28@gmail.com','/fotos/ivan28.jpg',0,NULL),(36,'Cruz','Rangel','Mario','CURM910529HPLRNL29','1991-05-29','Puebla','Mexicana',77.00,1.78,1,'Empleado','Secundaria','N/A','2229991122','2220002233','mario29@gmail.com','/fotos/mario29.jpg',0,NULL),(37,'Nieto','Quintero','Pablo','NIQP950313HDFTRR30','1995-03-13','CDMX','Mexicana',69.00,1.72,2,'Estudiante','Universidad','IPN','2221114455','2222225566','pablo30@gmail.com','/fotos/pablo30.jpg',0,NULL),(38,'GUZMÁN','AHUATZI','ADRIANA NICOLE','GUAA000000000MTK65','2005-01-19','TLAXCALA','MEXICANA',65.00,165.00,NULL,NULL,NULL,NULL,NULL,'2461798228','ady.nicole20@gmail.com',NULL,1,'NINGUNA'),(41,'GUZMÁN','AHUATZI','ADRIANA NICOLE','GUAA000067900MTK87','2005-01-19','TLAXCALA','MEXICANA',65.00,165.00,NULL,NULL,NULL,NULL,NULL,'2461798228','ady.nicole20@gmail.com',NULL,1,'NINGUNA');
/*!40000 ALTER TABLE `jugador` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `jugador_liga`
--

DROP TABLE IF EXISTS `jugador_liga`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `jugador_liga` (
  `id_jugador` bigint NOT NULL COMMENT 'Referencia al jugador',
  `id_liga` bigint NOT NULL COMMENT 'Referencia a la liga',
  `fecha_inscripcion` date NOT NULL COMMENT 'Fecha en que se inscribió el jugador en la liga',
  PRIMARY KEY (`id_jugador`,`id_liga`),
  KEY `jugador_liga_id_liga_foreign` (`id_liga`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jugador_liga`
--

LOCK TABLES `jugador_liga` WRITE;
/*!40000 ALTER TABLE `jugador_liga` DISABLE KEYS */;
/*!40000 ALTER TABLE `jugador_liga` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `liga`
--

DROP TABLE IF EXISTS `liga`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `liga` (
  `id_liga` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la liga',
  `nombre_liga` varchar(100) NOT NULL COMMENT 'Nombre de la liga deportiva',
  `categoria` varchar(50) DEFAULT NULL COMMENT 'Categoría de la liga (primera, juvenil, etc.)',
  PRIMARY KEY (`id_liga`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `liga`
--

LOCK TABLES `liga` WRITE;
/*!40000 ALTER TABLE `liga` DISABLE KEYS */;
INSERT INTO `liga` VALUES (1,'Liga AMIVD Puebla','Primera Fuerza'),(2,'Liga AMIVD Cholula','Juvenil'),(3,'Liga AMIVD Atlixco','Veteranos');
/*!40000 ALTER TABLE `liga` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `notificacion`
--

DROP TABLE IF EXISTS `notificacion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `notificacion` (
  `id_notificacion` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la notificación',
  `id_usuario` bigint NOT NULL COMMENT 'Referencia al usuario que recibe la notificación',
  `mensaje` text NOT NULL COMMENT 'Texto del mensaje de la notificación',
  `fecha` datetime NOT NULL COMMENT 'Fecha y hora en que se envió la notificación',
  `leida` tinyint(1) DEFAULT '0' COMMENT 'Indica si el usuario ya leyó la notificación',
  `fecha_eliminacion` datetime DEFAULT NULL COMMENT 'Fecha en que se puede eliminar automáticamente la notificación',
  PRIMARY KEY (`id_notificacion`),
  KEY `notificacion_id_usuario_foreign` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=13 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notificacion`
--

LOCK TABLES `notificacion` WRITE;
/*!40000 ALTER TABLE `notificacion` DISABLE KEYS */;
INSERT INTO `notificacion` VALUES (1,5,'Inicio de sesión desde el sistema.','2026-04-23 08:58:26',1,NULL),(2,5,'Inicio de sesión desde el sistema.','2026-04-23 09:21:05',1,NULL),(3,4,'Inicio de sesión desde el sistema.','2026-04-23 14:44:22',0,NULL),(4,5,'Inicio de sesión desde el sistema.','2026-04-23 16:03:36',1,NULL),(5,5,'Inicio de sesión desde el sistema.','2026-04-30 14:08:35',1,NULL),(6,4,'Inicio de sesión desde el sistema.','2026-04-30 14:20:10',0,NULL),(7,4,'Inicio de sesión desde el sistema.','2026-04-30 14:58:29',0,NULL),(8,4,'Inicio de sesión desde el sistema.','2026-04-30 18:34:44',0,NULL),(9,5,'Inicio de sesión desde el sistema.','2026-05-04 16:10:06',1,NULL),(10,5,'Registro de jugador (ref: #38) rechazado. Motivo: esta mal el registro','2026-05-04 16:30:59',0,NULL),(11,5,'Registro de jugador (ref: #41) autorizado correctamente.','2026-05-04 16:31:10',0,NULL),(12,5,'Registro de jugador (ref: #38) rechazado. Motivo: f f','2026-05-04 16:31:20',0,NULL);
/*!40000 ALTER TABLE `notificacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pago`
--

DROP TABLE IF EXISTS `pago`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pago` (
  `id_pago` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del pago',
  `id_afiliacion` bigint NOT NULL COMMENT 'Referencia a la afiliación que se está pagando',
  `fecha_pago` date NOT NULL COMMENT 'Fecha en que se realizó el pago',
  `estatus` enum('Pendiente','Completado','Cancelado') DEFAULT 'Pendiente' COMMENT 'Estatus del pago',
  `metodo_pago` varchar(50) DEFAULT NULL COMMENT 'Método de pago utilizado (efectivo, transferencia, etc.)',
  `referencia` varchar(100) DEFAULT NULL COMMENT 'Referencia o número de comprobante del pago',
  PRIMARY KEY (`id_pago`),
  KEY `pago_id_afiliacion_foreign` (`id_afiliacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pago`
--

LOCK TABLES `pago` WRITE;
/*!40000 ALTER TABLE `pago` DISABLE KEYS */;
/*!40000 ALTER TABLE `pago` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `registro_externo`
--

DROP TABLE IF EXISTS `registro_externo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `registro_externo` (
  `id_registro` int NOT NULL AUTO_INCREMENT,
  `tipo` enum('Jugador','Arbitro','Entrenador') NOT NULL,
  `nombre_completo` varchar(150) NOT NULL,
  `curp` varchar(18) DEFAULT NULL,
  `email` varchar(150) DEFAULT NULL,
  `telefono` varchar(15) DEFAULT NULL,
  `fecha_nacimiento` date DEFAULT NULL,
  `fecha_registro` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `estatus` enum('Pendiente','Revisado') DEFAULT 'Pendiente',
  PRIMARY KEY (`id_registro`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `registro_externo`
--

LOCK TABLES `registro_externo` WRITE;
/*!40000 ALTER TABLE `registro_externo` DISABLE KEYS */;
/*!40000 ALTER TABLE `registro_externo` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sanciones`
--

DROP TABLE IF EXISTS `sanciones`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sanciones` (
  `id_sancion` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la sanción',
  `id_jugador` bigint NOT NULL COMMENT 'Referencia al jugador sancionado',
  `id_liga` bigint NOT NULL COMMENT 'Referencia a la liga donde se aplica la sanción',
  `tipo_sancion` varchar(50) NOT NULL COMMENT 'Tipo de sanción (suspensión, multa, etc.)',
  `fecha_sancion` date NOT NULL COMMENT 'Fecha en que se aplicó la sanción',
  `fecha_fin_sancion` date DEFAULT NULL COMMENT 'Fecha en que termina la sanción (si aplica)',
  `motivo` text NOT NULL COMMENT 'Motivo o razón de la sanción',
  `estatus` varchar(20) DEFAULT 'Activa' COMMENT 'Estatus de la sanción (Activa, Cumplida, Anulada)',
  PRIMARY KEY (`id_sancion`),
  KEY `sanciones_id_jugador_foreign` (`id_jugador`),
  KEY `sanciones_id_liga_foreign` (`id_liga`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sanciones`
--

LOCK TABLES `sanciones` WRITE;
/*!40000 ALTER TABLE `sanciones` DISABLE KEYS */;
/*!40000 ALTER TABLE `sanciones` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sesion`
--

DROP TABLE IF EXISTS `sesion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sesion` (
  `id_sesion` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador único de la sesión',
  `id_usuario` bigint NOT NULL COMMENT 'Referencia al usuario que inició sesión',
  `token` varchar(255) NOT NULL COMMENT 'Token único de la sesión',
  `fecha_inicio` datetime NOT NULL COMMENT 'Fecha y hora en que inició la sesión',
  `fecha_expiracion` datetime NOT NULL COMMENT 'Fecha y hora en que expira la sesión',
  `ip_address` varchar(45) DEFAULT NULL COMMENT 'Dirección IP desde donde se conectó el usuario',
  PRIMARY KEY (`id_sesion`),
  UNIQUE KEY `token` (`token`),
  KEY `sesion_id_usuario_foreign` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sesion`
--

LOCK TABLES `sesion` WRITE;
/*!40000 ALTER TABLE `sesion` DISABLE KEYS */;
/*!40000 ALTER TABLE `sesion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tutor_padre`
--

DROP TABLE IF EXISTS `tutor_padre`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tutor_padre` (
  `id_tutor` bigint NOT NULL AUTO_INCREMENT,
  `id_jugador` bigint DEFAULT NULL,
  `nombre_completo` varchar(150) DEFAULT NULL,
  `celular` varchar(20) DEFAULT NULL,
  `correo_electronico` varchar(150) DEFAULT NULL,
  `curp_tutor` varchar(18) DEFAULT NULL,
  `fotografia_ine` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id_tutor`),
  KEY `id_jugador` (`id_jugador`),
  CONSTRAINT `tutor_padre_ibfk_1` FOREIGN KEY (`id_jugador`) REFERENCES `jugador` (`id_jugador`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tutor_padre`
--

LOCK TABLES `tutor_padre` WRITE;
/*!40000 ALTER TABLE `tutor_padre` DISABLE KEYS */;
INSERT INTO `tutor_padre` VALUES (1,33,'ALAN FERNADEZ HERNANDEZ','2468575896','alan@gmail.com','',NULL),(2,34,'MIGUEL VARGAS LOPEZ','2465815679','migue@gmail.com','',NULL);
/*!40000 ALTER TABLE `tutor_padre` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id_usuario` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del usuario',
  `nombre_usuario` varchar(50) NOT NULL COMMENT 'Nombre de usuario para iniciar sesión',
  `password` varchar(255) NOT NULL COMMENT 'Contraseña del usuario (se guarda encriptada)',
  `rol` enum('Presidente','Secretaria','Administrador','Delegado') DEFAULT NULL,
  `nombre_completo` varchar(150) NOT NULL COMMENT 'Nombre completo del usuario',
  `email` varchar(150) DEFAULT NULL COMMENT 'Correo electrónico del usuario',
  `activo` tinyint(1) DEFAULT '1' COMMENT 'Indica si el usuario puede acceder al sistema',
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `nombre_usuario` (`nombre_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
INSERT INTO `usuario` VALUES (4,'presidente','$2a$12$HUyRb/B1lta9kTU7./XfSeNjUUJIEYi72x.7lLKwtt5y6WanPF3na','Presidente','Juan Andres','andrefivb@hotmail.com',1),(5,'Nick','$2b$12$EDRIQNOKrR64BgePiTSFc.agFozxvMBVTQ/hErWdfIuU/iz02xN6e','Administrador','Nicole Guzman','andircio98@gmail.com',1);
/*!40000 ALTER TABLE `usuario` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `vigencias`
--

DROP TABLE IF EXISTS `vigencias`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `vigencias` (
  `id_vigencia` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del tipo de vigencia',
  `descripcion` varchar(50) NOT NULL COMMENT 'Descripción de la vigencia (Anual, Semestral)',
  PRIMARY KEY (`id_vigencia`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vigencias`
--

LOCK TABLES `vigencias` WRITE;
/*!40000 ALTER TABLE `vigencias` DISABLE KEYS */;
INSERT INTO `vigencias` VALUES (1,'Anual'),(2,'Semestral');
/*!40000 ALTER TABLE `vigencias` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-05-04 17:07:37
