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
    print("❗ Por favor, forneça um argumento: 'pneu' ou 'amoreiras'.")
    sys.exit(1)

argumento = sys.argv[1].lower()

# Mapear os argumentos para as URLs corretas
streams = {
    'pneu': 'rtsp://admin:saveiro85@campinasmiamipneus.ddns.net',
    'amoreiras': 'rtsp://admin:saveiro85@camvampinasvistoria.ddns.net'
}

if argumento not in streams:
    print(f"❌ Argumento inválido: '{argumento}'. Use apenas 'pneu' ou 'amoreiras'.")
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

        if 6 <= hour <= 23:
            print("⏳ Dentro do horário de gravação. Iniciando novo vídeo...")

            timestamp = now.strftime("%Y%m%d_%H%M%S")
            random_tag = ''.join(random.choices(string.ascii_lowercase + string.digits, k=4))  # <- novo
            temp_video_file = f'captura_temp_{timestamp}_{random_tag}.mp4'  # <- novo

            base_final_name = f'captura_video_{argumento}_{timestamp}.mp4'
            final_video_file = base_final_name
            destino = os.path.join(video_dir, final_video_file)

            # Evita sobrescrita de arquivos existentes
            ext_counter = 1
            while os.path.exists(destino):
                final_video_file = f'captura_video_{argumento}_{timestamp}__ext{ext_counter}.mp4'
                destino = os.path.join(video_dir, final_video_file)
                ext_counter += 1

            command = [
                'ffmpeg',
                '-rtsp_transport', 'tcp',
                '-analyzeduration', '100M',
                '-probesize', '100M',
                '-fflags', 'nobuffer',
                '-i', stream_url,
                '-r', '30',
                '-vf', 'scale=1920:1080',
                '-b:v', '8000k',
                '-crf', '15',
                '-preset', 'fast',
                '-tune', 'zerolatency',
                '-threads', '8',
                '-rtbufsize', '2G',
                '-t', '30',
                temp_video_file
            ]

            print(f"🎬 Gravando: {temp_video_file}")
            try:
                process = subprocess.Popen(command)
                process.wait()

                if os.path.exists(temp_video_file):
                    shutil.move(temp_video_file, destino)
                    print(f"✅ Vídeo salvo: {destino}")
                else:
                    print("❌ Vídeo não foi gerado. Falha de captura ou stream offline.")

            except Exception as e:
                print(f"❗ Erro durante a gravação: {e}")
        else:
            print("🌙 Fora do horário de gravação. Aguardando horário permitido...")
            time.sleep(60)

        time.sleep(1)

except KeyboardInterrupt:
    print("🛑 Captura encerrada pelo usuário (CTRL+C).")
