"""How hot are the sibilants (s, z, ch) compared with the body of the voice? Raw cut vs treated stem.
Level of the 4.5-10 kHz band in 5 ms frames, relative to the speech rms of the same file.
Run from the edit folder:  python -X utf8 audio/sibilance.py <wav> [<wav> ...]
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

EDIT = Path(__file__).resolve().parent.parent
W = json.load(open(EDIT / "words_out.json", encoding="utf8"))
for name in sys.argv[1:]:
    x, sr = sf.read(name, dtype="float64")
    if x.ndim > 1:
        x = x[:, 0]
    hf = signal.sosfiltfilt(signal.butter(2, [4500, 10000], "bandpass", fs=sr, output="sos"), x)
    n = sr // 200
    m = len(x) // n
    e_hf = 10 * np.log10((hf[: m * n].reshape(m, n) ** 2).mean(1) + 1e-12)
    e_all = 10 * np.log10((x[: m * n].reshape(m, n) ** 2).mean(1) + 1e-12)
    speech = 10 * np.log10(np.mean(x ** 2))
    rel = e_hf - speech
    print(f"\n{name}: speech rms {speech:.1f} dBFS | sibilant band vs speech rms: p90 {np.percentile(rel, 90):+.1f}  p99 {np.percentile(rel, 99):+.1f}  "
          f"p99.9 {np.percentile(rel, 99.9):+.1f}  max {rel.max():+.1f} dB | peak of the band {20 * np.log10(np.abs(hf).max()):.1f} dBFS vs full peak {20 * np.log10(np.abs(x).max()):.1f}")
    top = np.argsort(rel)[::-1]
    seen = []
    for i in top:
        t = i * n / sr
        if all(abs(t - s) > 0.12 for s in seen):
            seen.append(t)
            wd = next((w["text"] for w in W if w["start"] - 0.05 <= t <= w["end"] + 0.05), "(gap)")
            print(f"   {t:6.2f} s  {rel[i]:+5.1f} dB  {wd}")
        if len(seen) == 7:
            break
