import os
import sys
import cv2
import time
import shutil

# Verificar se argumento foi passado
if len(sys.argv) < 2:
    print("❗ Por favor, forneça um argumento.")
    sys.exit(1)

# Argumento passado
argumento = sys.argv[1].lower()

# Verifica se é um valor permitido
if argumento not in ['pneu', 'amoreiras', 'garagein']:
    print(f"❌ Argumento inválido: '{argumento}'. Use apenas 'pneu',  'amoreiras' ou 'garagein'.")
    sys.exit(1)

foto_dir = os.path.join('fotos', argumento, 'veiculos_detectados')
salvar_dir = os.path.join(foto_dir, '15')
processada_dir = os.path.join(salvar_dir, 'processada')

os.makedirs(salvar_dir, exist_ok=True)
os.makedirs(processada_dir, exist_ok=True)

print(f"🔄 Iniciando rotação das imagens para '{argumento}'...")

while True:
    arquivos = [f for f in os.listdir(foto_dir) if os.path.isfile(os.path.join(foto_dir, f)) and not f.lower().endswith('.tmp')]
    if not arquivos:
        print("⏳ Nenhuma imagem nova encontrada. Aguardando 5 segundos...")
        time.sleep(5)
        continue

    for file_name in arquivos:
        file_path = os.path.join(foto_dir, file_name)

        # Ignorar arquivos já processados na pasta salvar_dir para evitar repetição
        if os.path.exists(os.path.join(salvar_dir, file_name)) or os.path.exists(os.path.join(processada_dir, file_name)):
            continue

        image = cv2.imread(file_path)
        if image is None:
            print(f"❗ Erro ao carregar imagem {file_path}")
            continue

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, 14, 1.0)  # Rotação 15 graus para esquerda
        rotated_image = cv2.warpAffine(image, rotation_matrix, (w, h))

        save_path = os.path.join(salvar_dir, file_name)
        cv2.imwrite(save_path, rotated_image)
        print(f"🔄 Imagem rotacionada e salva: {file_name}")

        # Mover arquivo original para pasta processada
        dest_path = os.path.join(processada_dir, file_name)
        shutil.move(file_path, dest_path)
        print(f"📂 Imagem original movida para processada: {file_name}")

    print("✅ Ciclo concluído, aguardando 5 segundos para próxima verificação...")
    time.sleep(5)
