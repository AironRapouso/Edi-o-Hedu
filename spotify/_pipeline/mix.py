"""Monta o episódio de podcast (Spotify) a partir do áudio do YouTube.  Uso: python mix.py <pasta do episódio>

Padrão: vinheta -> cold open -> apresentação da narradora -> blocos (stinger + narradora + fala)
-> "Para fixar" -> chamada final -> vinheta. Trilha ambiente sintetizada por baixo, com
automação de volume por região (sem "bombeamento" nas pausas).

plan.json: blocks = {cold, b1..bn}, cada um com "title" e "spans". Um span é
  [i, j]            -> trechos de fala i..j do segments.json (cortes sempre em silêncio real)
  [t0, t1, "raw"]   -> tempo exato em segundos (corte dentro de um trecho)
"""
import json, pathlib, subprocess, sys
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve
from scipy.ndimage import uniform_filter1d
from common import FF, SR, VINHETA, ff, db, block_lines

EP = pathlib.Path(sys.argv[1])
ROOT = EP / 'edit'
rng = np.random.default_rng(7)
f32 = np.float32


def load(path):
    x, sr = sf.read(path, dtype='float32', always_2d=True)
    assert sr == SR, (path, sr)
    return x.mean(1)


def speech_rms(x):
    # RMS só dos trechos com fala (janelas de 50 ms acima de -45 dBFS)
    n = SR // 20
    w = x[:len(x) // n * n].reshape(-1, n)
    r = np.sqrt((w ** 2).mean(1))
    return float(np.sqrt((r[r > db(-45)] ** 2).mean()))


PLAN = json.load(open(ROOT / 'plan.json', encoding='utf8'))
SEG = json.load(open(ROOT / 'segments.json', encoding='utf8'))['segments']

# ---------- 1. tratamento de voz (ffmpeg) ----------
VOICE_CHAIN = ('highpass=f=75,afftdn=nr=6:nf=-50,'
               'equalizer=f=280:t=q:w=1.1:g=-2.5,'
               'equalizer=f=3400:t=q:w=1.4:g=2.5,'
               'highshelf=f=9500:g=2,'
               'deesser=i=0.35,'
               'acompressor=threshold=-21dB:ratio=2.5:attack=8:release=160:makeup=2')
host_f = ROOT / 'host_treated.wav'
if not host_f.exists():
    # nivela a fonte (fala em torno de -18 dBFS RMS) para a cadeia agir igual em todo episódio
    g = 20 * np.log10(db(-18) / speech_rms(load(EP / 'src/source.wav')))
    ff('-i', str(EP / 'src/source.wav'), '-af', f'volume={g:.2f}dB,' + VOICE_CHAIN,
       '-ac', '1', '-ar', str(SR), '-c:a', 'pcm_f32le', str(host_f))
host = load(host_f)

tts = {}
for f in sorted((ROOT / 'tts').glob('*.mp3')):
    w = ROOT / 'tts' / (f.stem + '.wav')
    if not w.exists() or w.stat().st_mtime < f.stat().st_mtime:
        ff('-i', str(f), '-af', 'highpass=f=80,equalizer=f=3000:t=q:w=1.5:g=1.5,'
           'acompressor=threshold=-20dB:ratio=2:attack=10:release=150',
           '-ac', '1', '-ar', str(SR), '-c:a', 'pcm_f32le', str(w))
    tts[f.stem] = load(w)

vin_f = pathlib.Path(__file__).parent / 'vinheta.wav'
if not vin_f.exists():
    ff('-i', VINHETA, '-vn', '-ac', '2', '-ar', str(SR), '-c:a', 'pcm_f32le', str(vin_f))
vin, _ = sf.read(vin_f, dtype='float32', always_2d=True)

# ---------- 2. cortes (bordas nos silêncios reais, pausas comprimidas) ----------
MAX_GAP, KEEP_GAP = 0.80, 0.62   # pausa > 0.80 s vira 0.62 s
LEAD, TRAIL = 0.10, 0.25         # folga antes/depois de cada span (limitada ao silêncio disponível)


def piece(a, b, fade=0.012):
    seg = host[int(a * SR):int(b * SR)].copy()
    f = min(int(fade * SR), len(seg) // 2)
    seg[:f] *= np.linspace(0, 1, f, dtype=f32); seg[-f:] *= np.linspace(1, 0, f, dtype=f32)
    return seg


def snap(t, lo=-0.30, hi=0.05):
    """Ponto mais silencioso (janela de 30 ms) em torno de t."""
    w, h = int(0.03 * SR), int(0.005 * SR)
    i0 = max(0, int((t + lo) * SR)); i1 = int((t + hi) * SR)
    best = min(range(i0, i1, h), key=lambda i: float((host[i:i + w] ** 2).sum()))
    return (best + w // 2) / SR


def render_span(sp):
    """[a, b]. Inteiro = índice de trecho (borda no silêncio real). Decimal positivo = início da
    palavra seguinte ao corte (encaixa no ponto mais silencioso logo antes). Decimal negativo, só em b =
    fim aproximado da última palavra (encaixa logo depois). [t0, t1, 'raw'] = tempos exatos.
    Trechos marcados como som (vinheta/efeito) dentro do span são pulados."""
    if len(sp) == 3:
        return piece(sp[0], sp[1], 0.006)
    a, b = sp
    if isinstance(a, int):
        prev_off = SEG[a - 1]['off'] if a > 0 else 0.0
        a = max(prev_off + 0.02, SEG[a]['on'] - LEAD, 0)
    else:
        a = snap(a)
    if isinstance(b, int):
        next_on = SEG[b + 1]['on'] if b + 1 < len(SEG) else len(host) / SR
        b = min(next_on - 0.02, SEG[b]['off'] + TRAIL)
    elif b < 0:
        b = snap(-b, -0.05, 0.50)
    else:
        b = snap(b)
    assert b > a, sp
    inside = [s for s in SEG if s['off'] > a and s['on'] < b and not s.get('sound')]
    out, cur = [], a
    for p, q in zip(inside, inside[1:]):    # comprime pausas longas e pula sons entre trechos de fala
        if q['on'] - p['off'] > MAX_GAP:
            out.append(piece(cur, p['off'] + KEEP_GAP / 2)); cur = q['on'] - KEEP_GAP / 2
    out.append(piece(cur, b))
    return np.concatenate(out)


def render_block(spans):
    parts = []
    for n, sp in enumerate(spans):
        if n:                               # emenda de corte: respiro curto entre os spans
            parts.append(np.zeros(int(0.22 * SR), f32))
        parts.append(render_span(sp))
    return np.concatenate(parts)


host_parts = {k: render_block(v['spans']) for k, v in PLAN['blocks'].items()}

# iguala a narradora à voz do apresentador
ref = speech_rms(np.concatenate(list(host_parts.values())))
for k in tts:
    tts[k] *= ref / speech_rms(tts[k]) * db(-1.0)

# ---------- 3. trilha sintetizada ----------
def lowpass(x, fc, order=4):
    return sosfilt(butter(order, fc, 'low', fs=SR, output='sos'), x, axis=0)


def reverb(x, secs=2.2, mix=0.35):
    n = int(secs * SR)
    t = np.arange(n) / SR
    ir = rng.standard_normal((n, 2)) * np.exp(-t / (secs / 6.9))[:, None]
    ir = lowpass(ir, 6000)
    ir /= np.sqrt((ir ** 2).sum(0))
    wet = np.stack([fftconvolve(x[:, c], ir[:, c])[:len(x)] for c in range(2)], 1)
    return x * (1 - mix) + wet * mix * 3


def note(f, dur, amp=1.0, att=1.6, rel=2.0):
    n = int(dur * SR); t = np.arange(n) / SR
    env = np.minimum(1, t / att) * np.minimum(1, (dur - t) / rel).clip(0)
    out = np.zeros((n, 2))
    for c, det in enumerate((-0.12, 0.12)):     # leve chorus estéreo
        ff_ = f * (1 + det / 100 * 5)
        out[:, c] = (np.sin(2 * np.pi * ff_ * t) + 0.35 * np.sin(2 * np.pi * 2 * ff_ * t)
                     + 0.12 * np.sin(2 * np.pi * 3 * ff_ * t + 0.4))
    return out * env[:, None] * amp


def hz(m): return 440 * 2 ** ((m - 69) / 12)


# Dm9 - Bbmaj7 - Fmaj7/A - C(add9): sóbrio, institucional
CHORDS = [[50, 57, 62, 65, 69, 64], [46, 53, 57, 62, 65, 69], [45, 53, 60, 64, 69, 67], [48, 55, 60, 64, 67, 62]]
BAR = 8.0


def bed_loop():
    """Um ciclo de 32 s da trilha em regime permanente (repete sem emenda). Fica em cache."""
    cache = pathlib.Path(__file__).parent / 'bed_loop.npy'
    if cache.exists():
        return np.load(cache)
    total = 3 * 4 * BAR
    out = np.zeros((int(total * SR) + SR * 12, 2))
    for i in range(12):
        ch = CHORDS[i % 4]; s = int(i * BAR * SR)
        for j, m in enumerate(ch):
            seg = note(hz(m), BAR + 2.5, amp=(0.5 if j == 0 else 0.22), att=2.5, rel=3.0)
            out[s:s + len(seg)] += seg
        sub = note(hz(ch[0] - 12), BAR + 2.5, amp=0.35, att=2.0, rel=3.0)
        out[s:s + len(sub)] += sub
    out = reverb(lowpass(out, 2200), 3.0, 0.45)
    n = int(4 * BAR * SR)
    loop = out[n:2 * n]
    loop = (loop / np.abs(loop).max()).astype(f32)
    np.save(cache, loop)
    return loop


def stinger():
    # whoosh (ruído filtrado em subida) + sino suave — marca a troca de bloco
    d = 2.6; n = int(d * SR); t = np.arange(n) / SR
    noise = rng.standard_normal((n, 2))
    sw = np.zeros_like(noise)
    k = int(0.9 * SR)
    for a in range(0, k, 2400):        # filtro passa-faixa varrendo para cima
        fc = 300 + 5000 * (a / k) ** 2
        sw[a:a + 2400] = sosfilt(butter(2, [fc * 0.7, fc * 1.3], 'band', fs=SR, output='sos'), noise[a:a + 2400], axis=0)
    env = np.zeros(n); env[:k] = (np.arange(k) / k) ** 2.5
    env[k:k + 1200] = np.linspace(1, 0, 1200)
    whoosh = sw * env[:, None] * 0.25
    bell = np.zeros((n, 2))
    for f, a in ((hz(74), 0.5), (hz(81), 0.3), (hz(86), 0.12)):
        tt = t[k:] - t[k]
        e = np.exp(-tt / 0.55) * np.minimum(1, tt / 0.004)
        bell[k:] += (np.sin(2 * np.pi * f * tt) * e * a)[:, None]
    x = reverb(whoosh + bell, 2.0, 0.4)
    return (x / np.abs(x).max()).astype(f32), 0.9   # (áudio, instante do "impacto")


# ---------- 4. linha do tempo ----------
keys = [k for k in PLAN['blocks'] if k != 'cold']
seq = PLAN.get('sequence')
if not seq:
    seq = [{'type': 'vinheta', 'gap': 0.4}, {'type': 'host', 'key': 'cold', 'gap': 0.2},
           {'type': 'stinger'}, {'type': 'narr', 'key': 'intro', 'gap': 0.3}]
    for k in keys:
        seq += [{'type': 'stinger'}, {'type': 'narr', 'key': k, 'gap': 0.55},
                {'type': 'host', 'key': k, 'gap': 0.4 if k == keys[-1] else 0.2}]
    seq += [{'type': 'stinger'}, {'type': 'narr', 'key': 'recap', 'gap': 0.7},
            {'type': 'narr', 'key': 'outro', 'gap': 0.6}, {'type': 'vinheta', 'gap': 0.0}]

tl, cur = [], 0.0   # (início em s, áudio)


def put(x, gap_after=0.0, at=None):
    global cur
    s = cur if at is None else at
    tl.append((s, x))
    cur = max(cur, s + len(x) / SR + gap_after)
    return s


regions, marks = [], []  # (t0, t1, nível da trilha em dB) / (tipo, chave, início)
st, st_hit = stinger()
st = st * ref * 3.0
for step in seq:
    kind, key = step['type'], step.get('key')
    gap = step.get('gap', 0.45)
    if kind == 'vinheta':
        s = put(vin, gap); regions.append((s, cur, None))
    elif kind == 'stinger':
        s = put(st, at=cur); cur = s + st_hit + 0.55; regions.append((s, cur, -12))
    elif kind == 'narr':
        s = put(tts[key], gap); regions.append((s, cur, -16))
    elif kind == 'host':
        s = put(host_parts[key], gap); regions.append((s, cur, -22))
    marks.append((kind, key, round(s, 2), round(cur, 2)))
total = cur + 1.0

N = int(total * SR)
mix = np.zeros((N, 2), f32)
for s, x in tl:
    i = int(s * SR); x = x[:N - i]
    mix[i:i + len(x)] += x if x.ndim == 2 else x[:, None]

# automação da trilha: rampas de 1,2 s entre regiões; some durante a vinheta
gain = np.full(N, db(-80.0), f32)
for t0, t1, lvl in regions:
    if lvl is not None:
        gain[int(t0 * SR):int(t1 * SR)] = db(lvl)
gain = uniform_filter1d(gain, int(1.2 * SR), mode='nearest')
loop = bed_loop() * (ref * 4.0)   # escala relativa à voz
L = len(loop)
for i in range(0, N, L):
    n = min(L, N - i)
    mix[i:i + n] += loop[:n] * gain[i:i + n, None]
del gain

# ---------- 5. master ----------
pre = ROOT / 'mix_pre.wav'
sf.write(pre, mix, SR, subtype='FLOAT')
lines = block_lines(PLAN)
json.dump({'duration': total, 'regions': regions, 'marks': marks,
           'narr': [{'key': k, 'start': s, 'end': e, 'text': lines[k]} for t, k, s, e in marks if t == 'narr'],
           'host_secs': {k: round(len(v) / SR, 1) for k, v in host_parts.items()}},
          open(ROOT / 'timeline.json', 'w', encoding='utf8'), ensure_ascii=False, indent=1)

# loudnorm em 2 passadas: -14 LUFS integrado, true peak -1,5 dBTP (padrão Spotify)
r = subprocess.run([FF, '-hide_banner', '-i', str(pre), '-af',
                    'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                   capture_output=True, text=True)
m = json.loads(r.stderr[r.stderr.rindex('{'):r.stderr.rindex('}') + 1])
LN = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
      f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
out = EP / 'out'
out.mkdir(exist_ok=True)
name = PLAN['name']
ff('-i', str(pre), '-af', LN + ',alimiter=limit=0.85:attack=2:release=50:level=false', '-ar', '48000',
   '-c:a', 'pcm_s24le', str(out / f'{name}.wav'))
ff('-i', str(out / f'{name}.wav'), '-ar', '44100', '-c:a', 'libmp3lame', '-b:a', '320k',
   '-metadata', f"title={PLAN['title']}", '-metadata', 'artist=A Nova Ordem Educacional',
   '-metadata', 'album=A Nova Ordem Educacional', str(out / f'{name}.mp3'))
pre.unlink()

# ---------- 6. descrição com capítulos ----------
def ts(t):
    return f'{int(t // 60):02d}:{int(t % 60):02d}'


start = {k: s for t, k, s, e in marks if t == 'narr'}
ch = [f"00:00 Abertura — {PLAN['blocks']['cold']['title']}", f"{ts(start['intro'])} Apresentação do episódio"]
for i, k in enumerate(keys, 1):
    head = 'Encerramento' if i == len(keys) else f'Bloco {i}'
    ch.append(f"{ts(start[k])} {head} — {PLAN['blocks'][k]['title']}")
ch.append(f"{ts(start['recap'])} Para fixar: as 3 ideias do episódio")
desc = [PLAN['title'], '', PLAN['summary'], '', 'Capítulos', *ch, '']
if PLAN.get('refs'):
    desc += [PLAN['refs'], '']
if PLAN.get('youtube_id'):
    desc += [f"Assista em vídeo: https://youtu.be/{PLAN['youtube_id']}", '']
desc += ['Educação é estratégia.', '']
(out / f'{name}.txt').write_text('\n'.join(desc), encoding='utf8')
print(f'{EP.name}: master ok, {ts(total)}, blocos', json.dumps({k: round(len(v) / SR) for k, v in host_parts.items()}))
