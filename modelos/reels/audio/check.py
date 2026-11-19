"""Checks on the new soundtrack (nothing here can hear - these are measurements):
  - room tone left in the pauses, before vs after the voice treatment
  - where effects come close to the voice level in the speech band (masking risk)
  - A/V alignment of the final file against the cut voice
  - loudness / true peak of the final file, and a picture of the two stems
Run from the edit folder:  python -X utf8 audio/check.py
"""
import json
import re
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf
from scipy import signal

HERE = Path(__file__).resolve().parent
EDIT = HERE.parent
SR = 48000
final = EDIT.parent / f"{EDIT.parent.name}_final.mp4"


def rms_db(x):
    return 20 * np.log10(np.sqrt(np.mean(np.square(x))) + 1e-12)


raw, _ = sf.read(str(EDIT / "audio_raw.wav"), dtype="float64")
voice, _ = sf.read(str(HERE / "stem_voice.wav"), dtype="float64")
sfx, _ = sf.read(str(HERE / "stem_sfx.wav"), dtype="float64")
voice = voice[:, 0]
W = json.load(open(EDIT / "words_out.json", encoding="utf8"))

# ---- room tone in the pauses (frames with no word within 60 ms)
hop = SR // 50
n = min(len(raw), len(voice)) // hop
busy = np.zeros(n, bool)
for w in W:
    busy[max(0, int((w["start"] - 0.06) * 50)): int((w["end"] + 0.06) * 50) + 1] = True
fr = lambda x: x[: n * hop].reshape(n, hop)
pr, pv = (fr(raw) ** 2).mean(1), (fr(voice) ** 2).mean(1)
quiet = ~busy
print(f"pauses: {quiet.sum() * 0.02:.2f} s of the cut")
print(f"  before: speech {10 * np.log10(pr[busy].mean()):.1f} dBFS, pauses {10 * np.log10(pr[quiet].mean()):.1f} dBFS -> {10 * np.log10(pr[busy].mean() / pr[quiet].mean()):.1f} dB apart")
print(f"  after : speech {10 * np.log10(pv[busy].mean()):.1f} dBFS, pauses {10 * np.log10(pv[quiet].mean()):.1f} dBFS -> {10 * np.log10(pv[busy].mean() / pv[quiet].mean()):.1f} dB apart")

# ---- masking: effects vs voice in the speech band, 100 ms windows
sos = signal.butter(2, [300, 3400], "bandpass", fs=SR, output="sos")
vb = signal.sosfilt(sos, voice)
sb = signal.sosfilt(sos, sfx.mean(1))
h = SR // 10
m = min(len(vb), len(sb)) // h
lv = 10 * np.log10((vb[: m * h].reshape(m, h) ** 2).mean(1) + 1e-12)
ls = 10 * np.log10((sb[: m * h].reshape(m, h) ** 2).mean(1) + 1e-12)
speaking = lv > np.percentile(lv, 90) - 25
close = [(i / 10, ls[i] - lv[i]) for i in range(m) if speaking[i] and ls[i] - lv[i] > -6]
print(f"effects within 6 dB of the voice in the speech band (300-3400 Hz), while he speaks: {len(close)} windows of 100 ms out of {int(speaking.sum())}")
for t, d in close:
    wd = next((w["text"] for w in W if w["start"] - 0.05 <= t + 0.05 <= w["end"] + 0.05), "(gap)")
    print(f"  {t:5.1f} s  effects {d:+.1f} dB vs voice   on '{wd}'")
print(f"effects stem: {rms_db(sfx):.1f} dBFS rms, voice stem {rms_db(voice):.1f} dBFS rms -> effects {rms_db(voice) - rms_db(sfx):.1f} dB under the voice on average")

# ---- final file
r = subprocess.run(["ffmpeg", "-hide_banner", "-i", str(final), "-af", "ebur128=peak=true", "-f", "null", "-"], capture_output=True, text=True,
                   encoding="utf-8", errors="replace").stderr
tail = r[r.rindex("Summary"):]
print("final file:", re.search(r"I:\s+(-?[\d.]+) LUFS", tail).group(1), "LUFS | true peak", re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail).group(1),
      "dBTP | LRA", re.search(r"LRA:\s+([\d.]+) LU", tail).group(1), "LU")
p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_name,channels,sample_rate,nb_frames", "-of", "default=nw=1", str(final)],
                   capture_output=True, text=True).stdout
print(" | ".join(p.split()))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(final), "-vn", "-ac", "1", "-ar", "16000", str(HERE / "_final16.wav")])
a, _ = sf.read(str(HERE / "_final16.wav"))
b = signal.resample_poly(raw, 1, 3)
k = min(len(a), len(b))
env = lambda x: (lambda e: e - e.mean())(np.abs(x[: len(x) // 160 * 160]).reshape(-1, 160).mean(1))
ea, eb = env(a[:k]), env(b[:k])
best = max(range(-30, 31), key=lambda s: float(np.dot(ea[max(0, s): len(ea) + min(0, s)], eb[max(0, -s): len(eb) + min(0, -s)])))
print("audio offset, final vs the cut voice:", best * 10, "ms")
(HERE / "_final16.wav").unlink()

# ---- picture of the stems (voice on top, effects below)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / "stem_voice.wav"), "-i", str(HERE / "stem_sfx.wav"), "-filter_complex",
                "[0:a]aformat=channel_layouts=mono,showwavespic=s=2400x260:colors=0x0457E7:scale=sqrt[v];"
                "[1:a]aformat=channel_layouts=mono,showwavespic=s=2400x260:colors=0xE5484D:scale=sqrt[s];[v][s]vstack,pad=2400:540:0:10:white",
                "-frames:v", "1", str(HERE / "stems.png")])
print("stems picture:", HERE / "stems.png")
