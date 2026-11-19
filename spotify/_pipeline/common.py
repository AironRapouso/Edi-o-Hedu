"""Constantes e utilitários compartilhados do pipeline de podcast (A Nova Ordem Educacional)."""
import os
import pathlib
import shutil
import subprocess
import numpy as np

# ffmpeg: variável FFMPEG ou o ffmpeg do PATH (no Linux: sudo apt install ffmpeg)
FF = os.environ.get('FFMPEG') or shutil.which('ffmpeg') or 'ffmpeg'
SR = 48000
# vinheta oficial do canal; o áudio já vem extraído em _pipeline/vinheta.wav, este arquivo só é usado se ele faltar
VINHETA = os.environ.get('VINHETA') or str(pathlib.Path(__file__).resolve().parents[2] / 'assets' / 'vinheta.mp4')
VOICE, RATE = 'pt-BR-FranciscaNeural', '-8%'   # narradora (ver PADRAO_PODCAST.md)

NUM = ['zero', 'um', 'dois', 'três', 'quatro', 'cinco', 'seis', 'sete', 'oito', 'nove', 'dez',
       'onze', 'doze']


def ff(*a):
    subprocess.run([FF, '-hide_banner', '-loglevel', 'error', '-y', *a], check=True)


def decode(path, sr=16000):
    """Decodifica qualquer áudio para mono float32 (o PyAV instalado é incompatível com o faster-whisper)."""
    raw = subprocess.run([FF, '-v', 'error', '-i', str(path), '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32)


def db(x):
    return 10 ** (x / 20)


def block_lines(plan):
    """Falas da narradora, na ordem: intro, 'Bloco N. título' (último = Encerramento), recap, outro."""
    nar = plan['narration']
    keys = [k for k in plan['blocks'] if k != 'cold']
    lines = {'intro': nar['intro']}
    for i, k in enumerate(keys, 1):
        b = plan['blocks'][k]
        say = b.get('say', b['title'])
        if say[-1] not in '.?!':
            say += '.'
        head = 'Encerramento' if i == len(keys) else f'Bloco {NUM[i]}'
        lines[k] = nar.get(k, f'{head}. {say}')
    lines['recap'] = nar['recap']
    lines['outro'] = nar['outro']
    return lines
