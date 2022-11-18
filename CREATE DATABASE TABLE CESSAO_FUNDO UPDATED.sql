-- Copiando estrutura do banco de dados para edesoft-db
CREATE DATABASE IF NOT EXISTS `edesoft_db` DEFAULT CHARACTER SET latin1 COLLATE latin1_swedish_ci;
USE `edesoft_db`;

-- Copiando estrutura para tabela edesoft-db.cessao_fundo
CREATE TABLE IF NOT EXISTS `cessao_fundo` (
  `ID_CESSAO` int(22) NOT NULL AUTO_INCREMENT,
  `ORIGINADOR` varchar(250) NOT NULL,
  `DOC_ORIGINADOR` varchar(50) NOT NULL,
  `CEDENTE` varchar(250) NOT NULL,
  `DOC_CEDENTE` varchar(50) NOT NULL,
  `CCB` int(22) NOT NULL,
  `ID_EXTERNO` int(22) NOT NULL,
  `CLIENTE` varchar(250) NOT NULL,
  `CPF_CNPJ` varchar(50) NOT NULL,
  `ENDERECO` varchar(250) NOT NULL,
  `CEP` varchar(50) NOT NULL,
  `CIDADE` varchar(250) NOT NULL,
  `UF` varchar(50) NOT NULL,
  `VALOR_DO_EMPRESTIMO` decimal(10,2) NOT NULL,
  `VALOR_PARCELA` decimal(10,2) NOT NULL,
  `TOTAL_PARCELAS` int(22) NOT NULL,
  `PARCELA` int(22) NOT NULL,
  `DATA_DE_EMISSAO` date NOT NULL,
  `DATA_DE_VENCIMENTO` date NOT NULL,
  `PRECO_DE_AQUISICAO` decimal(10,2) NOT NULL,
  PRIMARY KEY (`ID_CESSAO`),
  UNIQUE KEY `ID_EXTERNO` (`ID_EXTERNO`)
) DEFAULT CHARSET=latin1 COLLATE=latin1_swedish_ci;
