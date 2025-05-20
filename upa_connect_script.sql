DROP DATABASE IF EXISTS upa_connect;
CREATE DATABASE upa_connect;

-- CREATE USER IF NOT EXISTS 'admin_upa_connect'@'%' IDENTIFIED BY 'urubu100';
-- GRANT ALL PRIVILEGES ON upa_connect.* TO 'admin_upa_connect'@'%';
-- FLUSH PRIVILEGES;

USE upa_connect;

CREATE TABLE Upa (
    id_upa INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(60),
    capacidade_atendimento INT,
    latitude DOUBLE,
    longitude DOUBLE
);

CREATE TABLE Paciente (
    id_paciente INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(45),
    cpf CHAR(11),
    data_nascimento DATE,
    biometria BLOB
);

CREATE TABLE Sensor (
    id_sensor INT PRIMARY KEY AUTO_INCREMENT,
    nome_sensor VARCHAR(45)
);

CREATE TABLE UnidadeDeMedida (
    id_unidade_de_medida INT PRIMARY KEY AUTO_INCREMENT,
    unidade_de_medida VARCHAR(45)
);

CREATE TABLE HistoricoSensor (
    id_registro INT PRIMARY KEY AUTO_INCREMENT,
    data_hora DATETIME,
    valor DECIMAL(5,2),
    fk_upa INT,
    FOREIGN KEY (fk_upa) REFERENCES Upa(id_upa),
    fk_paciente INT,
    FOREIGN KEY (fk_paciente) REFERENCES Paciente(id_paciente),
    fk_sensor INT,
    FOREIGN KEY (fk_sensor) REFERENCES Sensor(id_sensor),
    fk_unid_medida INT,
    FOREIGN KEY (fk_unid_medida) REFERENCES UnidadeDeMedida(id_unidade_de_medida)
);
