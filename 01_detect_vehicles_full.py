import os
import sys
import cv2
import shutil
import time
from ultralytics import YOLO

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

# Carrega o modelo YOLO pré-treinado (versão nano)
model = YOLO("modelos/yolov8n.pt")

# Define os diretórios de entrada e saída com base no argumento
input_dir = os.path.join("fotos", argumento)
output_detected = os.path.join(input_dir, "veiculos_detectados")
output_no_vehicle = os.path.join(input_dir, "sem_veiculos")

# Cria os diretórios de saída, se não existirem
os.makedirs(output_detected, exist_ok=True)
os.makedirs(output_no_vehicle, exist_ok=True)

# Classes de veículos de interesse conforme o modelo COCO:
# 2 = carro, 5 = ônibus, 7 = caminhão
vehicle_classes = [2, 5, 7]

print(f"🔄 Iniciando processamento contínuo para '{argumento}'...")

# Loop infinito que verifica continuamente novas imagens na pasta
while True:
    imagens_encontradas = False

    # Percorre todos os arquivos da pasta de entrada
    for filename in os.listdir(input_dir):
        image_path = os.path.join(input_dir, filename)

        # Ignora arquivos que não sejam PNG ou que não sejam arquivos
        if not filename.lower().endswith('.png') or not os.path.isfile(image_path):
            continue

        imagens_encontradas = True

        # Lê a imagem
        image = cv2.imread(image_path)
        if image is None:
            continue

        # Aplica o modelo YOLO na imagem
        results = model(image, verbose=False)[0]
        vehicle_saved = False

        # Para cada detecção, verifica se é um veículo de interesse
        for i, box in enumerate(results.boxes):
            class_id = int(box.cls[0])
            if class_id in vehicle_classes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])  # Coordenadas do retângulo da detecção
                cropped_vehicle = image[y1:y2, x1:x2]  # Recorta o veículo da imagem original

                # Define novo nome do arquivo e caminho de saída
                name, ext = os.path.splitext(filename)
                new_filename = f"{name}_vehicle_{i}.png"
                output_path = os.path.join(output_detected, new_filename)

                # Salva a imagem do veículo detectado
                cv2.imwrite(output_path, cropped_vehicle)
                #print(f"[✓] Veículo salvo: {new_filename}")
                vehicle_saved = True

        # Se nenhum veículo foi salvo, copia a imagem para a pasta de "sem_veiculos"
        if not vehicle_saved:
            dest_path = os.path.join(output_no_vehicle, filename)
            shutil.copy(image_path, dest_path)
            #print(f"[ ] Sem veículo válido: {filename}")

        # Remove a imagem original após o processamento
        os.remove(image_path)

    # Se não houver imagens, espera 5 segundos antes de verificar novamente
    if not imagens_encontradas:
        print("⏳ Nenhuma imagem encontrada. Aguardando 5 segundos...")
        time.sleep(5)
