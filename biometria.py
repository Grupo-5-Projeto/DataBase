import pymysql

# Configurações do banco de dados (certifique-se de que correspondam às suas)
CONFIG_BD = {
    'host': 'localhost',
    'user': 'admin_upa_connect',
    'password': 'urubu100',
    'database': 'upa_connect'
}

def visualizar_biometria(id_biometria_para_visualizar):
    """
    Conecta ao banco de dados e busca o conteúdo BLOB da biometria
    para o ID especificado.
    """
    try:
        conexao = pymysql.connect(**CONFIG_BD)
        cursor = conexao.cursor()

        # Consulta SQL para buscar a biometria pelo ID
        sql = "SELECT biometria FROM biometria WHERE id_biometria = %s"
        cursor.execute(sql, (id_biometria_para_visualizar,))
        resultado = cursor.fetchone()

        if resultado:
            conteudo_blob = resultado[0]
            print(f"Conteúdo BLOB para id_biometria {id_biometria_para_visualizar}:")
            print(f"Tipo: {type(conteudo_blob)}")
            print(f"Tamanho em bytes: {len(conteudo_blob)}")
            # Se você quiser ver uma representação hexadecimal dos primeiros bytes
            print(f"Primeiros 20 bytes (hexadecimal): {conteudo_blob[:20].hex()}")
            # Note: Imprimir o conteúdo completo de um BLOB pode gerar uma saída muito longa
            # e geralmente não é útil para inspeção visual direta.

        else:
            print(f"Nenhuma biometria encontrada com id_biometria {id_biometria_para_visualizar}.")

    except pymysql.err.Error as e:
        print(f"Erro ao acessar o banco de dados: {e}")
    finally:
        if 'conexao' in locals() and conexao.open:
            cursor.close()
            conexao.close()
            print("Conexão ao banco de dados fechada.")

if __name__ == "__main__":
    id_para_ver = int(input("Digite o id_biometria que você quer visualizar: "))
    visualizar_biometria(id_para_ver)