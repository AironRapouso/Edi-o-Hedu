"""Confere cada fala da narradora recortada do master.  Uso: python verify_narr.py <pasta do episódio> [...]
(Na transcrição do episódio inteiro o whisper erra as falas coladas no sino; recortando, acerta.)"""
import json, pathlib, re, difflib, sys
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
from faster_whisper import WhisperModel

UNITS = 'zero um dois três quatro cinco seis sete oito nove dez onze doze treze quatorze quinze dezesseis dezessete dezoito dezenove'.split()
TENS = {20: 'vinte', 30: 'trinta', 40: 'quarenta', 50: 'cinquenta', 60: 'sessenta', 70: 'setenta', 80: 'oitenta', 90: 'noventa'}


def spell(n):
    if n < 20: return UNITS[n]
    if n < 100: return TENS[n // 10 * 10] + ('' if n % 10 == 0 else ' e ' + UNITS[n % 10])
    return str(n)


NUMW = set(UNITS) | set(TENS.values()) | {'cem', 'cento', 'duzentos', 'trezentos', 'quinhentos', 'mil', 'vírgula', 'uma', 'duas'}


def norm(s):
    """Minúsculas, sem pontuação e sem números (dígitos ou por extenso): compara só as palavras."""
    s = s.lower().replace('à', 'a').replace('%', ' por cento').replace('xxi', ' ').replace('xix', ' ')
    s = re.sub(r'[^\wà-ú ]', ' ', s).replace('por que', 'porque')
    return [w for w in s.split() if not w.isdigit() and w not in NUMW and w != 'e']


W = WhisperModel('small', device='cpu', compute_type='int8', cpu_threads=4)
total_bad = 0
for ep in sys.argv[1:]:
    EP = pathlib.Path(ep)
    plan = json.load(open(EP / 'edit/plan.json', encoding='utf8'))
    tl = json.load(open(EP / 'edit/timeline.json', encoding='utf8'))
    f = sf.SoundFile(EP / 'out' / f"{plan['name']}.wav")
    bad = []
    for n in tl['narr']:
        f.seek(int(max(0, n['start'] - 0.3) * f.samplerate))
        seg = f.read(int((n['end'] - n['start'] + 0.3) * f.samplerate), dtype='float32', always_2d=True).mean(1)
        seg = resample_poly(seg, 1, 3).astype(np.float32)
        hyp = ' '.join(t.text.strip() for t in W.transcribe(seg, language='pt', beam_size=5)[0])
        r = difflib.SequenceMatcher(None, norm(n['text']), norm(hyp)).ratio()
        if r < 0.9:
            bad.append(f"   VER {n['key']:6s} {r:.2f}\n       esperado: {n['text']}\n       ouvido:   {hyp}")
    total_bad += len(bad)
    print(f"{EP.name}: {len(tl['narr'])} falas, {len(bad)} com divergência", flush=True)
    print('\n'.join(bad), flush=True) if bad else None
print('TOTAL de falas com divergência:', total_bad)
