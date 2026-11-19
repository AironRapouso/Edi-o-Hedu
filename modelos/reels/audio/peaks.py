"""Where do the peaks of a voice file come from? Prints level percentiles and the loudest instants.
Run from the edit folder:  python -X utf8 audio/peaks.py <wav> [<wav> ...]
"""
import json
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

EDIT = Path(__file__).resolve().parent.parent
W = json.load(open(EDIT / "words_out.json", encoding="utf8"))


def word_at(t):
    for w in W:
        if w["start"] - 0.03 <= t <= w["end"] + 0.03:
            return w["text"]
    return "(gap)"


for name in sys.argv[1:]:
    x, sr = sf.read(name, dtype="float64")
    if x.ndim > 1:
        x = x[:, 0]
    a = np.abs(x)
    rms = 20 * np.log10(np.sqrt((x ** 2).mean()))
    pct = {p: 20 * np.log10(np.percentile(a, p) + 1e-12) for p in (50, 90, 99, 99.9, 99.99)}
    print(f"\n{name}: rms {rms:.1f} dBFS, max {20 * np.log10(a.max()):.1f} | percentiles " + " ".join(f"p{p}={v:.1f}" for p, v in pct.items()))
    # speech-only rms (frames above the gate)
    n = sr // 50
    fr = a[: len(a) // n * n].reshape(-1, n)
    lv = 20 * np.log10(np.sqrt((fr ** 2).mean(1)) + 1e-12)
    act = lv > np.percentile(lv, 95) - 30
    print(f"  speech-active frames {act.mean() * 100:.0f} %: rms {10 * np.log10((fr[act] ** 2).mean()):.1f} dBFS -> crest {20 * np.log10(a.max()) - 10 * np.log10((fr[act] ** 2).mean()):.1f} dB")
    # the loudest 8 instants (at least 150 ms apart)
    order = np.argsort(a)[::-1]
    seen = []
    for i in order:
        if all(abs(i - j) > 0.15 * sr for j in seen):
            seen.append(i)
            # how long does the signal stay within 6 dB of this peak?
            near = a[max(0, i - 2400): i + 2400] > a[i] * 0.5
            print(f"  {i / sr:6.2f} s  {20 * np.log10(a[i]):6.1f} dBFS  {word_at(i / sr):14s} samples within 6 dB (+-50 ms): {int(near.sum())}")
        if len(seen) == 8:
            break
