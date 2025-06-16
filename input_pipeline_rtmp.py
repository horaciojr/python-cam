import cv2
import numpy as np
import time
import os
from datetime import datetime
import sys

# Verificar se argumento foi passado
if len(sys.argv) < 2:
    print("❗ Por favor, forneça um argumento.")
    sys.exit(1)

# Argumento passado
argumento = sys.argv[1].lower()

# Verifica se é um valor permitido
if argumento not in ['pneu', 'amoreiras', 'garagein', 'quiosque', 'cerveja']:
    print(f"❌ Argumento inválido: '{argumento}'. Use apenas 'pneu',  'amoreiras' , 'quiosque' ou 'cerveja'.")
    sys.exit(1)


# Mapear os argumentos para as URLs corretas
streams = {
    'pneu': 'rtsp://admin:saveiro85@campinasmiamipneus.ddns.net',
    'amoreiras': 'rtsp://admin:saveiro85@camvampinasvistoria.ddns.net',
    'garagein': '',  # substitua pela URL real
    'quiosque': 'rtmp://localizaplaca.com.br/live/cam1',
    'cerveja': 'rtmp://localizaplaca.com.br/live/cerveja'

}

# Seleciona a URL correspondente
rtmp_url = streams[argumento]

# Parâmetros de detecção de mudança
DIF_THRESHOLD = 25           # Intensidade mínima de diferença por pixel (0–255)
PERCENT_THRESHOLD = 15       # Porcentagem mínima de pixels diferentes para considerar mudança significativa

# Cria pasta "fotos" no mesmo diretório do script, se não existir
output_dir = os.path.join(os.path.dirname(__file__), "fotos", argumento)
os.makedirs(output_dir, exist_ok=True)

while True:
    try:
        # Conecta ao stream RTMP
        cap = cv2.VideoCapture(rtmp_url)

        if not cap.isOpened():
            print("Erro ao conectar no stream RTMP. Aguardando 30 segundos")
            cap.release()
            time.sleep(30)
        else:
            break


    except Exception as e:
        print(f"⚠️ Exceção ao tentar conectar: {e}. Tentando novamente em 30 segundos...")
        time.sleep(30)    

print("Conectado com sucesso. Monitorando frames...")

while True:
    try:
        # Captura o primeiro frame do vídeo
        ret, prev_frame = cap.read()
        if not ret:
            print("Erro ao ler o primeiro frame.")
            cap.release()
            time.sleep(30)
        else:
            break

    except Exception as e:
        print(f"⚠️ Exceção ao tentar conectar: {e}. Tentando novamente em 30 segundos...")
        time.sleep(30)    


# Converte o primeiro frame para escala de cinza para facilitar a comparação
prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
frame_count = 0  # Contador opcional para depuração

# Loop contínuo para leitura dos frames
while True:
    # Lê um novo frame do stream
    ret, frame = cap.read()
    if not ret:
        print("Erro ao ler frame, encerrando.")
        break

    # Converte frame atual para tons de cinza
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calcula a diferença absoluta entre o frame atual e o anterior
    diff = cv2.absdiff(prev_gray, gray)

    # Conta quantos pixels têm diferença maior que o limiar definido
    changed_pixels = np.sum(diff > DIF_THRESHOLD)

    # Calcula a porcentagem de pixels que mudaram
    total_pixels = diff.shape[0] * diff.shape[1]
    percent_changed = (changed_pixels / total_pixels) * 100

    # Se a mudança for significativa, salva o frame
    if percent_changed >= PERCENT_THRESHOLD:
        # Gera timestamp no formato YYYYMMDD_HHMMSSmmm (com milissegundos)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S%f")[:-3]
        filename = os.path.join(output_dir, f"frame_{timestamp}.png")

        # Salva o frame como imagem PNG
        cv2.imwrite(filename, frame)

        # Mostra log no terminal
        print(f"[{timestamp}] Alteração {percent_changed:.2f}% — frame salvo: {filename}")

        # Atualiza o frame anterior com o atual
        prev_gray = gray.copy()

    frame_count += 1
