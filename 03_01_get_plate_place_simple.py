import os
import sys
import cv2
import easyocr
from datetime import datetime
from ultralytics import YOLO

# Carregar o modelo YOLO
model = YOLO("modelos/license_plate_detector.pt")

# Configuração do leitor OCR
reader = easyocr.Reader(['pt', 'en'])

# Verifica se argumento foi passado
if len(sys.argv) < 2:
    print("❗ Por favor, forneça o argumento: 'amoreiras' ou 'pneu'.")
    sys.exit(1)

# Argumento recebido
argumento = sys.argv[1]

# Define o diretório base, a partir do diretório atual onde o script está sendo executado
base_dir = os.getcwd()

# Define os diretórios de entrada
input_dir = os.path.join(base_dir, "fotos", argumento, "veiculos_detectados", "15")

# Verifica se a pasta de entrada existe
if not os.path.exists(input_dir):
    print(f"❗ A pasta de entrada {input_dir} não foi encontrada.")
    sys.exit(1)

# Cria o arquivo de relatório em HTML
html_content = """
<html>
<head>
    <title>Relatório de Placas Detectadas</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            font-size: 12px;
            margin: 0;
            padding: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        table, th, td {
            border: 1px solid black;
        }
        th, td {
            padding: 8px;
            text-align: left;
        }
        img {
            width: 50%;  /* Dobrar o tamanho da imagem */
            height: 50%; /* Dobrar o tamanho da imagem */
        }
        .container {
            max-width: 1200px; /* Opcional, pode ajustar conforme necessário */
            margin: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <h2>Relatório de Placas Detectadas</h2>
        <table>
            <thead>
                <tr>
                    <th>Imagem</th>
                    <th>Texto Detectado</th>
                </tr>
            </thead>
            <tbody>
"""

# Processa as imagens
for filename in sorted(os.listdir(input_dir)):
    if filename.lower().endswith('.png'):
        img_path = os.path.join(input_dir, filename)  # Caminho completo da imagem

        image = cv2.imread(img_path)
        if image is None:
            print(f"Erro ao carregar imagem: {filename}")
            continue

        # Realiza a detecção com YOLO na imagem
        results = model(img_path)

        # Verifica se há deteção de placa (existe pelo menos uma caixa de coordenadas)
        if results[0].boxes.shape[0] > 0:
            # Realiza a tradução da placa com EasyOCR
            texto_detectado = reader.readtext(image, detail=0)

            if texto_detectado:
                texto_placa = " | ".join(texto_detectado)
                print(f"Imagem: {filename} - Texto detectado: {texto_placa}")
            else:
                texto_placa = "Nenhum texto detectado."
        else:
            texto_placa = "Nenhuma placa detectada."

        # Adiciona os resultados ao relatório HTML
        html_content += f"""
                <tr>
                    <td><img src="file:///{img_path}" alt="Placa Detectada"></td>
                    <td>{texto_placa}</td>
                </tr>
        """

# Finaliza o HTML
html_content += """
        </tbody>
    </table>
</div>
</body>
</html>
"""

# Salva o relatório
report_filename = os.path.join(input_dir, "relatorio_placas_detectadas.html")
with open(report_filename, "w", encoding="utf-8") as report_file:
    report_file.write(html_content)

print(f"✅ Relatório gerado com sucesso: {report_filename}")
