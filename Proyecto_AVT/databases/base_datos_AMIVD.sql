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
  PRIMARY KEY (`id_autorizacion`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `autorizacion_pendiente`
--

LOCK TABLES `autorizacion_pendiente` WRITE;
/*!40000 ALTER TABLE `autorizacion_pendiente` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cat_estado`
--

LOCK TABLES `cat_estado` WRITE;
/*!40000 ALTER TABLE `cat_estado` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cat_municipio`
--

LOCK TABLES `cat_municipio` WRITE;
/*!40000 ALTER TABLE `cat_municipio` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `direccion`
--

LOCK TABLES `direccion` WRITE;
/*!40000 ALTER TABLE `direccion` DISABLE KEYS */;
/*!40000 ALTER TABLE `direccion` ENABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `expediente`
--

LOCK TABLES `expediente` WRITE;
/*!40000 ALTER TABLE `expediente` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `jugador`
--

LOCK TABLES `jugador` WRITE;
/*!40000 ALTER TABLE `jugador` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `liga`
--

LOCK TABLES `liga` WRITE;
/*!40000 ALTER TABLE `liga` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `notificacion`
--

LOCK TABLES `notificacion` WRITE;
/*!40000 ALTER TABLE `notificacion` DISABLE KEYS */;
/*!40000 ALTER TABLE `notificacion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `padre_tutor`
--

DROP TABLE IF EXISTS `padre_tutor`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `padre_tutor` (
  `id_tutor` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del tutor',
  `id_jugador` bigint NOT NULL COMMENT 'Referencia al jugador que está bajo tutela',
  `nombre_completo` varchar(150) NOT NULL COMMENT 'Nombre completo del tutor',
  `celular` varchar(20) DEFAULT NULL COMMENT 'Teléfono celular del tutor',
  `correo_electronico` varchar(150) DEFAULT NULL COMMENT 'Correo electrónico del tutor',
  `curp_tutor` varchar(18) NOT NULL COMMENT 'CURP del tutor',
  `fotografia_ine` varchar(255) DEFAULT NULL COMMENT 'Ruta donde se guarda la foto del INE del tutor',
  PRIMARY KEY (`id_tutor`),
  KEY `padre_tutor_id_jugador_foreign` (`id_jugador`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `padre_tutor`
--

LOCK TABLES `padre_tutor` WRITE;
/*!40000 ALTER TABLE `padre_tutor` DISABLE KEYS */;
/*!40000 ALTER TABLE `padre_tutor` ENABLE KEYS */;
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
-- Table structure for table `usuario`
--

DROP TABLE IF EXISTS `usuario`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuario` (
  `id_usuario` bigint NOT NULL AUTO_INCREMENT COMMENT 'Identificador único del usuario',
  `nombre_usuario` varchar(50) NOT NULL COMMENT 'Nombre de usuario para iniciar sesión',
  `password` varchar(255) NOT NULL COMMENT 'Contraseña del usuario (se guarda encriptada)',
  `rol` enum('Presidente','Secretaria') NOT NULL COMMENT 'Rol del usuario (Presidente o Secretaria)',
  `nombre_completo` varchar(150) NOT NULL COMMENT 'Nombre completo del usuario',
  `email` varchar(150) DEFAULT NULL COMMENT 'Correo electrónico del usuario',
  `activo` tinyint(1) DEFAULT '1' COMMENT 'Indica si el usuario puede acceder al sistema',
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `nombre_usuario` (`nombre_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuario`
--

LOCK TABLES `usuario` WRITE;
/*!40000 ALTER TABLE `usuario` DISABLE KEYS */;
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
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `vigencias`
--

LOCK TABLES `vigencias` WRITE;
/*!40000 ALTER TABLE `vigencias` DISABLE KEYS */;
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

-- Dump completed on 2026-04-05 20:17:28
