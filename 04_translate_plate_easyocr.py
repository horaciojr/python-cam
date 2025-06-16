import os
import sys
import mysql.connector
from datetime import datetime
import easyocr
import shutil
import time

# Argumento obrigatório
if len(sys.argv) < 2:
    print("❗ Por favor, forneça um argumento.")
    sys.exit(1)

argumento = sys.argv[1].lower()

if argumento not in ['pneu', 'amoreiras', 'garagein', 'quiosque', 'cerveja']:
    print(f"❌ Argumento inválido: '{argumento}'.")
    sys.exit(1)

# Diretórios principais
base_dir = os.path.dirname(__file__)
input_dir = os.path.join("fotos", argumento, "veiculos_detectados", "com_retangulos", "placa")
output_dir = os.path.join(input_dir, "processada")
dir_veiculo = os.path.join(base_dir, "fotos", argumento, "veiculos_detectados", "com_retangulos")

# Diretórios públicos
dest_carro = "/usr/local/nginx/html/localizaplaca/imagens/carro"
dest_placa = "/usr/local/nginx/html/localizaplaca/imagens/placa"

os.makedirs(input_dir, exist_ok=True)
os.makedirs(output_dir, exist_ok=True)
os.makedirs(dest_carro, exist_ok=True)
os.makedirs(dest_placa, exist_ok=True)

# OCR
reader = easyocr.Reader(['pt', 'en'], gpu=False)

def extrair_info_imagem(nome_arquivo):
    try:
        partes = nome_arquivo.split("_")
        data_str = partes[1]
        hora_str = partes[2]
        datahora = datetime.strptime(data_str + hora_str, "%Y%m%d%H%M%S%f")
        return nome_arquivo, datahora.strftime("%Y-%m-%d %H:%M:%S")
    except Exception as e:
        print(f"Erro ao extrair data/hora da imagem '{nome_arquivo}': {e}")
        return nome_arquivo, None

def corrigir_para_letra(char):
    return {'0': 'O', '1': 'I', '2': 'Z', '3': 'E','4': 'A', '5': 'S', '6': 'G', '7': 'T','8': 'B', '9': 'P'}.get(char.upper(), char.upper())

def corrigir_para_numero(char):
    return {'O': '0', 'D': '0', 'Q': '0', 'U': '0','I': '1', 'L': '1','Z': '2', 'E': '3', 'S': '5','G': '6', 'T': '7', 'Y': '7', 'B': '8', 'P': '9'}.get(char.upper(), char.upper())

def normalizar_placa(texto):
    texto = texto.strip().upper()
    if len(texto) == 7:
        return ''.join([corrigir_para_letra(c) if i in [0,1,2,4] else corrigir_para_numero(c) for i, c in enumerate(texto)])
    elif len(texto) == 8 and texto[3] in [' ', '-', ',', '.']:
        return ''.join([corrigir_para_letra(c) for c in texto[:3]]) + texto[3] + ''.join([corrigir_para_numero(c) for c in texto[4:]])
    return texto

def copiar_arquivo_com_prefixo(prefixo, origem, destino, renomear_para=None):
    for nome_arquivo in os.listdir(origem):
        if nome_arquivo.startswith(prefixo) and nome_arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            origem_arquivo = os.path.join(origem, nome_arquivo)
            destino_arquivo = os.path.join(destino, renomear_para if renomear_para else nome_arquivo)
            shutil.copy2(origem_arquivo, destino_arquivo)
            print(f"📥 Copiado: {nome_arquivo} → {destino_arquivo}")
            break
    else:
        print(f"⚠️ Nenhum arquivo com prefixo '{prefixo}' encontrado em {origem}")

# Conexão com o banco
try:
    db = mysql.connector.connect(
        host="localhost",
        user="webdb",
        password="webdb",
        database="seguraplacas"
    )
    cursor = db.cursor()
except mysql.connector.Error as err:
    print(f"Erro na conexão com MySQL: {err}")
    sys.exit(1)

while True:
    imagens_encontradas = False

    for filename in sorted(os.listdir(input_dir)):
        if not filename.lower().endswith(".png"):
            continue

        imagens_encontradas = True
        filepath = os.path.join(input_dir, filename)
        ocr_resultados = reader.readtext(filepath)

        for bbox, texto_detectado, confianca in ocr_resultados:
            texto_corrigido = normalizar_placa(texto_detectado)
            texto_limpo = texto_corrigido.translate(str.maketrans('', '', '{}[]()'))

            if len(texto_limpo) <= 6:
                continue

            imagem, datahora = extrair_info_imagem(filename)

            try:
                cursor.execute("""
                    INSERT INTO placas_detectadas (imagem, original, corrigido, confianca, data, cam)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (imagem, texto_detectado, texto_limpo, float(confianca), datahora, argumento))

                # Se for confiável e tamanho adequado, copia para os diretórios finais
                if float(confianca) > 0.5 and len(texto_limpo) >= 6:
                    base_prefix = filename.rsplit("_placa_", 1)[0]
                    novo_nome = base_prefix + ".png"

                    copiar_arquivo_com_prefixo(base_prefix, dir_veiculo, dest_carro, renomear_para=novo_nome)
                    copiar_arquivo_com_prefixo(base_prefix, output_dir, dest_placa)

            except Exception as e:
                print(f"Erro ao inserir no banco ou copiar arquivos: {e}")

        try:
            shutil.move(filepath, os.path.join(output_dir, filename))
        except Exception as e:
            print(f"⚠️ Erro ao mover {filepath} para {output_dir}: {e}")

    if not imagens_encontradas:
        print("⏳ Nenhuma imagem encontrada. Aguardando 5 segundos...")
        time.sleep(5)

db.commit()
cursor.close()
db.close()

print(f"✅ OCR + cópia finalizada para: {argumento}")
