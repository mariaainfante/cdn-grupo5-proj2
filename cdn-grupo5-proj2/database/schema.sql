-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema conatus
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema conatus
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `conatus` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci ;
USE `conatus` ;

-- -----------------------------------------------------
-- Table `conatus`.`cliente`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `conatus`.`cliente` (
  `id_cliente` INT NOT NULL AUTO_INCREMENT,
  `nm_cliente` VARCHAR(120) NOT NULL,
  `contato_cliente` VARCHAR(190) NULL DEFAULT NULL COMMENT 'RF01. Anulavel: o documento nao declara obrigatoriedade.',
  PRIMARY KEY (`id_cliente`))
ENGINE = InnoDB
AUTO_INCREMENT = 11
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci
COMMENT = 'RD01. Registro de identificacao e contato; sem faixa de investimento.';


-- -----------------------------------------------------
-- Table `conatus`.`projeto`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `conatus`.`projeto` (
  `id_projeto` INT NOT NULL AUTO_INCREMENT,
  `id_cliente` INT NOT NULL,
  `nm_projeto` VARCHAR(120) NOT NULL,
  `desc_projeto` TEXT NOT NULL,
  `estado_projeto` ENUM('planejado', 'em_andamento', 'concluido') NOT NULL DEFAULT 'planejado' COMMENT 'RF22: Planejado, Em andamento, Concluido.',
  `criado_em` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `inicio_previsto` DATE NULL DEFAULT NULL,
  `fim_previsto` DATE NULL DEFAULT NULL,
  PRIMARY KEY (`id_projeto`),
  INDEX `ix_projeto_cliente` (`id_cliente` ASC),
  INDEX `ix_projeto_estado` (`estado_projeto` ASC),
  CONSTRAINT `fk_projeto_cliente`
    FOREIGN KEY (`id_cliente`)
    REFERENCES `conatus`.`cliente` (`id_cliente`))
ENGINE = InnoDB
AUTO_INCREMENT = 11
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci
COMMENT = 'RD04. Cliente 1:N Projeto (RN19). Sem FK para propriedade.';


-- -----------------------------------------------------
-- Table `conatus`.`propriedade`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `conatus`.`propriedade` (
  `id_propiedade` INT NOT NULL AUTO_INCREMENT,
  `id_projeto` INT NOT NULL,
  `nm_propriedade` VARCHAR(120) NOT NULL,
  `tp_propriedade` VARCHAR(45) NULL DEFAULT NULL,
  `endereco_propriedade` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id_propiedade`),
  UNIQUE INDEX `uq_propriedade_id_projeto` (`id_propiedade` ASC, `id_projeto` ASC) COMMENT '\'\'\'Alvo das FKs compostas de localizacao (RN20).\'\'\'',
  INDEX `ix_propriedade_projeto` (`id_projeto` ASC),
  CONSTRAINT `fk_propriedade_projeto`
    FOREIGN KEY (`id_projeto`)
    REFERENCES `conatus`.`projeto` (`id_projeto`))
ENGINE = InnoDB
AUTO_INCREMENT = 11
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci
COMMENT = 'RD03/RF02. Projeto 1:N Propriedade (RN19). Nome obrigatorio; tipo e endereco opcionais (D6).';


-- -----------------------------------------------------
-- Table `conatus`.`ambiente`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `conatus`.`ambiente` (
  `id_ambiente` INT NOT NULL AUTO_INCREMENT,
  `id_propiedade` INT NOT NULL,
  `nm_ambiente` VARCHAR(120) NOT NULL,
  `tp_ambiente` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`id_ambiente`),
  UNIQUE INDEX `uq_ambiente_id_propriedade` (`id_ambiente` ASC, `id_propiedade` ASC) COMMENT '\'\'\'Alvo das FKs compostas de localizacao (RN20).\'\'\'',
  INDEX `ix_ambiente_propriedade` (`id_propiedade` ASC),
  CONSTRAINT `fk_ambiente_propriedade`
    FOREIGN KEY (`id_propiedade`)
    REFERENCES `conatus`.`propriedade` (`id_propiedade`))
ENGINE = InnoDB
AUTO_INCREMENT = 11
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci
COMMENT = 'RD05/RF03. Propriedade 1:N Ambiente. Sem project_id (derivado pela propriedade). Nome obrigatorio; tipo opcional (D6).';


-- -----------------------------------------------------
-- Table `conatus`.`usuario`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `conatus`.`usuario` (
  `id_user` INT NOT NULL AUTO_INCREMENT,
  `nm_user` VARCHAR(120) NOT NULL,
  `email_user` VARCHAR(190) NOT NULL,
  `password_hash` VARCHAR(255) NOT NULL COMMENT 'Hash gerado pelo framework (RNF07). Nunca a senha em texto.',
  `papel_global` ENUM('gestor', 'padrao') NOT NULL DEFAULT 'padrao' COMMENT 'RN21/D4: somente gestor cadastra clientes e cria projetos. Nao da acesso a projetos (RN03).',
  PRIMARY KEY (`id_user`),
  UNIQUE INDEX `uq_usuario_email` (`email_user` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 11
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci
COMMENT = 'RD02. Conta de usuario. Cliente nao tem conta.';


-- -----------------------------------------------------
-- Table `conatus`.`vinculo_projeto_usuario`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `conatus`.`vinculo_projeto_usuario` (
  `id_vinculo` INT NOT NULL AUTO_INCREMENT,
  `id_projeto` INT NOT NULL,
  `id_user` INT NOT NULL,
  `papel_no_projeto` ENUM('manager', 'technician', 'architect', 'commercial') NOT NULL COMMENT 'D4: papel dentro do projeto; define o que pode ser editado nele.',
  `ativo` TINYINT(1) NOT NULL DEFAULT '1' COMMENT 'D3: retirada de participante = ativo 0. Vinculo desativado preserva autoria, mas nao autoriza acesso (RN03).',
  PRIMARY KEY (`id_vinculo`),
  UNIQUE INDEX `uq_vinculo_projeto_usuario` (`id_projeto` ASC, `id_user` ASC),
  UNIQUE INDEX `uq_vinculo_id_projeto` (`id_vinculo` ASC, `id_projeto` ASC) COMMENT '\'\'\'Alvo das FKs compostas de autoria: garante que o autor pertence ao projeto do registro.\'\'\'',
  INDEX `ix_vinculo_usuario` (`id_user` ASC),
  CONSTRAINT `fk_vinculo_projeto`
    FOREIGN KEY (`id_projeto`)
    REFERENCES `conatus`.`projeto` (`id_projeto`),
  CONSTRAINT `fk_vinculo_usuario`
    FOREIGN KEY (`id_user`)
    REFERENCES `conatus`.`usuario` (`id_user`))
ENGINE = InnoDB
AUTO_INCREMENT = 11
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci
COMMENT = 'RD02. N:N Usuario-Projeto; (project_id, user_id) unico. Nunca excluir vinculo com historico.';


-- -----------------------------------------------------
-- Table `conatus`.`evento_historico`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `conatus`.`evento_historico` (
  `id_evento` INT NOT NULL AUTO_INCREMENT,
  `id_projeto` INT NOT NULL,
  `id_vinculo` INT NOT NULL COMMENT 'D3: vinculo usuario-projeto. Deve ser do mesmo projeto (FK composta).',
  `id_propiedade` INT NULL DEFAULT NULL COMMENT 'Nivel propriedade ou ambiente. NULL = evento de nivel projeto.',
  `id_ambiente` INT NULL DEFAULT NULL COMMENT 'Nivel ambiente (exige propriedade_id). NULL = nivel projeto ou propriedade.',
  `acao_evento` VARCHAR(120) NOT NULL COMMENT 'Titulo curto (RF46) ou acao de auditoria (RF37).',
  `desc_evento` TEXT NOT NULL COMMENT 'Texto do membro (manual) ou texto gerado pelo sistema (automatico). Sem antes/depois (D2).',
  `criado_em` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Atribuido pelo servidor (RN16). Precisao de microssegundos para ordenar a linha do tempo.',
  PRIMARY KEY (`id_evento`),
  INDEX `ix_evento_timeline` (`id_projeto` ASC, `criado_em` DESC),
  INDEX `ix_evento_autor` (`id_vinculo` ASC, `id_projeto` ASC),
  INDEX `ix_evento_propriedade` (`id_propiedade` ASC, `id_projeto` ASC),
  INDEX `ix_evento_ambiente` (`id_ambiente` ASC, `id_propiedade` ASC),
  CONSTRAINT `fk_evento_ambiente`
    FOREIGN KEY (`id_ambiente` , `id_propiedade`)
    REFERENCES `conatus`.`ambiente` (`id_ambiente` , `id_propiedade`),
  CONSTRAINT `fk_evento_autor`
    FOREIGN KEY (`id_vinculo` , `id_projeto`)
    REFERENCES `conatus`.`vinculo_projeto_usuario` (`id_vinculo` , `id_projeto`),
  CONSTRAINT `fk_evento_projeto`
    FOREIGN KEY (`id_projeto`)
    REFERENCES `conatus`.`projeto` (`id_projeto`),
  CONSTRAINT `fk_evento_propriedade`
    FOREIGN KEY (`id_propiedade` , `id_projeto`)
    REFERENCES `conatus`.`propriedade` (`id_propiedade` , `id_projeto`))
ENGINE = InnoDB
AUTO_INCREMENT = 11
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci
COMMENT = 'RD17. Append-only (RN15). Nivel do evento: so project_id = projeto; + propriedade_id = propriedade; + ambiente_id = ambiente (RN20).';


-- -----------------------------------------------------
-- Table `conatus`.`comentario`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `conatus`.`comentario` (
  `id_comentario` INT NOT NULL AUTO_INCREMENT,
  `id_evento` INT NOT NULL,
  `id_vinculo` INT NOT NULL COMMENT 'D3: vinculo usuario-projeto. Deve ser do projeto do evento (verificar na aplicacao).',
  `texto_comentario` TEXT NOT NULL,
  `criado_em` DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) COMMENT 'Atribuido pelo servidor (RN16).',
  PRIMARY KEY (`id_comentario`),
  INDEX `ix_comentario_evento` (`id_evento` ASC, `criado_em` ASC),
  INDEX `ix_comentario_autor` (`id_vinculo` ASC),
  CONSTRAINT `fk_comentario_autor`
    FOREIGN KEY (`id_vinculo`)
    REFERENCES `conatus`.`vinculo_projeto_usuario` (`id_vinculo`),
  CONSTRAINT `fk_comentario_evento`
    FOREIGN KEY (`id_evento`)
    REFERENCES `conatus`.`evento_historico` (`id_evento`))
ENGINE = InnoDB
AUTO_INCREMENT = 11
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci
COMMENT = 'RD20/RF47. Append-only (RN15). Pertence a um evento; projeto e local sao os do evento.';


-- -----------------------------------------------------
-- Table `conatus`.`sensor`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `conatus`.`sensor` (
  `id_sensor` INT NOT NULL AUTO_INCREMENT,
  `nm_sensor` VARCHAR(120) NOT NULL,
  `desc_sensor` VARCHAR(255) NULL DEFAULT NULL,
  `preco_sensor` DECIMAL(10,2) NOT NULL,
  PRIMARY KEY (`id_sensor`))
ENGINE = InnoDB
AUTO_INCREMENT = 11
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci
COMMENT = 'Catalogo de sensores e seus precos de referencia.';


-- -----------------------------------------------------
-- Table `conatus`.`projeto_sensor`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `conatus`.`projeto_sensor` (
  `id_projeto_sensor` INT NOT NULL AUTO_INCREMENT,
  `id_projeto` INT NOT NULL,
  `id_sensor` INT NOT NULL,
  `quantidade` INT NOT NULL DEFAULT '1',
  `preco_unitario` DECIMAL(10,2) NOT NULL COMMENT 'Preco aplicado ao projeto no momento do orcamento.',
  PRIMARY KEY (`id_projeto_sensor`),
  UNIQUE INDEX `uq_projeto_sensor` (`id_projeto` ASC, `id_sensor` ASC),
  INDEX `ix_projeto_sensor_sensor` (`id_sensor` ASC),
  CONSTRAINT `fk_projeto_sensor_projeto`
    FOREIGN KEY (`id_projeto`)
    REFERENCES `conatus`.`projeto` (`id_projeto`),
  CONSTRAINT `fk_projeto_sensor_sensor`
    FOREIGN KEY (`id_sensor`)
    REFERENCES `conatus`.`sensor` (`id_sensor`))
ENGINE = InnoDB
AUTO_INCREMENT = 11
DEFAULT CHARACTER SET = utf8mb4
COLLATE = utf8mb4_0900_ai_ci
COMMENT = 'Sensores usados em cada projeto, com quantidade e preco aplicado.';

USE `conatus` ;

-- -----------------------------------------------------
-- Placeholder table for view `conatus`.`vw_orcamento_projeto`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `conatus`.`vw_orcamento_projeto` (`id_projeto` INT, `nm_projeto` INT, `nm_cliente` INT, `valor_orcamento` INT);

-- -----------------------------------------------------
-- View `conatus`.`vw_orcamento_projeto`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `conatus`.`vw_orcamento_projeto`;
USE `conatus`;
CREATE  OR REPLACE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `conatus`.`vw_orcamento_projeto` AS select `p`.`id_projeto` AS `id_projeto`,`p`.`nm_projeto` AS `nm_projeto`,`c`.`nm_cliente` AS `nm_cliente`,coalesce(sum((`ps`.`quantidade` * `ps`.`preco_unitario`)),0.00) AS `valor_orcamento` from ((`conatus`.`projeto` `p` join `conatus`.`cliente` `c` on((`c`.`id_cliente` = `p`.`id_cliente`))) left join `conatus`.`projeto_sensor` `ps` on((`ps`.`id_projeto` = `p`.`id_projeto`))) group by `p`.`id_projeto`,`p`.`nm_projeto`,`c`.`nm_cliente`;
USE `conatus`;

DELIMITER $$
USE `conatus`$$
CREATE
DEFINER=`root`@`localhost`
TRIGGER `conatus`.`trg_evento_historico_bd`
BEFORE DELETE ON `conatus`.`evento_historico`
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'RN15: evento_historico e append-only (DELETE negado).';
END$$

USE `conatus`$$
CREATE
DEFINER=`root`@`localhost`
TRIGGER `conatus`.`trg_evento_historico_bu`
BEFORE UPDATE ON `conatus`.`evento_historico`
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'RN15: evento_historico e append-only (UPDATE negado).';
END$$

USE `conatus`$$
CREATE
DEFINER=`root`@`localhost`
TRIGGER `conatus`.`trg_comentario_bd`
BEFORE DELETE ON `conatus`.`comentario`
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'RN15: comentario e append-only (DELETE negado).';
END$$

USE `conatus`$$
CREATE
DEFINER=`root`@`localhost`
TRIGGER `conatus`.`trg_comentario_bu`
BEFORE UPDATE ON `conatus`.`comentario`
FOR EACH ROW
BEGIN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'RN15: comentario e append-only (UPDATE negado).';
END$$


DELIMITER ;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
