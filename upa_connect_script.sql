DROP DATABASE IF EXISTS upa_connect;
CREATE DATABASE upa_connect;

CREATE USER IF NOT EXISTS 'admin_upa_connect'@'%' IDENTIFIED BY 'urubu100';
GRANT ALL PRIVILEGES ON upa_connect.* TO 'admin_upa_connect'@'%';
FLUSH PRIVILEGES;

USE upa_connect;

CREATE TABLE endereco (
id_endereco INT PRIMARY KEY AUTO_INCREMENT,
cep CHAR(9),
rua VARCHAR(70),
bairro VARCHAR(45),
numero INT,
cidade VARCHAR(45),
estado VARCHAR(45),
latitude DECIMAL(10,8),
longitude DECIMAL(11,8),
entidade_referenciada CHAR(1)
);

CREATE TABLE upa (
id_upa INT PRIMARY KEY AUTO_INCREMENT,
nome VARCHAR(90),
cnpj CHAR(14),
telefone CHAR(11),
capacidade_atendimento INT,
fk_endereco INT,
FOREIGN KEY (fk_endereco) REFERENCES endereco(id_endereco)
);

CREATE TABLE temperatura_ambiente (
id_temperatura_ambiente INT PRIMARY KEY AUTO_INCREMENT, 
data_hora DATETIME,
valor DECIMAL(4,2),
fk_upa INT,
FOREIGN KEY (fk_upa) REFERENCES upa(id_upa)
);

CREATE TABLE umidade (
id_umidade INT PRIMARY KEY AUTO_INCREMENT, 
data_hora DATETIME,
valor DECIMAL(5,2),
fk_upa INT,
FOREIGN KEY (fk_upa) REFERENCES upa(id_upa)
);

CREATE TABLE camera_computacional (
id_camera INT PRIMARY KEY AUTO_INCREMENT, 
data_hora DATETIME,
qtd_pessoas INT,
fk_upa INT,
FOREIGN KEY (fk_upa) REFERENCES upa(id_upa)
);

CREATE TABLE paciente (
id_paciente INT PRIMARY KEY AUTO_INCREMENT,
nome VARCHAR(45),
cpf CHAR(11),
data_nascimento DATE,
carteira_sus CHAR(15),
fk_endereco INT, 
FOREIGN KEY (fk_endereco) REFERENCES endereco(id_endereco),
fk_upa INT,
FOREIGN KEY (fk_upa) REFERENCES upa(id_upa)
);

CREATE TABLE temperatura_paciente (
id_temperatura_paciente INT PRIMARY KEY AUTO_INCREMENT, 
data_hora DATETIME,
valor DECIMAL(4,2),
fk_paciente INT,
FOREIGN KEY (fk_paciente) REFERENCES paciente(id_paciente)
);

CREATE TABLE oximetro (
id_oximetro INT PRIMARY KEY AUTO_INCREMENT, 
data_hora DATETIME,
valor DECIMAL(5,2),
fk_paciente INT,
FOREIGN KEY (fk_paciente) REFERENCES paciente(id_paciente)
);

CREATE TABLE biometria (
id_biometria INT PRIMARY KEY AUTO_INCREMENT, 
data_hora DATETIME,
biometria_hash VARCHAR(64),
fk_paciente INT,
FOREIGN KEY (fk_paciente) REFERENCES paciente(id_paciente)
);