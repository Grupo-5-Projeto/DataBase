-- selects uteis
SELECT 
	u.id_upa as id_upa,
    u.nome AS nome_upa,
    p.nome AS nome_paciente,
    tp.data_hora AS data_temp,
    tp.valor AS temperatura,
    o.data_hora AS data_oxi,
    o.valor AS oximetria
FROM paciente p
JOIN temperatura_paciente tp ON p.id_paciente = tp.fk_paciente
JOIN oximetro o ON p.id_paciente = o.fk_paciente
JOIN upa u ON p.fk_upa = u.id_upa
WHERE u.id_upa = 1;

SELECT 
    u.id_upa,
    u.nome AS nome_upa,
    t.tempo_espera,
    e.rua,
    e.numero,
    e.bairro,
    e.cidade,
    e.estado
FROM upa u
LEFT JOIN tempo_espera t ON u.id_upa = t.fk_upa
LEFT JOIN endereco e ON u.fk_endereco = e.id_endereco;


-- visualização dos dados gerados pelas simulações
select * from temperatura_ambiente;
select * from umidade;

select * from temperatura_paciente;
select * from oximetro;

select * from camera_computacional;

-- visualização dos valores fora do range
select * from temperatura_ambiente where valor < 22 or valor > 24;
select * from umidade where valor < 40 or valor > 60;
select * from temperatura_paciente where valor < 36 or valor > 37.5;
select * from oximetro where valor < 90 or valor > 100;

-- valotes fora do range da temp do ambiente -> média da temperatura a cada 30 minutos
SELECT 
  FLOOR((id_temperatura_ambiente - 1) / 6) AS grupo,
  ROUND(AVG(valor),1) AS media
FROM 
  temperatura_ambiente
WHERE 
  valor < 22 or valor > 24
GROUP BY 
  grupo
ORDER BY 
  grupo;

-- qtd d valores fora do range da temp do ambiente gerados a cada 30 min
SELECT COUNT(*) AS qtd_gerada
FROM 
(SELECT 
  FLOOR((id_temperatura_ambiente - 1) / 6) AS grupo,
  ROUND(AVG(valor),1) AS media
FROM 
  temperatura_ambiente
WHERE 
  valor < 22 or valor > 24
GROUP BY 
  grupo
ORDER BY 
  grupo
) AS subquery;

SELECT 
  FLOOR((id_umidade - 1) / 6) AS grupo,
  ROUND(AVG(valor),1) AS media
FROM 
  umidade
WHERE 
  valor < 40 or valor > 60
GROUP BY 
  grupo
ORDER BY 
  grupo;
  
SELECT COUNT(*) AS qtd_gerada
FROM 
(SELECT 
  FLOOR((id_umidade - 1) / 6) AS grupo,
  ROUND(AVG(valor),1) AS media
FROM 
  umidade
WHERE 
  valor < 40 or valor > 60
GROUP BY 
  grupo
ORDER BY 
  grupo
) AS subquery;