import subprocess
import time
import datetime
import os
import shutil
import sys
import random
import string  # <- novo

# Verificar argumento
if len(sys.argv) < 2:
    print("❗ Por favor, forneça um argumento")
    sys.exit(1)

argumento = sys.argv[1].lower()

# Mapear os argumentos para as URLs corretas
streams = {
    'pneu': 'rtsp://admin:saveiro85@campinasmiamipneus.ddns.net',
    'amoreiras': 'rtsp://admin:saveiro85@camvampinasvistoria.ddns.net',
    'garagein': 'rtsp://admin:saveiro85@campinasmiamipneus.ddns.net',  # substitua pela URL real
    'quiosque': 'rtmp://localizaplaca.com.br/live/cam1'

}

if argumento not in streams:
    print(f"❌ Argumento inválido: '{argumento}'. Use apenas: {', '.join(streams.keys())}.")
    sys.exit(1)

# Seleciona a URL correspondente
stream_url = streams[argumento]

# Diretório de destino
video_dir = os.path.join('videos', argumento)
os.makedirs(video_dir, exist_ok=True)

print(f"🎥 Sistema de captura iniciado para '{argumento}'. Gravando automaticamente entre 06h e 23h...")

try:
    while True:
        now = datetime.datetime.now()
        hour = now.hour
        gravar = False  # Segurança, inicializando com valor conhecido.

        if argumento in ('quiosque', 'garagein'):
            gravar = True  # Grava 24 horas
        elif argumento in ('pneu', 'amoreiras'):
            gravar = 6 <= hour <= 18  # Grava apenas das 6h às 18h
        else:
            gravar = False  # Segurança, caso algo estranho entre

        if gravar:
        
            print("⏳ Dentro do horário de gravação. Iniciando novo vídeo...")

            timestamp = now.strftime("%Y%m%d_%H%M%S")
            final_video_file = f'captura_video_{argumento.replace(" ", "_")}_{timestamp}.mp4'
            destino = os.path.join(video_dir, final_video_file)
            tmp = os.path.join(video_dir, 'tmp.mp4')


            command = [
                'ffmpeg',
                '-rtsp_transport', 'tcp',
                '-i', stream_url,
                '-r', '30',
                '-c:v', 'libx264',
                '-b:v', '6000k',
                '-crf', '20',
                '-preset', 'veryfast',
                '-tune', 'zerolatency',
                '-threads', '4',
                '-t', '30',
                tmp
            ]

            print(f"🎬 Gravando: {destino}")
            try:
                subprocess.run(command, check=True, timeout=35)
                os.rename(tmp, destino)
            except subprocess.TimeoutExpired:
                print("⏱️ Tempo limite de execução atingido (35s).")
            except subprocess.CalledProcessError as e:
                print(f"❌ Erro ao executar o ffmpeg: {e}")
        else:
            print("🌙 Fora do horário de gravação. Aguardando horário permitido...")
            time.sleep(60)

except KeyboardInterrupt:
    print("🛑 Captura encerrada pelo usuário (CTRL+C).")
