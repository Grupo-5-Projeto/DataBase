<h1>📌 Banco de Dados - UPA Connect</h1>

<h2>📋 Sobre o Projeto</h2>

Este repositório contém o esquema do banco de dados utilizado no projeto UPA Connect, incluindo o seu script. </br>

<h2>🏗 Estrutura do Banco de Dados</h2>

    SGBD: MySQL

    Modelo: Relacional

    Padrão de nomenclatura: snake_case para tabelas e colunas

<h2>📂 Entidades</h2>

<ul>
  <li><b><span style="font-size: 14px;">upa</span></b> 🏥 - Contém as informações de uma determinada UPA.</li>
  <li><b><span style="font-size: 14px;">endereco</span></b> 📍 - Contém endereços que podem pertencer tanto às UPAs quanto aos pacientes.</li>
  <li><b><span style="font-size: 14px;">temperatura_ambiente</span></b> 🌡️ - Dados coletados do sensor de temperatura do ambiente da UPA.</li>
  <li><b><span style="font-size: 14px;">camera_computacional</span></b> 🎥 - Dados coletados do sensor da câmera computacional, com o principal objetivo de saber a quantidade de pessoas no ambiente.</li>
  <li><b><span style="font-size: 14px;">umidade</span></b> 💧 - Dados coletados do sensor de umidade da UPA.</li>
  <li><b><span style="font-size: 14px;">paciente</span></b> 🧑‍⚕️ - Contém informações pessoais de pacientes.</li>
  <li><b><span style="font-size: 14px;">temperatura_paciente</span></b> 🤒 - Dados coletados do sensor que mede a temperatura do paciente ao entrar na UPA.</li>
  <li><b><span style="font-size: 14px;">oximetro</span></b> 🩸 - Dados coletados da oxigenação do sangue do paciente assim que entrar na UPA.</li>
  <li><b><span style="font-size: 14px;">biometria</span></b> 🖐️ - Dados da biometria digital dos pacientes, para que a UPA possa fazer um atendimento mais veloz.</li>
</ul>
