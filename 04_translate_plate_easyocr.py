import os
import sys
import csv
import mysql.connector
from datetime import datetime
import easyocr

# Verifica argumento
if len(sys.argv) < 2:
    print("❗ Por favor, forneça o argumento: 'amoreiras' ou 'pneu'.")
    sys.exit(1)

argumento = sys.argv[1]
input_dir = os.path.join("fotos", argumento, "veiculos_detectados", "15", "com_retangulos", "placa", "grayscale")
os.makedirs(input_dir, exist_ok=True)

# OCR
reader = easyocr.Reader(['pt', 'en'], gpu=False)

import datetime

from datetime import datetime

def extrair_info_imagem(nome_arquivo):
    """
    Extrai o nome da imagem original, a data e a hora a partir do nome do arquivo.
    
    Exemplo de nome: frame_captura_video_pneu_20250520_170201_1747771358_0037_vehicle_0_placa_0_bin.png
    """
    try:
        partes = nome_arquivo.split("_")
        data_str = partes[4]      # Ex: '20250520'
        hora_str = partes[5]      # Ex: '170201'
        
        datahora = datetime.strptime(data_str + hora_str, "%Y%m%d%H%M%S")
        return nome_arquivo, datahora.strftime("%Y-%m-%d %H:%M:%S")
    
    except (IndexError, ValueError) as e:
        print(f"Erro ao extrair data/hora da imagem '{nome_arquivo}': {e}")
        return nome_arquivo, None



# Substituições
def corrigir_para_letra(char):
    return {
        '0': 'O', '1': 'I', '2': 'Z', '3': 'E',
        '4': 'A', '5': 'S', '6': 'G', '7': 'T',
        '8': 'B', '9': 'P'
    }.get(char.upper(), char.upper())

def corrigir_para_numero(char):
    return {
        'O': '0', 'D': '0', 'Q': '0', 'U': '0',
        'I': '1', 'L': '1',
        'Z': '2', 'E': '3', 'S': '5',
        'G': '6', 'T': '7', 'Y': '7', 'B': '8', 'P': '9'
    }.get(char.upper(), char.upper())

def normalizar_placa(texto):
    texto = texto.strip().upper()
    if len(texto) == 7:
        corrigida = ""
        for i, c in enumerate(texto):
            if i in [0, 1, 2, 4]:
                corrigida += corrigir_para_letra(c)
            else:
                corrigida += corrigir_para_numero(c)
        return corrigida
    elif len(texto) == 8:
        parte_letras = texto[:3]
        separador = texto[3]
        parte_numeros = texto[4:]
        if separador not in [' ', '-', ',', '.']:
            return texto
        letras_corrigidas = ''.join([corrigir_para_letra(c) for c in parte_letras])
        numeros_corrigidos = ''.join([corrigir_para_numero(c) for c in parte_numeros])
        return f"{letras_corrigidas}{separador}{numeros_corrigidos}"
    return texto

# Conexão MySQL
try:
    db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="seguraplacas"
    )
    cursor = db.cursor()
except mysql.connector.Error as err:
    print(f"Erro na conexão com MySQL: {err}")
    sys.exit(1)

# Cria a tabela se não existir
cursor.execute("""
CREATE TABLE IF NOT EXISTS placas_detectadas (
    id INT AUTO_INCREMENT PRIMARY KEY,
    imagem VARCHAR(255),
    original TEXT,
    corrigido VARCHAR(20),
    confianca FLOAT,
    data DATETIME
)
""")

# CSV para textos curtos (não salvos no banco)
csv_path = os.path.join(input_dir, f"placas_textos_curto_{argumento}.csv")
csv_file = open(csv_path, "a", newline="", encoding="utf-8")
csv_writer = csv.writer(csv_file)
# Cabeçalho só se arquivo vazio
if os.path.getsize(csv_path) == 0:
    csv_writer.writerow(["arquivo", "texto_detectado", "texto_corrigido", "confiança", "datahora"])


# Processamento
for filename in sorted(os.listdir(input_dir)):
    if not filename.lower().endswith(".png"):
        continue

    filepath = os.path.join(input_dir, filename)
    ocr_resultados = reader.readtext(filepath)

    for bbox, texto_detectado, confianca in ocr_resultados:
        texto_corrigido = normalizar_placa(texto_detectado)
        texto_limpo = texto_corrigido.translate(str.maketrans('', '', '{}[]()'))

        if len(texto_limpo) <= 6:
            csv_writer.writerow([filename, texto_detectado.strip(), texto_corrigido, round(confianca, 4)])
            continue
        else:

            imagem, datahora = extrair_info_imagem(filename)

            try:
                cursor.execute("""
                    INSERT INTO placas_detectadas (imagem, original, corrigido, confianca, data)
                VALUES (%s, %s, %s, %s, %s)
            """, (imagem, texto_detectado, texto_limpo, float(confianca),datahora))
            except Exception as e:
                 print(f"Erro ao inserir no banco: {e}")

conn.commit()
cursor.close()
conn.close()
csvfile.close()

print(f"✅ OCR finalizado para: {argumento}")
print(f"📁 Placas inválidas salvas em: {csv_path}")
