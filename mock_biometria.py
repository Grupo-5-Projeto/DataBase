import random
import pymysql
from datetime import datetime, timedelta

# Configurações do banco de dados
CONFIG_BD = {
    'host': 'localhost',
    'user': 'admin_upa_connect',
    'password': 'urubu100',
    'database': 'upa_connect'
}

def gerar_biometria_r503():
    """Simula a leitura de uma biometria do sensor R503."""
    tamanho_template = random.randint(300, 500)
    return random.randbytes(tamanho_template)

def inserir_biometria(conexao, data_hora, biometria_data, fk_paciente):
    """Insere os dados de biometria na tabela."""
    cursor = conexao.cursor()
    sql = "INSERT INTO biometria (data_hora, biometria, fk_paciente) VALUES (%s, %s, %s)"
    try:
        cursor.execute(sql, (data_hora, biometria_data, fk_paciente))
        conexao.commit()
        cursor.close()
        return True
    except pymysql.err.Error as e:
        print(f"Erro ao inserir biometria para paciente {fk_paciente} em {data_hora}: {e}")
        conexao.rollback()
        cursor.close()
        return False

def obter_ids_pacientes():
    """Obtém os IDs de todos os pacientes cadastrados no banco de dados."""
    try:
        conexao = pymysql.connect(**CONFIG_BD)
        cursor = conexao.cursor()
        sql = "SELECT id_paciente FROM paciente"  # Adapte o nome da coluna do ID se for diferente
        cursor.execute(sql)
        ids_pacientes = [row[0] for row in cursor.fetchall()]
        cursor.close()
        conexao.close()
        return ids_pacientes
    except pymysql.err.Error as e:
        print(f"Erro ao obter IDs dos pacientes: {e}")
        if 'conexao' in locals() and conexao.open:
            conexao.close()
        return []

def inserir_biometrias_mockadas_simuladas_pacientes(num_simulacoes=1):
    """Gera e insere uma biometria mockada por paciente, simulando intervalos de 5 minutos."""
    ids_pacientes = obter_ids_pacientes()
    if not ids_pacientes:
        print("Não foram encontrados pacientes no banco de dados.")
        return

    try:
        conexao = pymysql.connect(**CONFIG_BD)
        agora = datetime.now()

        for i, fk_paciente in enumerate(ids_pacientes):
            # Simula o timestamp com intervalos de 5 minutos
            data_hora_insercao = agora - timedelta(minutes=5 * i)
            data_hora_formatada = data_hora_insercao.strftime('%Y-%m-%d %H:%M:%S')

            biometria_mockada = gerar_biometria_r503()
            inserir_sucesso = inserir_biometria(conexao, data_hora_formatada, biometria_mockada, fk_paciente)
            if inserir_sucesso:
                print(f"Biometria mockada inserida para paciente {fk_paciente} em {data_hora_formatada} (Simulação com intervalo de 5 minutos).")
            else:
                print(f"Falha ao inserir biometria mockada para paciente {fk_paciente} em {data_hora_formatada} (Simulação com intervalo de 5 minutos).")

        conexao.close()
        print("Simulação de inserção de biometrias concluída para os pacientes encontrados, com intervalos de 5 minutos simulados.")

    except pymysql.err.Error as e:
        print(f"Erro de conexão com o banco de dados: {e}")
    finally:
        if 'conexao' in locals() and conexao.open:
            conexao.close()
            print("Conexão ao banco de dados fechada.")

if __name__ == "__main__":
    inserir_biometrias_mockadas_simuladas_pacientes()