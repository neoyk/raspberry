-- MySQL dump 10.13  Distrib 5.5.40, for debian-linux-gnu (armv7l)
--
-- Host: localhost    Database: raspberry
-- ------------------------------------------------------
-- Server version	5.5.40-0+wheezy1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `address`
--

DROP TABLE IF EXISTS `address`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `address` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `mac` char(20) NOT NULL,
  `ipv4` varchar(200) NOT NULL,
  `asn4` varchar(200) NOT NULL,
  `ipv6` varchar(400) NOT NULL,
  `asn6` varchar(200) NOT NULL,
  `time` datetime DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `avgbw4`
--

DROP TABLE IF EXISTS `avgbw4`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `avgbw4` (
  `mac` varchar(20) NOT NULL,
  `time` datetime NOT NULL,
  `avgbw` double NOT NULL,
  `type` varchar(50) NOT NULL,
  KEY `selection` (`mac`,`time`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `avgbw6`
--

DROP TABLE IF EXISTS `avgbw6`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `avgbw6` (
  `mac` varchar(20) NOT NULL,
  `time` datetime NOT NULL,
  `avgbw` double NOT NULL,
  `type` varchar(50) NOT NULL,
  KEY `selection` (`mac`,`time`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `avgloss4`
--

DROP TABLE IF EXISTS `avgloss4`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `avgloss4` (
  `mac` varchar(20) NOT NULL,
  `time` datetime NOT NULL,
  `avgloss` double NOT NULL,
  `type` varchar(50) NOT NULL,
  KEY `selection` (`mac`,`time`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `avgloss6`
--

DROP TABLE IF EXISTS `avgloss6`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `avgloss6` (
  `mac` varchar(20) NOT NULL,
  `time` datetime NOT NULL,
  `avgloss` double NOT NULL,
  `type` varchar(50) NOT NULL,
  KEY `selection` (`mac`,`time`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `avgrtt4`
--

DROP TABLE IF EXISTS `avgrtt4`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `avgrtt4` (
  `mac` varchar(20) NOT NULL,
  `time` datetime NOT NULL,
  `avgrtt` double NOT NULL,
  `type` varchar(50) NOT NULL,
  KEY `selection` (`mac`,`time`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `avgrtt6`
--

DROP TABLE IF EXISTS `avgrtt6`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `avgrtt6` (
  `mac` varchar(20) NOT NULL,
  `time` datetime NOT NULL,
  `avgrtt` double NOT NULL,
  `type` varchar(50) NOT NULL,
  KEY `selection` (`mac`,`time`,`type`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ipv4server`
--

DROP TABLE IF EXISTS `ipv4server`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ipv4server` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `webdomain` varchar(800) NOT NULL,
  `asn` varchar(14) DEFAULT NULL,
  `ip` varchar(16) DEFAULT NULL,
  `location` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `longitude` float DEFAULT NULL,
  `latitude` float DEFAULT NULL,
  `crawl` int(11) DEFAULT '1',
  `slow` int(11) DEFAULT '0',
  `error` int(11) DEFAULT '0',
  `aspath` varchar(100) DEFAULT NULL,
  `pagesize` double DEFAULT '1000000',
  `performance` varchar(200) DEFAULT NULL,
  `bandwidth` double DEFAULT '0',
  `type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `ip` (`ip`,`webdomain`)
) ENGINE=MyISAM AUTO_INCREMENT=2440 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `ipv6server`
--

DROP TABLE IF EXISTS `ipv6server`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `ipv6server` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `webdomain` varchar(1000) DEFAULT NULL,
  `asn` varchar(14) DEFAULT NULL,
  `ip` varchar(40) DEFAULT NULL,
  `location` varchar(100) CHARACTER SET utf8 COLLATE utf8_unicode_ci DEFAULT NULL,
  `longitude` float DEFAULT NULL,
  `latitude` float DEFAULT NULL,
  `crawl` int(11) DEFAULT '1',
  `slow` int(11) DEFAULT '0',
  `error` int(11) DEFAULT '0',
  `aspath` varchar(100) DEFAULT NULL,
  `pagesize` double DEFAULT '1000000',
  `performance` varchar(200) DEFAULT NULL,
  `bandwidth` double DEFAULT '0',
  `type` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `webdomain` (`webdomain`)
) ENGINE=MyISAM AUTO_INCREMENT=646 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `web_perf4`
--

DROP TABLE IF EXISTS `web_perf4`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `web_perf4` (
  `mac` varchar(20) DEFAULT NULL,
  `id` int(11) NOT NULL,
  `ip` varchar(16) NOT NULL,
  `asn` varchar(20) DEFAULT NULL,
  `webdomain` varchar(500) NOT NULL,
  `time` datetime NOT NULL,
  `bandwidth` double NOT NULL,
  `pagesize` double NOT NULL,
  `latency` float NOT NULL,
  `lossrate` float DEFAULT NULL,
  `actual_loss` float DEFAULT NULL,
  `maxbw` double DEFAULT NULL,
  `type` varchar(50) DEFAULT NULL,
  UNIQUE KEY `search` (`id`,`time`,`mac`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `web_perf6`
--

DROP TABLE IF EXISTS `web_perf6`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `web_perf6` (
  `mac` varchar(20) NOT NULL,
  `id` int(11) NOT NULL,
  `ip` varchar(40) NOT NULL,
  `asn` varchar(20) DEFAULT NULL,
  `webdomain` varchar(500) NOT NULL,
  `time` datetime NOT NULL,
  `bandwidth` double NOT NULL,
  `pagesize` double NOT NULL,
  `latency` float NOT NULL,
  `lossrate` float DEFAULT NULL,
  `actual_loss` float DEFAULT NULL,
  `maxbw` double DEFAULT NULL,
  `type` varchar(50) DEFAULT NULL,
  UNIQUE KEY `search` (`id`,`time`,`mac`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2014-11-26 20:04:41
