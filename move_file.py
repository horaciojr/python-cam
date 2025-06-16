import mysql.connector
import os
import shutil

# Conexão com o banco de dados
conn = mysql.connector.connect(
    host="localhost",
    user="webdb",
    password="webdb",
    database="seguraplacas"
)

cursor = conn.cursor()
cursor.execute("""
    SELECT imagem 
    FROM placas_detectadas 
    WHERE LENGTH(corrigido) >= 6 
      AND confianca > 0.5
      AND DATE(data) = 20250613
""")

# Diretórios de origem
base_dir = os.path.dirname(__file__)
dir_veiculo = os.path.join(base_dir, "fotos", "quiosque", "veiculos_detectados", "com_retangulos")
dir_placa   = os.path.join(dir_veiculo, "placa", "processada")

# Diretórios de destino
dest_carro = "/usr/local/nginx/html/localizaplaca/imagens/carro"
dest_placa = "/usr/local/nginx/html/localizaplaca/imagens/placa"

os.makedirs(dest_carro, exist_ok=True)
os.makedirs(dest_placa, exist_ok=True)

def copiar_arquivo_com_prefixo(prefixo, origem, destino, renomear_para=None):
    encontrados = False
    for nome_arquivo in os.listdir(origem):
        if nome_arquivo.startswith(prefixo) and nome_arquivo.lower().endswith(('.png', '.jpeg', '.jpg')):
            origem_arquivo = os.path.join(origem, nome_arquivo)

            # Se for para renomear o arquivo
            if renomear_para:
                destino_arquivo = os.path.join(destino, renomear_para)
            else:
                destino_arquivo = os.path.join(destino, nome_arquivo)

            shutil.copy2(origem_arquivo, destino_arquivo)
            print(f"✅ Copiado: {nome_arquivo} → {destino_arquivo}")
            encontrados = True
            break  # remove o break se quiser copiar todos os que casam com o prefixo
    if not encontrados:
        print(f"⚠️ Nenhum arquivo com prefixo '{prefixo}' encontrado em {origem}")

# Para cada linha no resultado do banco
for (original,) in cursor.fetchall():
    base_prefix = original.strip().rsplit("_placa_", 1)[0]
    print(f"base_prefix: '{base_prefix}'")

    # Define novo nome de saída (padronizado)
    novo_nome = base_prefix + ".png"

    # Copia imagem do carro com renomeação
    copiar_arquivo_com_prefixo(base_prefix, dir_veiculo, dest_carro, renomear_para=novo_nome)

    # Copia imagem da placa (sem renomear)
    copiar_arquivo_com_prefixo(base_prefix, dir_placa, dest_placa)

# Finaliza
cursor.close()
conn.close()
