import random
import pymysql
from datetime import datetime

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
        print(f"Erro ao inserir biometria para paciente {fk_paciente}: {e}")
        conexao.rollback()
        cursor.close()
        return False

def inserir_biometrias_mockadas():
    """Gera e insere dados de biometria mockados para 49 pacientes."""
    try:
        conexao = pymysql.connect(**CONFIG_BD)
        agora = datetime.now()
        data_hora_insercao = agora.strftime('%Y-%m-%d %H:%M:%S')

        for fk_paciente in range(1, 50):  # Itera pelos IDs de paciente de 1 a 49
            biometria_mockada = gerar_biometria_r503()
            inserir_sucesso = inserir_biometria(conexao, data_hora_insercao, biometria_mockada, fk_paciente)
            if inserir_sucesso:
                print(f"Biometria mockada inserida para paciente {fk_paciente} em {data_hora_insercao}.")
            else:
                print(f"Falha ao inserir biometria mockada para paciente {fk_paciente}.")

        conexao.close()
        print("Inserção de biometrias mockadas concluída para 49 pacientes.")

    except pymysql.err.Error as e:
        print(f"Erro de conexão com o banco de dados: {e}")
    finally:
        if 'conexao' in locals() and conexao.open:
            conexao.close()
            print("Conexão ao banco de dados fechada.")

if __name__ == "__main__":
    inserir_biometrias_mockadas()