"""Measure the cut voice before treating it: noise floor, tonal balance, level of each phrase/word, peaks.
Run from the edit folder:  python -X utf8 audio/analyze_voice.py [wav]   (default: audio_raw.wav)
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

EDIT = Path(__file__).resolve().parent.parent
wav = Path(sys.argv[1]) if len(sys.argv) > 1 else EDIT / "audio_raw.wav"
x, sr = sf.read(str(wav), dtype="float32")
if x.ndim > 1:
    x = x.mean(1)
src, _ = sf.read(str(EDIT / "source_48k.wav"), dtype="float32")
noise = src[int(0.12 * sr): int(0.95 * sr)]            # room tone before he starts speaking

BANDS = [(40, 80), (80, 160), (160, 320), (320, 640), (640, 1250), (1250, 2500), (2500, 5000), (5000, 8000), (8000, 12000), (12000, 20000)]


def band_db(sig):
    n = 4096
    hop = n // 2
    win = np.hanning(n)
    acc = np.zeros(n // 2 + 1)
    k = 0
    for i in range(0, len(sig) - n, hop):
        acc += np.abs(np.fft.rfft(sig[i: i + n] * win)) ** 2
        k += 1
    acc /= max(k, 1) * (win ** 2).sum()
    f = np.fft.rfftfreq(n, 1 / sr)
    return [10 * np.log10(acc[(f >= lo) & (f < hi)].sum() + 1e-15) for lo, hi in BANDS]


def rms_db(sig):
    return 20 * np.log10(np.sqrt((sig ** 2).mean()) + 1e-9)


print(f"file {wav.name}: {len(x) / sr:.2f} s, peak {20 * np.log10(np.abs(x).max()):.1f} dBFS, rms {rms_db(x):.1f} dBFS, crest {20 * np.log10(np.abs(x).max()) - rms_db(x):.1f} dB")
print(f"room tone (source 0.12-0.95 s): rms {rms_db(noise):.1f} dBFS")
sb, nb = band_db(x), band_db(noise)
print("band (Hz)        speech   noise   S/N")
for (lo, hi), s, n in zip(BANDS, sb, nb):
    print(f"{lo:>6}-{hi:<6} {s:8.1f} {n:7.1f} {s - n:6.1f}")

# level of each word (and of each cut segment) on the output timeline
W = json.load(open(EDIT / "words_out.json", encoding="utf8"))
S = json.load(open(EDIT / "segments.json", encoding="utf8"))
print("\nsegment levels (rms dBFS):")
for sg in S:
    a = int(sg["out"] * sr)
    b = a + (sg["f1"] - sg["f0"]) * sr // 30
    print(f'  {sg["out"]:6.2f}  {rms_db(x[a:b]):6.1f}  {sg["text"]}')
lv = [(rms_db(x[int(w["start"] * sr): max(int(w["end"] * sr), int(w["start"] * sr) + 480)]), w["text"], w["start"]) for w in W]
med = np.median([v[0] for v in lv])
print(f"\nword levels: median {med:.1f} dBFS; quietest words:")
for v in sorted(lv)[:8]:
    print(f"  {v[2]:6.2f}  {v[0]:6.1f} ({v[0] - med:+.1f})  {v[1]}")
print("loudest words:")
for v in sorted(lv)[-5:]:
    print(f"  {v[2]:6.2f}  {v[0]:6.1f} ({v[0] - med:+.1f})  {v[1]}")
# sibilance: 5-9 kHz energy relative to 1-4 kHz, per 20 ms frame, 95th percentile
n = 960
fr = len(x) // n
X = np.abs(np.fft.rfft(x[: fr * n].reshape(fr, n) * np.hanning(n), axis=1)) ** 2
f = np.fft.rfftfreq(n, 1 / sr)
hi = X[:, (f >= 5000) & (f < 9000)].sum(1)
mid = X[:, (f >= 1000) & (f < 4000)].sum(1)
act = (X.sum(1) > np.percentile(X.sum(1), 40))
ratio = 10 * np.log10((hi[act] + 1e-12) / (mid[act] + 1e-12))
print(f"\nsibilance index (5-9 kHz vs 1-4 kHz): median {np.median(ratio):.1f} dB, 95th pct {np.percentile(ratio, 95):.1f} dB")
