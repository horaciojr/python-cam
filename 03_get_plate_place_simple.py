# Ignora certificados SSL antes de qualquer import que use requests
import monkey_patch_requests

from ultralytics import YOLO
import cv2
import os
import shutil
import sys
import time

# Verifica se argumento foi passado
if len(sys.argv) < 2:
    print("❗ Por favor, forneça o argumento: 'amoreiras' ou 'pneu'.")
    sys.exit(1)

# Argumento recebido
argumento = sys.argv[1]

# Carrega o modelo YOLO localmente
model = YOLO("modelos/license_plate_detector.pt")

# Define as pastas
input_dir = os.path.join("fotos", argumento, "veiculos_detectados", "15")
output_base = input_dir
output_dir = os.path.join(output_base, "com_retangulos")
placa_dir = os.path.join(output_dir, "placa")
sem_placa_dir = os.path.join(output_dir, "sem_placa")

os.makedirs(output_dir, exist_ok=True)
os.makedirs(placa_dir, exist_ok=True)
os.makedirs(sem_placa_dir, exist_ok=True)

print(f"🔄 Iniciando processamento contínuo de placas para '{argumento}'...")

while True:
    imagens_encontradas = False

    images = [os.path.join(input_dir, f) for f in os.listdir(input_dir) if f.lower().endswith('.png')]

    if not images:
        print("⏳ Nenhuma imagem encontrada. Aguardando 5 segundos...")
        time.sleep(5)
        continue

    imagens_encontradas = True

    results = model.predict(
        source=input_dir,
        conf=0.3,
        save=False,
        save_crop=False,
        stream=True
    )

    for result in results:
        img_path = result.path
        image = cv2.imread(img_path)

        if image is None:
            print(f"Erro ao carregar imagem: {img_path}")
            continue

        filename = os.path.basename(img_path)
        name_no_ext, ext = os.path.splitext(filename)

        if ext.lower() != '.png':
            print(f"[ ] Ignorado: {filename} (não é PNG)")
            continue

        num_placas = 0

        if result.boxes is not None and len(result.boxes) > 0:
            for i, box in enumerate(result.boxes.xyxy.cpu().numpy()):
                x1, y1, x2, y2 = map(int, box)

                if x2 > x1 and y2 > y1:
                    # Desenha o retângulo amarelo original da detecção
                    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 255), 2)

                    # Recorta exatamente a área da detecção
                    cropped = image[y1:y2, x1:x2]
                    cropped_filename = f"{name_no_ext}_placa_{i}.png"
                    cv2.imwrite(os.path.join(placa_dir, cropped_filename), cropped)

                    num_placas += 1

            new_filename = f"{name_no_ext}__{num_placas}placas.png"
            cv2.imwrite(os.path.join(output_dir, new_filename), image)

        else:
            shutil.copy(img_path, os.path.join(sem_placa_dir, filename))
            print(f"[ ] Nenhuma placa encontrada: {filename}")

        os.remove(img_path)
