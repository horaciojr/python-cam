import subprocess
import os
import time
import shutil
import sys

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

# Diretórios
foto_dir = os.path.join('fotos', argumento)
video_dir = os.path.join('videos', argumento)
processado_dir = os.path.join(video_dir, 'processado')

# Cria as pastas se não existirem
os.makedirs(foto_dir, exist_ok=True)
os.makedirs(processado_dir, exist_ok=True)

print(f"🔄 Iniciando processamento contínuo para '{argumento}'...")

while True:
    videos_encontrados = False

    # Percorre todos os arquivos da pasta de vídeos
    for video_name in os.listdir(video_dir):
        video_path = os.path.join(video_dir, video_name)

        # Ignora a subpasta 'processado' e arquivos temporários
        if not os.path.isfile(video_path) or video_name.lower().endswith('.tmp'):
            continue
        if video_path.startswith(processado_dir):
            continue
        if not video_name.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
            continue
        if video_name.startswith('tmp'):
            continue

        videos_encontrados = True

        # Gera timestamp único para cada vídeo
        timestamp = int(time.time())

        # Nome base do vídeo (sem a extensão)
        base_name = os.path.splitext(video_name)[0]

        # Extrai frames diretamente para a pasta correta com FFmpeg
        frame_pattern = os.path.join(foto_dir, f'frame_{base_name}_{timestamp}_%04d.png')
        command = [
            'ffmpeg',
            '-i', video_path,
            '-vf', 'select=gt(scene\,0.075)',
            '-vsync', 'vfr',
            '-q:v', '1',  # Qualidade máxima
            frame_pattern
        ]

        print(f"📸 Extraindo frames de: {video_name}...")
        subprocess.run(command)

        print(f"✅ Frames de {video_name} salvos em {foto_dir}/")

        # Move o vídeo processado para a subpasta "processado"
        destino = os.path.join(processado_dir, video_name)
        shutil.move(video_path, destino)
        print(f"📦 {video_name} movido para {processado_dir}/\n")

    if not videos_encontrados:
        print("⏳ Nenhum vídeo encontrado. Aguardando 5 segundos...")
        time.sleep(5)
