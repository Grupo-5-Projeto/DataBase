import random
import math
import pymysql
from datetime import datetime

DB_CONFIG = {
    'host': 'localhost', 
    'user': 'admin_upa_connect',  
    'password': 'urubu100', 
    'database': 'upa_connect'
}

conn = pymysql.connect(**DB_CONFIG)
cursor = conn.cursor()

A = 0.001129148
B = 0.000234125
C = 0.0000000876741
R_REF = 10000  # Resistor de referência (10kΩ)
VCC = 3.3  # Tensão de alimentação do circuito
ADC_MAX = 1023  # Resolução de 10 bits (0-1023)

def temperatura_corporal():
    adc_value = random.randint(610, 670)  # Intervalo ajustado
    V_sensor = (adc_value / ADC_MAX) * VCC
    R_ntc = R_REF * ((VCC / V_sensor) - 1)

    T_kelvin = 1 / (A + B * math.log(R_ntc) + C * (math.log(R_ntc))**3)
    T_celsius = T_kelvin - 273.15

    return round(T_celsius, 2)

def oximetro():
    V_sensor = random.uniform(1.6, 2.6)  # Aumentado para ampliar a faixa
    SpO2 = 94 + (V_sensor - 2.0) * (10 / 1.0)  # Ajuste para cobrir 90-99%
    SpO2 = max(90.0, min(SpO2, 99.0))  # Garante os limites
    return round(SpO2, 1)

def temperatura_ambiente():
    A = 1.009249522e-03
    B = 2.378405444e-04
    C = 2.019202697e-07

    R = random.uniform(8000, 12000)

    T_kelvin = 1 / (A + B * math.log(R) + C * (math.log(R))**3)

    return T_kelvin - 273.15  # Convertendo para Celsius

def umidade():
    V_sensor = random.uniform(1, 3)
    V_max = 3.3
    RH = (V_sensor / V_max) * 100
    return RH

pessoas = random.randint(40, 150)

def visao_computacional():
    global pessoas
    variacao = random.randint(-1, 1) 
    pessoas += variacao
    pessoas = max(40, min(pessoas, 150)) 
    return pessoas
    
cursor.execute("SELECT id_paciente FROM paciente")
pacientes = cursor.fetchall()

if not pacientes:
    print("Nenhum paciente encontrado na base de dados.")
else:
    # Caso sejam poucos dados teremos de apartar a geração dos dados para cada sensor ou grafico
    NUM_MEDICOES = 7

    for paciente in pacientes:
        id_paciente = paciente[0]

        for _ in range(NUM_MEDICOES):
            temp_paci = temperatura_corporal()
            spo2 = oximetro()
            umi = umidade()
            temp_ambi = temperatura_ambiente()
            qtde_pessoas = visao_computacional()
            data_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            cursor.execute("""
                INSERT INTO temperatura_paciente (data_hora, valor, fk_paciente)
                VALUES (%s, %s, %s);
            """, (data_hora, temp_paci, id_paciente))

            cursor.execute("""
                INSERT INTO oximetro (data_hora, valor, fk_paciente)
                VALUES (%s, %s, %s);
            """, (data_hora, spo2, id_paciente))

            cursor.execute("""
                INSERT INTO temperatura_ambiente (data_hora, valor, fk_upa)
                VALUES (%s, %s, %s);
            """, (data_hora, temp_ambi, 1))  

            cursor.execute("""
                INSERT INTO umidade (data_hora, valor, fk_upa)
                VALUES (%s, %s, %s);
            """, (data_hora, umi, 1)) 

            cursor.execute("""
                INSERT INTO camera_computacional (data_hora, qtd_pessoas, fk_upa)
                VALUES (%s, %s, %s);
            """, (data_hora, qtde_pessoas, 1)) 

            conn.commit()
            print(f"Paciente {id_paciente} -> Temperatura: {temp_paci:.2f}°C, SpO2: {spo2:.1f}%")
            print(f"Temperatura: {temp_ambi:.2f}°C, Umidade: {umi:.2f}%")
            print(f"Quantidade de pessoas: {qtde_pessoas}")

cursor.close()
conn.close()
print("Dados inseridos com sucesso!")
