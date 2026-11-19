"""Prepara um episódio: transcreve (faster-whisper local) e segmenta a fala pelos silêncios reais.

Uso: python prep.py <pasta do episódio> [modelo=small]
Gera edit/transcripts/source.json (palavras), edit/segments.json (trechos de fala) e
edit/transcript.txt (leitura: '#índice [tempo] texto', com '‖índice' nas pausas internas).
O plan.json referencia os trechos pelo índice — o corte cai sempre em silêncio de verdade.
"""
import json, pathlib, sys
import numpy as np, soundfile as sf
from common import decode, SR

EP = pathlib.Path(sys.argv[1])
MODEL = sys.argv[2] if len(sys.argv) > 2 else 'small'
ED = EP / 'edit'
(ED / 'transcripts').mkdir(parents=True, exist_ok=True)
src = EP / 'src/source.wav'

# ---------- 1. transcrição ----------
wj = ED / 'transcripts/source.json'
if not wj.exists():
    from faster_whisper import WhisperModel
    model = WhisperModel(MODEL, device='cpu', compute_type='int8', cpu_threads=4)
    segs, _ = model.transcribe(decode(src), language='pt', word_timestamps=True, beam_size=3,
                               condition_on_previous_text=False, vad_filter=False)
    words = [{'text': w.word.strip(), 'start': round(w.start, 2), 'end': round(w.end, 2), 'type': 'word'}
             for s in segs for w in s.words]
    json.dump({'language_code': 'por', 'model': MODEL, 'words': words}, open(wj, 'w', encoding='utf8'),
              ensure_ascii=False)
words = json.load(open(wj, encoding='utf8'))['words']

# ---------- 2. trechos de fala pela energia ----------
x, sr = sf.read(src, dtype='float32', always_2d=True)
assert sr == SR, sr
x = x.mean(1)
n = SR // 100                                   # quadros de 10 ms
fr = x[:len(x) // n * n].reshape(-1, n)
lvl = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-9)
thr = float(np.clip(np.percentile(lvl, 10) + 15, -58, -38))
quiet = lvl < thr
MIN_SIL = 30                                    # 0,30 s
segs, i, N = [], 0, len(quiet)
on = None
run = 0
for k in range(N):
    if quiet[k]:
        run += 1
        if run == MIN_SIL and on is not None:
            segs.append([on * 0.01, (k - MIN_SIL + 1) * 0.01]); on = None
    else:
        if on is None:
            on = k
        run = 0
if on is not None:
    segs.append([on * 0.01, N * 0.01])
segs = [s for s in segs if s[1] - s[0] >= 0.06]

# palavras -> trecho (pelo meio da palavra; palavra "no silêncio" vai para o trecho mais próximo)
def assign(allowed):
    wseg = []
    for w in words:
        m = (w['start'] + min(w['end'], w['start'] + 0.6)) / 2
        inside = [j for j in allowed if segs[j][0] - 0.05 <= m <= segs[j][1] + 0.05]
        j = inside[0] if inside else min(allowed, key=lambda j: min(abs(m - segs[j][0]), abs(m - segs[j][1])))
        wseg.append(max(j, wseg[-1]) if wseg else j)          # mantém a ordem
    return wseg


wseg = assign(range(len(segs)))
count = np.bincount(wseg, minlength=len(segs))

# trechos com 0-1 palavra podem ser som (vinheta, efeito, tela final) ou fala que o whisper pulou:
# transcreve cada um isolado; se não sair texto nenhum, é som (o mix.py pula sozinho).
probe_f = ED / 'seg_probe.json'
probe = json.load(open(probe_f, encoding='utf8')) if probe_f.exists() else {}
cand = [j for j, (a, b) in enumerate(segs) if count[j] <= 1 and b - a >= 0.4 and f'{a:.2f}' not in probe]
if cand:
    from faster_whisper import WhisperModel
    from scipy.signal import resample_poly
    pm = WhisperModel('small', device='cpu', compute_type='int8', cpu_threads=4)
    pad = np.zeros(8000, np.float32)
    for j in cand:
        a, b = segs[j]
        clip = resample_poly(x[int(max(0, a - 0.15) * SR):int((b + 0.15) * SR)], 1, 3).astype(np.float32)
        r, _ = pm.transcribe(np.concatenate([pad, clip, pad]), language='pt', beam_size=3)
        probe[f'{a:.2f}'] = ' '.join(t.text.strip() for t in r if t.no_speech_prob < 0.6)
    json.dump(probe, open(probe_f, 'w', encoding='utf8'), ensure_ascii=False)
sound = [bool(count[j] <= 1 and b - a >= 0.9 and probe.get(f'{a:.2f}', 'x') == '') for j, (a, b) in enumerate(segs)]
wseg = assign([j for j in range(len(segs)) if not sound[j]])
texts = [[] for _ in segs]
for w, j in zip(words, wseg):
    texts[j].append(w['text'])
out = [{'i': j, 'on': round(a, 2), 'off': round(b, 2), 'sound': sound[j],
        'text': ' '.join(texts[j]) or ('' if sound[j] else '⟦' + probe.get(f'{a:.2f}', '') + '⟧')}
       for j, (a, b) in enumerate(segs)]
json.dump({'thr_db': thr, 'segments': out}, open(ED / 'segments.json', 'w', encoding='utf8'), ensure_ascii=False)

# ---------- 3. transcrição para leitura ----------
# '#i [mm:ss|s]' abre linha no trecho i (pausa >= 0,7 s); '‖i' = pausa curta antes do trecho i;
# '⟨t⟩' depois de fim de frase = início da palavra seguinte (ponto de corte em segundos).
first = {}
for k, j in enumerate(wseg):
    first.setdefault(j, k)
lines, cur = [], ''
for j, s in enumerate(out):
    gap = s['on'] - out[j - 1]['off'] if j else 9
    body = []
    if j in first:
        k = first[j]
        while k < len(words) and wseg[k] == j:
            t = words[k]['text']; body.append(t)
            if k + 1 < len(words) and words[k + 1]['start'] - words[k]['end'] > 1.5:
                # buraco sem fala (vinheta/efeito no meio): fim desta palavra | início da próxima
                body.append(f"⟨fim~{words[k]['end']:.2f} | {words[k + 1]['start']:.2f}⟩")
            elif t[-1:] in '.?!' and k + 1 < len(words):
                body.append(f"⟨{words[k + 1]['start']:.2f}⟩")
            k += 1
    txt = ' '.join(body) if body else (f"(SOM {s['off'] - s['on']:.1f}s, pulado)" if s['sound'] else s['text'])
    if body:   # som sem fala colado no começo/fim do trecho (vinheta, efeito): use corte por tempo
        w0, w1 = words[first[j]], words[k - 1]
        if w0['start'] - s['on'] > 1.2:
            txt = f"⟪som {w0['start'] - s['on']:.1f}s, fala em {w0['start']:.2f}⟫ " + txt
        if s['off'] - w1['end'] > 2.0:
            txt += f" ⟪som até {s['off']:.1f}, fala acaba ~{w1['end']:.2f}⟫"
    if gap >= 0.7 or not cur:
        if cur:
            lines.append(cur + (f'  ({gap:.1f}s)' if gap >= 1.5 else ''))
        m, sec = divmod(s['on'], 60)
        cur = f"#{j} [{int(m):02d}:{sec:04.1f}|{s['on']:.1f}] {txt}"
    else:
        cur += f" ‖{j} {txt}"
lines.append(cur)
(ED / 'transcript.txt').write_text(
    f"# {EP.name} | {len(x) / SR:.0f}s | {len(out)} trechos | limiar {thr:.0f} dB | piso p10 {np.percentile(lvl, 10):.0f} dB" + chr(10)
    + chr(10).join(lines), encoding='utf8')
print(EP.name, f'{len(x) / SR:.0f}s', len(words), 'palavras', len(out), 'trechos', f'limiar {thr:.0f} dB')
