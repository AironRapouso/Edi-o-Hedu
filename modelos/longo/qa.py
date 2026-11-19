"""QA of a rendered Reel: stream facts, loudness, freezes/blank frames, A/V offset against the cut voice track,
RMS per section and contact sheets (3 fps) to look at. Nothing here can hear: the audio is only measured.

Usage: python -X utf8 qa.py <final.mp4> [<cut voice wav>]      (run from the edit folder)
"""
import re
import subprocess
import sys
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).parent
final = Path(sys.argv[1])
voice = Path(sys.argv[2]) if len(sys.argv) > 2 else HERE / "audio_voice.wav"
out = HERE / "verify" / "qa"
out.mkdir(parents=True, exist_ok=True)
for f in out.glob("s_*.jpg"):
    f.unlink()


def run(args):
    return subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")


p = run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_name,width,height,r_frame_rate,nb_frames,pix_fmt,color_transfer",
         "-of", "default=nw=1", str(final)]).stdout
print(" | ".join(p.split()))
r = run(["ffmpeg", "-hide_banner", "-i", str(final), "-af", "ebur128=peak=true", "-f", "null", "-"]).stderr
tail = r[r.rindex("Summary"):]
print("loudness:", re.search(r"I:\s+(-?[\d.]+) LUFS", tail).group(1), "LUFS | true peak", re.search(r"Peak:\s+(-?[\d.]+) dBFS", tail).group(1),
      "dBFS | LRA", re.search(r"LRA:\s+([\d.]+) LU", tail).group(1), "LU")
r = run(["ffmpeg", "-hide_banner", "-i", str(final), "-vf", "freezedetect=n=-50dB:d=0.4,blackdetect=d=0.1", "-an", "-f", "null", "-"]).stderr
ev = re.findall(r"(freeze_start: [\d.]+|freeze_duration: [\d.]+|black_start:[\d.]+ black_end:[\d.]+)", r)
print("freezes / black frames:", ev or "none")

run(["ffmpeg", "-v", "error", "-y", "-i", str(final), "-vn", "-ac", "1", "-ar", "16000", str(out / "final.wav")])
run(["ffmpeg", "-v", "error", "-y", "-i", str(voice), "-ac", "1", "-ar", "16000", str(out / "voice.wav")])
a, _ = sf.read(str(out / "final.wav"))
b, _ = sf.read(str(out / "voice.wav"))
n = min(len(a), len(b))
a, b = a[:n], b[:n]


def env(x):
    m = len(x) // 160
    e = np.abs(x[: m * 160]).reshape(m, 160).mean(1)
    return e - e.mean()


ea, eb = env(a), env(b)
best = max(range(-30, 31), key=lambda k: float(np.dot(ea[max(0, k): len(ea) + min(0, k)], eb[max(0, -k): len(eb) + min(0, -k)])))
print("audio offset, final vs cut voice:", best * 10, "ms")
third = len(a) // 3
for k, name in enumerate(("first third", "middle third", "last third")):
    x = a[k * third: (k + 1) * third]
    print(f"RMS {name}: {20 * np.log10(np.sqrt((x ** 2).mean())):.1f} dBFS")
run(["ffmpeg", "-v", "error", "-y", "-i", str(final), "-vf", "fps=3,scale=270:480,tile=8x3", "-q:v", "3", str(out / "s_%02d.jpg")])
print("sheets:", ", ".join(sorted(f.name for f in out.glob("s_*.jpg"))))
