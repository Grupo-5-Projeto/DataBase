import random
import pymysql
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

# Parâmetros da simulação (agora relevantes apenas para os dados da UPA)
PERIODO_SIMULACAO_HORAS = 48
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

    return valor_sujo # Removemos a lógica de outlier daqui, trataremos nas funções específicas

def gerar_temp_corporal_suja():
    global falha_temp_paciente
    if falha_temp_paciente > 0:
        falha_temp_paciente -= 1
        return None
    else:
        temp_celsius_original = round(random.uniform(36.0, 37.5), 1) # Limitar a 1 casa decimal
        resultado = gerar_valor_sujo(temp_celsius_original, taxa_ruido=0.01, prob_faltante=0.1, desvio_outlier=4, minimo=30.0, maximo=45.0, prob_iniciar_falha=0.003, duracao_max_falha=12)
        if isinstance(resultado, int):
            falha_temp_paciente = resultado
            return None
        return round(resultado, 1) if resultado is not None else None # Limitar a 1 casa decimal

def gerar_oximetro_sujo():
    global falha_oximetro
    prob_outlier_oximetro = 0.01 # Probabilidade de gerar um outlier no oximetro

    if falha_oximetro > 0:
        falha_oximetro -= 1
        return None
    else:
        if random.random() < prob_outlier_oximetro:
            # Gerar um outlier de oximetro
            if random.random() < 0.5:
                return round(random.uniform(50.0, 85.0), 0) # Limitar a 0 casa decimal (inteiro)
            else:
                return round(random.uniform(101.0, 110.0), 0) # Limitar a 0 casa decimal (inteiro)
        else:
            spo2_original = round(random.uniform(95.0, 99.0), 0) # Limitar a 0 casa decimal (inteiro)
            resultado = gerar_valor_sujo(spo2_original, taxa_ruido=0.005, prob_faltante=0.07, minimo=70.0, maximo=105.0, prob_iniciar_falha=0.004, duracao_max_falha=10)
            if isinstance(resultado, int):
                falha_oximetro = resultado
                return None
            return round(resultado, 0) if resultado is not None else None # Limitar a 0 casa decimal

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

        if minutos_decorridos == 0 or ultima_temp_ambiente is None:
            temp_celsius_original = round(random.uniform(22.0, 24.0), 1) # Limitar a 1 casa decimal
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
        if minutos_decorridos == 0 or ultima_umidade is None:
            umidade_original = round(random.uniform(40.0, 60.0), 1) # Limitar a 1 casa decimal
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
        variacao = random.randint(-3, 3)
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
    except pymysql.err.DataError as e:
        print(f"Erro ao inserir em {tabela}: {e}")
        print(f"Dados problemáticos: {dados}")
        return False
    return True

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

    NUMERO_ITERACOES = 50

    for _ in range(NUMERO_ITERACOES):
        # Simula a decisão se o paciente é cadastrado ou não (50% para cada)
        eh_cadastrado = random.random() < 0.5
        agora = datetime.now()
        data_hora_registro = agora.strftime('%Y-%m-%d %H:%M:%S')

        if eh_cadastrado:
            print("Paciente cadastrado.")
        else:
            # Processar como um novo paciente
            print("Paciente não cadastrado. Gerando endereço, biometria e inserindo no banco.")
            # Gerar endereço
            cep, rua, bairro, numero, cidade, estado, latitude, longitude, entidade = gerar_endereco_sao_paulo()
            endereco_id = inserir_endereco(cursor, cep, rua, bairro, numero, cidade, estado, latitude, longitude, entidade)
            if endereco_id:
                # Gerar dados do paciente e inserir
                novo_paciente_id = inserir_paciente(cursor, fake.name(), extrair_numeros_cpf(fake.cpf()), fake.date_of_birth(minimum_age=18, maximum_age=80), fake.ssn(), endereco_id, random.randint(1, 34))
                if novo_paciente_id:
                    # Gerar biometria e inserir
                    nova_biometria = gerar_biometria_r503()
                    inserir_sucesso_biometria = inserir_biometria(cursor, data_hora_registro, nova_biometria, novo_paciente_id)
                    if inserir_sucesso_biometria:
                        print(f"Novo paciente (ID: {novo_paciente_id}) cadastrado com biometria.")
                    else:
                        print(f"Erro ao inserir biometria para o novo paciente (ID: {novo_paciente_id}).")
                else:
                    print("Erro ao inserir novo paciente.")
            else:
                print("Erro ao inserir novo endereço.")

    conexao.commit()
    print(f"\nProcessamento de biometria concluído para {NUMERO_ITERACOES} iterações.")

    conexao.commit()
    print("Dados de biometria inseridos com sucesso.")


    cursor.execute("SELECT id_paciente FROM paciente")
    ids_pacientes = [row[0] for row in cursor.fetchall()]

    if not ids_pacientes:
        print("Nenhum paciente encontrado na base de dados.")
    elif len(ids_pacientes) != 49:
        print(f"Atenção: O número de pacientes na base de dados ({len(ids_pacientes)}) é diferente do esperado (49).")
    else:
        print("Gerando dados para 48 horas da UPA (temperatura, umidade e câmera)...")
        agora = datetime.now()

        for i in range(NUMERO_AMOSTRAS):
            timestamp = agora - timedelta(minutes=INTERVALO_MINUTOS * (NUMERO_AMOSTRAS - 1 - i))
            data_hora_str = timestamp.strftime('%Y-%m-%d %H:%M:%S')

            # Dados da UPA
            temp_ambiente = gerar_temp_ambiente_suja()
            dados_temp_ambiente = {'data_hora': data_hora_str, 'valor': temp_ambiente, 'fk_upa': 1}
            inserir_sucesso_temp_ambiente = inserir_dados(cursor, 'temperatura_ambiente', dados_temp_ambiente)
            # if inserir_sucesso_temp_ambiente:
            #     print(f"UPA Temp Ambiente [{data_hora_str}]: {temp_ambiente}°C")

            umidade = gerar_umidade_suja()
            dados_umidade = {'data_hora': data_hora_str, 'valor': umidade, 'fk_upa': 1}
            inserir_sucesso_umidade = inserir_dados(cursor, 'umidade', dados_umidade)
            # if inserir_sucesso_umidade:
            #     print(f"UPA Umidade [{data_hora_str}]: {umidade}%")

            qtd_pessoas = gerar_contagem_pessoas_suja()
            dados_camera = {'data_hora': data_hora_str, 'qtd_pessoas': qtd_pessoas, 'fk_upa': 1}
            inserir_sucesso_camera = inserir_dados(cursor, 'camera_computacional', dados_camera)
            # if inserir_sucesso_camera:
            #     print(f"UPA Câmera [{data_hora_str}]: {qtd_pessoas} pessoas")

        print("Dados da UPA (temperatura, umidade e câmera) para 48 horas inseridos.")

        print("Gerando um registro de temperatura e oximetria por paciente...")
        agora_paciente = datetime.now()
        data_hora_registro = agora_paciente.strftime('%Y-%m-%d %H:%M:%S') # Usar o mesmo timestamp para todos os registros

        for id_paciente in ids_pacientes:
            # Gera um valor de temperatura e oximetria para cada paciente
            temp_paciente_valor = gerar_temp_corporal_suja()
            dados_temp_paciente = {'data_hora': data_hora_registro, 'valor': temp_paciente_valor, 'fk_paciente': id_paciente}
            inserir_sucesso_temp_paciente = inserir_dados(cursor, 'temperatura_paciente', dados_temp_paciente)
            if inserir_sucesso_temp_paciente:
                print(f"Paciente {id_paciente} Temp: {temp_paciente_valor}°C")

            oximetro_valor = gerar_oximetro_sujo()
            dados_oximetro = {'data_hora': data_hora_registro, 'valor': oximetro_valor, 'fk_paciente': id_paciente}
            inserir_sucesso_oximetro = inserir_dados(cursor, 'oximetro', dados_oximetro)
            if inserir_sucesso_oximetro:
                print(f"Paciente {id_paciente} Oximetria: {oximetro_valor}%")

        print("Um registro de temperatura e oximetria foi inserido para cada paciente.")

        conexao.commit()

except pymysql.err.Error as e:
    print(f"Erro de banco de dados: {e}")
finally:
    if 'conexao' in locals() and conexao.open:
        cursor.close()
        conexao.close()
        print("Conexão ao banco de dados fechada.")