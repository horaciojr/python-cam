import cv2
import os
import shutil
import time
import sys

# Verifica argumento (pneu ou amoreiras)
if len(sys.argv) < 2 or sys.argv[1] not in ["pneu", "amoreiras"]:
    print("Uso: python script.py [pneu|amoreiras]")
    sys.exit(1)

pasta = sys.argv[1]

# Define caminhos com base no argumento
base_dir = os.path.join("fotos", pasta, "veiculos_detectados", "15", "com_retangulos", "placa")
input_directory = base_dir
output_directory = os.path.join(base_dir, "grayscale")
processed_directory = os.path.join(output_directory, "processada")

# Cria diretórios, se necessário
os.makedirs(output_directory, exist_ok=True)
os.makedirs(processed_directory, exist_ok=True)

print(f"Monitorando a pasta: {input_directory}")
print("Pressione Ctrl+C para sair.")

while True:
    for filename in os.listdir(input_directory):
        if filename.endswith(".png"):
            input_image_path = os.path.join(input_directory, filename)

            # Evita reprocessar arquivos que já estão sendo movidos ou processados
            if os.path.exists(os.path.join(processed_directory, filename)):
                continue

            try:
                img = cv2.imread(input_image_path)
                if img is None:
                    continue

                height, width, _ = img.shape
                top = int(height * 0.25)
                bottom = int(height * 0.80)
                left = int(width * 0.05)
                right = int(width * 0.90)
                cropped_img = img[top:bottom, left:right]
                gray_img = cv2.cvtColor(cropped_img, cv2.COLOR_BGR2GRAY)

                alpha_values = [0.5, 2.0]
                beta_values = [100]

                filename_base = os.path.splitext(filename)[0]

                # Grayscale
                cv2.imwrite(os.path.join(output_directory, f"{filename_base}_gray.png"), gray_img)

                # Contraste e brilho
                for alpha in alpha_values:
                    for beta in beta_values:
                        bright_img = cv2.convertScaleAbs(gray_img, alpha=alpha, beta=beta)
                        cv2.imwrite(os.path.join(output_directory,
                            f"{filename_base}_bright_a{alpha}_b{beta}.png"), bright_img)

                # CLAHE
                for clip in [2.0, 4.0, 6.0]:
                    clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8))
                    clahe_img = clahe.apply(gray_img)
                    cv2.imwrite(os.path.join(output_directory,
                        f"{filename_base}_clahe{int(clip)}.png"), clahe_img)

                # Binarização Otsu
                suave = cv2.GaussianBlur(bright_img, (3, 3), 10)
                _, bin = cv2.threshold(suave, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
                bin = cv2.bitwise_not(bin)
                cv2.imwrite(os.path.join(output_directory, f"{filename_base}_bin.png"), bin)

                # Move imagem original para pasta "processada"
                shutil.move(input_image_path, os.path.join(processed_directory, filename))
                print(f"Processado: {filename}")

            except Exception as e:
                print(f"Erro ao processar {filename}: {e}")
    
    print("✅ Ciclo concluído, aguardando 5 segundos para próxima verificação...")
    time.sleep(5)  # Aguarda 5 segundos antes de procurar novas imagens
