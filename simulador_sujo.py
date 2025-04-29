import random
import pymysql
import math
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('pt_BR')

# Configurações do banco de dados
CONFIG_BD = {
    'host': 'localhost',
    'user': 'admin_upa_connect',
    'password': 'urubu100',
    'database': 'upa_connect'
}

# Parâmetros da simulação
PERIODO_SIMULACAO_HORAS = 24
INTERVALO_MINUTOS = 5
NUMERO_AMOSTRAS = (PERIODO_SIMULACAO_HORAS * 60) // INTERVALO_MINUTOS

# Variáveis para controlar falhas (sequências de valores nulos)
falha_temp_paciente = 0
falha_oximetro = 0
falha_temp_ambiente = 0
falha_umidade = 0
falha_visao = 0

# Variáveis para armazenar o último valor para simulação gradual
ultima_temp_ambiente = None
ultima_umidade = None

def gerar_valor_sujo(valor_original, taxa_ruido=0.02, prob_faltante=0.05, desvio_outlier=3, minimo=None, maximo=None, prob_iniciar_falha=0.005, duracao_max_falha=8):
    """Adiciona ruído, valores faltantes, outliers e valores negativos a um valor, com limites."""
    if random.random() < prob_iniciar_falha:
        return random.randint(1, duracao_max_falha) # Retorna a duração da falha

    valor_sujo = valor_original + random.uniform(-taxa_ruido * abs(valor_original), taxa_ruido * abs(valor_original))

    if random.random() < prob_faltante and not isinstance(valor_sujo, int):
        return None

    return valor_sujo

def gerar_leituras_proximas(valor_central, num_leituras=3, desvio_max=0.2, prob_nulo=0.1):
    """Gera uma lista de leituras próximas a um valor central, com chance de serem nulas."""
    leituras = []
    for _ in range(num_leituras):
        if random.random() < prob_nulo:
            leituras.append(None)
        else:
            desvio = random.uniform(-desvio_max, desvio_max)
            leituras.append(round(valor_central + desvio, 1))
    return leituras

A = 0.001129148
B = 0.000234125
C = 0.0000000876741
R_REF = 10000  # Resistor de referência (10kΩ)
VCC = 3.3  # Tensão de alimentação do circuito
ADC_MAX = 1023  # Resolução de 10 bits (0-1023)

def gerar_temp_corporal_suja_multipla():
    global falha_temp_paciente
    prob_outlier_temp = 0.05 # Aumentando a probabilidade de outliers de temperatura

    if falha_temp_paciente > 0:
        falha_temp_paciente -= 1
        return [None] * 3
    else:
        if random.random() < prob_outlier_temp:
            # Gerar um outlier de temperatura significativo
            tipo_outlier = random.random()
            if tipo_outlier < 0.33:
                outlier = round(random.uniform(-10.0, 33.9), 1) # Temperaturas muito baixas
            elif tipo_outlier < 0.66:
                outlier = round(random.uniform(38.0, 99.0), 1) # Temperaturas muito altas
            else:
                outlier = round(random.uniform(46.0, 60.0), 1) # Temperaturas extremamente altas
            return [outlier, round(outlier + random.uniform(-0.5, 0.5), 1), round(outlier + random.uniform(-0.5, 0.5), 1)]
        else:

            adc_value = random.randint(610, 670)  # Intervalo ajustado
            V_sensor = (adc_value / ADC_MAX) * VCC
            R_ntc = R_REF * ((VCC / V_sensor) - 1)

            T_kelvin = 1 / (A + B * math.log(R_ntc) + C * (math.log(R_ntc))**3)
            T_celsius = T_kelvin - 273.15

            temp_celsius_original = round(T_celsius, 1) # Limitar a 1 casa decimal
            primeiro_resultado = gerar_valor_sujo(temp_celsius_original, taxa_ruido=0.01, prob_faltante=0.3, desvio_outlier=4, minimo=30.0, maximo=45.0, prob_iniciar_falha=0.003, duracao_max_falha=12)
            if isinstance(primeiro_resultado, int):
                falha_temp_paciente = primeiro_resultado
                return [None] * 3
            elif primeiro_resultado is None:
                return [None, round(random.uniform(36.0, 37.5), 1), round(random.uniform(36.0, 37.5), 1)]
            else:
                return [round(primeiro_resultado, 1), round(primeiro_resultado + random.uniform(-0.1, 0.1), 1), round(primeiro_resultado + random.uniform(-0.1, 0.1), 1)]

def gerar_oximetro_sujo_multipla():
    global falha_oximetro
    prob_outlier_oximetro = 0.01

    if falha_oximetro > 0:
        falha_oximetro -= 1
        return [None] * 3
    else:
        if random.random() < prob_outlier_oximetro:
            if random.random() < 0.5:
                outlier = round(random.uniform(50.0, 85.0), 0)
            else:
                outlier = round(random.uniform(101.0, 110.0), 0)
            return [outlier, round(outlier + random.uniform(-1, 1), 0), round(outlier + random.uniform(-1, 1), 0)]
        else:
            V_sensor = random.uniform(1.6, 2.6)  # Aumentado para ampliar a faixa
            SpO2 = 94 + (V_sensor - 2.0) * (10 / 1.0)  # Ajuste para cobrir 90-99%
            SpO2 = max(90.0, min(SpO2, 99.0))  # Garante os limites
            
            spo2_original = round(SpO2, 1) # Limitar a 1 casa decimal
            primeiro_resultado = gerar_valor_sujo(spo2_original, taxa_ruido=0.005, prob_faltante=0.3, minimo=70.0, maximo=105.0, prob_iniciar_falha=0.004, duracao_max_falha=10)
            if isinstance(primeiro_resultado, int):
                falha_oximetro = primeiro_resultado
                return [None] * 3
            elif primeiro_resultado is None:
                return [None, round(random.uniform(95.0, 99.0), 0), round(random.uniform(95.0, 99.0), 0)]
            else:
                return [round(primeiro_resultado, 0), round(primeiro_resultado + random.uniform(-1, 1), 0), round(primeiro_resultado + random.uniform(-1, 1), 0)]


def gerar_temp_ambiente_suja():
    global falha_temp_ambiente, ultima_temp_ambiente
    intervalo_15_minutos = 15
    agora = datetime.now()
    minutos_decorridos = (agora.hour * 60 + agora.minute) % intervalo_15_minutos
    prob_outlier = 0.02 # Aumentando a probabilidade de outlier de temperatura

    if falha_temp_ambiente > 0:
        falha_temp_ambiente -= 1
        return None
    else:
        if random.random() < prob_outlier:
            # Gerar um outlier de temperatura discrepante (máximo 99.9)
            tipo_outlier = random.random()
            if tipo_outlier < 0.25:
                return round(random.uniform(40.0, 99.9), 1) # Limitar a 1 casa decimal
            elif tipo_outlier < 0.5:
                return round(random.uniform(-25.0, 12.0), 1) # Limitar a 1 casa decimal
            elif tipo_outlier < 0.75:
                return round(random.uniform(60.0, 99.9), 1) # Limitar a 1 casa decimal
            else:
                return round(random.uniform(-50.0, -26.0), 1) # Limitar a 1 casa decimal

        A = 1.009249522e-03
        B = 2.378405444e-04
        C = 2.019202697e-07

        R = random.uniform(8000, 12000)

        T_kelvin = 1 / (A + B * math.log(R) + C * (math.log(R))**3)

        if minutos_decorridos == 0 or ultima_temp_ambiente is None:
            temp_celsius_original = round(T_kelvin - 273.15, 1) # Limitar a 1 casa decimal
            ultima_temp_ambiente_temp = gerar_valor_sujo(temp_celsius_original, taxa_ruido=0.01, prob_faltante=0.05, minimo=15.0, maximo=35.0, prob_iniciar_falha=0.001, duracao_max_falha=10)
            if isinstance(ultima_temp_ambiente_temp, int):
                falha_temp_ambiente = ultima_temp_ambiente_temp
                ultima_temp_ambiente = None
                return None
            ultima_temp_ambiente = round(ultima_temp_ambiente_temp, 1) if ultima_temp_ambiente_temp is not None else None # Limitar a 1 casa decimal
        elif ultima_temp_ambiente is not None:
            variacao = random.uniform(-0.2, 0.2)
            temp_atual = ultima_temp_ambiente + variacao
            ultima_temp_ambiente_temp = gerar_valor_sujo(round(temp_atual, 1), taxa_ruido=0.005, prob_faltante=0.02, minimo=15.0, maximo=35.0)
            if isinstance(ultima_temp_ambiente_temp, int):
                falha_temp_ambiente = ultima_temp_ambiente_temp
                ultima_temp_ambiente = None
                return None
            ultima_temp_ambiente = round(ultima_temp_ambiente_temp, 1) if ultima_temp_ambiente_temp is not None else None # Limitar a 1 casa decimal
        return ultima_temp_ambiente

def gerar_umidade_suja():
    global falha_umidade, ultima_umidade
    intervalo_15_minutos = 15
    agora = datetime.now()
    minutos_decorridos = (agora.hour * 60 + agora.minute) % intervalo_15_minutos
    prob_outlier = 0.02 # Aumentando a probabilidade de outlier de umidade

    if falha_umidade > 0:
        falha_umidade -= 1
        return None
    else:
        if random.random() < prob_outlier:
            # Gerar um outlier de umidade discrepante (negativos e maiores que 100)
            if random.random() < 0.33:
                return round(random.uniform(61.0, 120.0), 1) # Limitar a 1 casa decimal
            elif random.random() < 0.66:
                return round(random.uniform(-30.0, 39.0), 1) # Limitar a 1 casa decimal
            else:
                return round(random.uniform(121.0, 150.0), 1) # Limitar a 1 casa decimal
            
        V_sensor = random.uniform(1, 3)
        V_max = 3.3
        RH = (V_sensor / V_max) * 100

        if minutos_decorridos == 0 or ultima_umidade is None:
            umidade_original = RH
            ultima_umidade_temp = gerar_valor_sujo(umidade_original, taxa_ruido=0.01, prob_faltante=0.05, minimo=30.0, maximo=70.0, prob_iniciar_falha=0.001, duracao_max_falha=10)
            if isinstance(ultima_umidade_temp, int):
                falha_umidade = ultima_umidade_temp
                ultima_umidade = None
                return None
            ultima_umidade = round(ultima_umidade_temp, 1) if ultima_umidade_temp is not None else None # Limitar a 1 casa decimal
        elif ultima_umidade is not None:
            variacao = random.uniform(-1.0, 1.0)
            umidade_atual = ultima_umidade + variacao
            ultima_umidade_temp = gerar_valor_sujo(round(umidade_atual, 1), taxa_ruido=0.005, prob_faltante=0.02, minimo=30.0, maximo=70.0)
            if isinstance(ultima_umidade_temp, int):
                falha_umidade = ultima_umidade_temp
                ultima_umidade = None
                return None
            ultima_umidade = round(ultima_umidade_temp, 1) if ultima_umidade_temp is not None else None # Limitar a 1 casa decimal
        return ultima_umidade

pessoas = random.randint(40, 150)

def gerar_contagem_pessoas_suja():
    global falha_visao, pessoas
    if falha_visao > 0:
        falha_visao -= 1
        return None
    else:
        variacao = random.randint(-1, 1) 
        pessoas += variacao
        pessoas_suja = max(0, min(pessoas, 200))
        resultado = gerar_valor_sujo(pessoas_suja, taxa_ruido=0.015, prob_faltante=0.06, desvio_outlier=2, minimo=0, maximo=200, prob_iniciar_falha=0.001, duracao_max_falha=15)
        if isinstance(resultado, int):
            falha_visao = resultado
            return None
        return round(resultado, 0) if resultado is not None else None # Limitar a 0 casa decimal (inteiro)

def inserir_dados(cursor, tabela, dados):
    """Insere um registro na tabela especificada."""
    campos = ', '.join(dados.keys())
    valores = ', '.join(['%s'] * len(dados))
    sql = f"INSERT INTO {tabela} ({campos}) VALUES ({valores})"
    try:
        cursor.execute(sql, list(dados.values()))
        return True
    except pymysql.err.DataError as e:
        print(f"Erro ao inserir em {tabela}: {e}")
        print(f"Dados problemáticos: {dados}")
        return False

def gerar_biometria_r503():
    """Simula a leitura de uma biometria do sensor R503."""
    tamanho_template = random.randint(300, 500)
    return random.randbytes(tamanho_template)

def inserir_biometria(cursor, data_hora, biometria_data, fk_paciente):
    """Insere os dados de biometria na tabela."""
    sql = "INSERT INTO biometria (data_hora, biometria, fk_paciente) VALUES (%s, %s, %s)"
    try:
        cursor.execute(sql, (data_hora, biometria_data, fk_paciente))
        return True
    except pymysql.err.Error as e:
        print(f"Erro ao inserir biometria para paciente {fk_paciente}: {e}")
        return False

def buscar_biometrias(cursor):
    """Busca todas as biometrias existentes no banco."""
    cursor.execute("SELECT biometria FROM biometria")
    return [row[0] for row in cursor.fetchall() if row[0]]

def buscar_paciente_por_biometria(cursor, biometria):
    """Busca o ID do paciente pela biometria."""
    cursor.execute("SELECT fk_paciente FROM biometria WHERE biometria = %s", (biometria,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def inserir_paciente(cursor, nome, cpf, data_nascimento, carteira_sus, fk_endereco, fk_upa):
    """Insere um novo paciente no banco de dados."""
    sql = "INSERT INTO paciente (nome, cpf, data_nascimento, carteira_sus, fk_endereco, fk_upa) VALUES (%s, %s, %s, %s, %s, %s)"
    try:
        cursor.execute(sql, (nome, cpf, data_nascimento, carteira_sus, fk_endereco, fk_upa))
        print(f"PACIENTE INSERIDO com ID: {cursor.lastrowid}")
        return cursor.lastrowid
    except pymysql.err.Error as e:
        print(f"Erro ao inserir paciente: {e}")
        return None

def inserir_endereco(cursor, cep, rua, bairro, numero, cidade, estado, latitude, longitude, entidade_referenciada):
    """Insere um novo endereço no banco de dados."""
    sql = "INSERT INTO endereco (cep, rua, bairro, numero, cidade, estado, latitude, longitude, entidade_referenciada) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
    try:
        cursor.execute(sql, (cep, rua, bairro, numero, cidade, estado, latitude, longitude, entidade_referenciada))
        return cursor.lastrowid
    except pymysql.err.Error as e:
        print(f"Erro ao inserir endereço: {e}")
        return None

def formatar_cep(cep):
    # Remove quaisquer espaços ou caracteres não numéricos
    cep = ''.join(filter(str.isdigit, cep))

    # Verifica se o CEP tem o tamanho correto
    if len(cep) != 8:
        raise ValueError("O CEP deve conter exatamente 8 dígitos.")

    # Adiciona o hífen no local correto
    return f"{cep[:5]}-{cep[5:]}"

def gerar_endereco_sao_paulo():
    """Gera um endereço aleatório na cidade de São Paulo."""
    cep = formatar_cep(fake.postcode())
    rua = fake.street_name()
    bairro = fake.bairro()
    numero = fake.building_number()
    cidade = "São Paulo"
    estado = "SP"
    latitude = fake.latitude()
    longitude = fake.longitude()
    return cep, rua, bairro, numero, cidade, estado, latitude, longitude, 'P' # 'P' para Paciente

def extrair_numeros_cpf(cpf):
    return ''.join(char for char in cpf if char.isdigit())

try:
    conexao = pymysql.connect(**CONFIG_BD)
    cursor = conexao.cursor()

    NUMERO_ITERACOES = (PERIODO_SIMULACAO_HORAS * 60) // INTERVALO_MINUTOS # Garante que o loop rode para cada intervalo de 5 minutos

    for i in range(NUMERO_ITERACOES):
        agora = datetime.now() - timedelta(minutes=INTERVALO_MINUTOS * (NUMERO_ITERACOES - 1 - i))
        data_hora_registro = agora.strftime('%Y-%m-%d %H:%M:%S')

        # Simula a chegada de um novo paciente (com uma certa probabilidade a cada 5 minutos)
        chance_novo_paciente = 0.3 # Ajuste essa probabilidade conforme a necessidade
        if random.random() < chance_novo_paciente:
            print(f"\nSimulando chegada de novo paciente às {data_hora_registro}.")
            # Processar como um novo paciente
            print("Gerando endereço, biometria e inserindo no banco.")
            # Gerar endereço
            cep, rua, bairro, numero, cidade, estado, latitude, longitude, entidade = gerar_endereco_sao_paulo()
            endereco_id = inserir_endereco(cursor, cep, rua, bairro, numero, cidade, estado, latitude, longitude, entidade)
            if endereco_id:
                # Gerar dados do paciente e inserir
                novo_paciente_id = inserir_paciente(cursor, fake.name(), extrair_numeros_cpf(fake.cpf()), fake.date_of_birth(minimum_age=18, maximum_age=80), fake.ssn(), endereco_id, random.randint(1, 34))
                if novo_paciente_id:
                    # Gerar biometria e inserir (uma vez por paciente)
                    nova_biometria = gerar_biometria_r503()
                    inserir_sucesso_biometria = inserir_biometria(cursor, data_hora_registro, nova_biometria, novo_paciente_id)
                    if inserir_sucesso_biometria:
                        print(f"  Biometria inserida para paciente {novo_paciente_id} às {data_hora_registro}.")
                    else:
                        print(f"  Erro ao inserir biometria para paciente {novo_paciente_id} às {data_hora_registro}.")
                else:
                    print("Erro ao inserir novo paciente.")
            else:
                print("Erro ao inserir novo endereço.")
        else:
            # Se não chegou um novo paciente, apenas simular outras atividades ou aguardar o próximo intervalo
            print(f"Nenhum novo paciente cadastrado às {data_hora_registro}.")

    conexao.commit()
    print(f"\nProcessamento de biometria (simulando novo paciente a cada 5 minutos) concluído para {NUMERO_ITERACOES} iterações.")

    # Buscar todos os IDs dos pacientes cadastrados
    cursor.execute("SELECT id_paciente FROM paciente")
    ids_pacientes = [row[0] for row in cursor.fetchall()]

    if not ids_pacientes:
        print("Nenhum paciente encontrado na base de dados para gerar dados de sensores.")
    else:
        print("Gerando e inserindo três registros de oximetria e temperatura (com valores próximos) para um paciente aleatório a cada 5 minutos...")
        agora_simulacao = datetime.now()
        for i in range(NUMERO_AMOSTRAS):
            timestamp_sensor = agora_simulacao - timedelta(minutes=INTERVALO_MINUTOS * (NUMERO_AMOSTRAS - 1 - i))
            data_hora_sensor = timestamp_sensor.strftime('%Y-%m-%d %H:%M:%S')

            # Selecionar um paciente aleatório da lista de pacientes cadastrados
            paciente_aleatorio_id = random.choice(ids_pacientes)
            print(f"Processando dados de sensores para paciente ID: {paciente_aleatorio_id} às {data_hora_sensor}")

            # Resetar as variáveis de falha para este paciente
            falha_temp_paciente = 0
            falha_oximetro = 0

            # Gerar e inserir temperatura corporal para o paciente aleatório (3 valores próximos)
            temps = gerar_temp_corporal_suja_multipla()
            for j, temp_valor in enumerate(temps):
                dados_temp = {'data_hora': timestamp_sensor - timedelta(seconds=j), 'valor': temp_valor, 'fk_paciente': paciente_aleatorio_id}
                inserir_dados(cursor, 'temperatura_paciente', dados_temp)
                print(f"  Temperatura {j+1}: {temp_valor}°C")

            # Gerar e inserir oximetria para o paciente aleatório (3 valores próximos)
            oxis = gerar_oximetro_sujo_multipla()
            for j, oxi_valor in enumerate(oxis):
                dados_oxi = {'data_hora': timestamp_sensor - timedelta(seconds=j), 'valor': oxi_valor, 'fk_paciente': paciente_aleatorio_id}
                inserir_dados(cursor, 'oximetro', dados_oxi)
                print(f"  Oximetria {j+1}: {oxi_valor}%")

        conexao.commit()
        print("Três registros de oximetria e temperatura gerados e inseridos para um paciente aleatório a cada 5 minutos.")

    # Buscar todos os IDs das UPAs cadastradas
    cursor.execute("SELECT id_upa FROM upa")
    ids_upas = [row[0] for row in cursor.fetchall()]

    if not ids_upas:
        print("Nenhuma UPA encontrada na base de dados.")
    else:
        print("Gerando dados da UPA (temperatura, umidade e câmera) para todas as UPAs por 24 horas...") # Alterado para 24 horas para consistência
        agora_upa = datetime.now()
        for id_upa in ids_upas:
            print(f"Processando dados da UPA ID: {id_upa}")
            # Resetar as variáveis de falha para cada UPA
            falha_temp_ambiente = 0
            falha_umidade = 0
            falha_visao = 0
            ultima_temp_ambiente = None
            ultima_umidade = None

            for i in range(NUMERO_AMOSTRAS):
                timestamp = agora_upa - timedelta(minutes=INTERVALO_MINUTOS * (NUMERO_AMOSTRAS - 1 - i))
                data_hora_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')

                # Dados da UPA - Temperatura Ambiente
                temp_ambiente = gerar_temp_ambiente_suja()
                dados_temp_ambiente = {'data_hora': data_hora_str, 'valor': temp_ambiente, 'fk_upa': id_upa}
                inserir_dados(cursor, 'temperatura_ambiente', dados_temp_ambiente)

                # Dados da UPA - Umidade
                umidade = gerar_umidade_suja()
                dados_umidade = {'data_hora': data_hora_str, 'valor': umidade, 'fk_upa': id_upa}
                inserir_dados(cursor, 'umidade', dados_umidade)

                # Dados da UPA - Câmera Computacional
                qtd_pessoas = gerar_contagem_pessoas_suja()
                dados_camera = {'data_hora': data_hora_str, 'qtd_pessoas': qtd_pessoas, 'fk_upa': id_upa}
                inserir_dados(cursor, 'camera_computacional', dados_camera)

        print("Dados da UPA (temperatura, umidade e câmera) para todas as UPAs por 24 horas inseridos.")

    conexao.commit()

except pymysql.err.Error as e:
    print(f"Erro de banco de dados: {e}")
finally:
    if 'conexao' in locals() and conexao.open:
        cursor.close()
        conexao.close()
        print("Conexão ao banco de dados fechada.")