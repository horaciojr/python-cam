import cv2
import numpy as np
import time
import os
from datetime import datetime

# URL do stream RTMP
rtmp_url = "rtmp://localhost/live/cam1"

# Parâmetros de detecção de mudança
DIF_THRESHOLD = 25           # Intensidade mínima de diferença por pixel (0–255)
PERCENT_THRESHOLD = 10       # Porcentagem mínima de pixels diferentes para considerar mudança significativa

# Cria pasta "fotos" no mesmo diretório do script, se não existir
output_dir = os.path.join(os.path.dirname(__file__), "fotos")
os.makedirs(output_dir, exist_ok=True)

# Conecta ao stream RTMP
cap = cv2.VideoCapture(rtmp_url)

if not cap.isOpened():
    print("Erro ao conectar no stream RTMP.")
    exit()

print("Conectado com sucesso. Monitorando frames...")

# Captura o primeiro frame do vídeo
ret, prev_frame = cap.read()
if not ret:
    print("Erro ao ler o primeiro frame.")
    cap.release()
    exit()

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
import cv2
import numpy as np
import time
import os
from datetime import datetime

# URL do stream RTMP
rtmp_url = "rtmp://localhost/live/cam1"

# Parâmetros de detecção de mudança
DIF_THRESHOLD = 25           # Intensidade mínima de diferença por pixel (0–255)
PERCENT_THRESHOLD = 10       # Porcentagem mínima de pixels diferentes para considerar mudança significativa

# Cria pasta "fotos" no mesmo diretório do script, se não existir
output_dir = os.path.join(os.path.dirname(__file__), "fotos")
os.makedirs(output_dir, exist_ok=True)

# Conecta ao stream RTMP
cap = cv2.VideoCapture(rtmp_url)

if not cap.isOpened():
    print("Erro ao conectar no stream RTMP.")
    exit()

print("Conectado com sucesso. Monitorando frames...")

# Captura o primeiro frame do vídeo
ret, prev_frame = cap.read()
if not ret:
    print("Erro ao ler o primeiro frame.")
    cap.release()
    exit()

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
