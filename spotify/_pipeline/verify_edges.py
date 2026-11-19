"""Confere as bordas dos cortes: transcreve o começo e o fim de cada bloco de fala no master
e mede o volume final.  Uso: python verify_edges.py <pasta do episódio> [...]"""
import json, pathlib, subprocess, sys
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
from faster_whisper import WhisperModel
from common import FF

W = WhisperModel('small', device='cpu', compute_type='int8', cpu_threads=4)
for ep in sys.argv[1:]:
    EP = pathlib.Path(ep)
    plan = json.load(open(EP / 'edit/plan.json', encoding='utf8'))
    tl = json.load(open(EP / 'edit/timeline.json', encoding='utf8'))
    wav = EP / 'out' / f"{plan['name']}.wav"
    r = subprocess.run([FF, '-hide_banner', '-i', str(wav), '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                       capture_output=True, text=True).stderr
    tail = r[r.rindex('Summary'):]
    I = tail.split('I:')[1].split('LUFS')[0].strip(); P = tail.split('Peak:')[1].split('dBFS')[0].strip()
    print(f"== {EP.name} | {tl['duration'] / 60:.1f} min | {I} LUFS | pico {P} dBFS", flush=True)
    f = sf.SoundFile(wav)

    def hear(t0, t1):
        f.seek(int(max(0, t0) * f.samplerate))
        seg = f.read(int((t1 - t0) * f.samplerate), dtype='float32', always_2d=True).mean(1)
        seg = resample_poly(seg, 1, 3).astype(np.float32)
        return ' '.join(t.text.strip() for t in W.transcribe(seg, language='pt', beam_size=3)[0])

    for kind, key, s, e in tl['marks']:
        if kind != 'host':
            continue
        d = e - s
        if d <= 16:
            print(f'  {key:5s} {d:5.0f}s | {hear(s, e)}', flush=True)
        else:
            print(f'  {key:5s} {d:5.0f}s | {hear(s, s + 7)}  [...]  {hear(e - 8, e)}', flush=True)
