"""REELS 3 (Short 03 "Planilha do chefe") — cut for the split-panel look of REELS 1-2 (session 2):
speech starts on frame 0, every silence above 0.25 s goes, two beats keep a little air so the picture can land,
and half a second of real image after the last word holds the comment CTA (REELS 2 kept 0.9 s).

Outputs (in this folder): transcripts/REELS3_refined.json, segments.json, words_out.json, base.mp4
Run: python -X utf8 cut.py
"""
import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).parent
SRC = str(HERE / "raw" / "source.mp4")   # a gravação vertical do Reel: copie para edit/raw/source.mp4
FPS = 30
PAD_IN, PAD_OUT = 0.05, 0.09      # air kept around each kept phrase
MAX_GAP = 0.25                    # pauses longer than this are cut (the script says: nothing above 0.3 s)
# extra air after word index (beats that need to land): "chamado?" (the door gag) / "preço." (half the coins fly off)
HOLD = {9: 0.10, 33: 0.16}
LAST_PAD = 0.50                   # he keeps looking at the camera for 1.2 s after the last word; 0.5 s holds the CTA
GRADE = "eq=contrast=1.07:brightness=0.025:saturation=1.10,unsharp=5:5:0.5"

# ---------- refine word edges ----------
d = json.load(open(HERE / "transcripts/REELS3.json", encoding="utf8"))
a16, sr16 = sf.read(str(HERE / "transcripts/REELS3.16k.wav"), dtype="float32")
hop = sr16 // 100
n = len(a16) // hop
db = 20 * np.log10(np.sqrt((a16[: n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12))
thr = np.percentile(db, 10) + 14
loud = db > thr
W = [w for w in d["words"] if w["type"] == "word"]

# silence runs (>= 0.15 s) of the whole take, in seconds
SIL, s0 = [], None
for i, v in enumerate(np.append(loud, True)):
    if not v and s0 is None:
        s0 = i
    if v and s0 is not None:
        if i - s0 >= 15:
            SIL.append((s0 / 100, i / 100))
        s0 = None

# Whisper glues a pause to the word before or after it, so a word window can hold "sound, long pause, sound".
# Walk the word boundaries left to right and move each one into the pause it belongs to:
#   pause sits after the boundary, only a short sound before it  -> that sound is the tail of the previous word
#   pause sits before the boundary, only a short onset after it  -> the next word really starts after the pause
for k in range(len(W) - 1):
    wk, wn = W[k], W[k + 1]
    bnd = wn["start"]
    for (p, q) in SIL:
        if bnd <= p and p - bnd <= 0.30 and q < wn["end"] - 0.04 and loud[int(q * 100): int(wn["end"] * 100)].any():
            print(f'  boundary {wk["text"]}|{wn["text"]}: {bnd:.2f} -> pause {p:.2f}-{q:.2f} (tail given back)')
            wk["end"], wn["start"] = p, q
            break
        if q <= bnd and bnd - q <= 0.25 and p > wk["start"] + 0.02:
            print(f'  boundary {wk["text"]}|{wn["text"]}: {bnd:.2f} -> pause {p:.2f}-{q:.2f} (onset given forward)')
            wk["end"], wn["start"] = p, q
            break

for w in W:
    i0, i1 = int(w["start"] * 100), max(int(w["start"] * 100) + 1, int(np.ceil(w["end"] * 100)))
    idx = np.nonzero(loud[i0:i1])[0]
    if len(idx) == 0:
        continue
    run = np.convolve(loud[i0:i1 + 4].astype(int), np.ones(5, int), "valid")     # 50 ms of continuous sound
    st = np.nonzero(run >= 5)[0]
    first = st[0] if len(st) else idx[0]                                         # ignores a click or breath before the word
    s = max(w["start"], (i0 + first) / 100 - 0.03)
    e = min(w["end"], (i0 + idx[-1] + 1) / 100 + 0.04)
    if e - s >= 0.08:
        w["start"], w["end"] = round(s, 3), round(e, 3)
json.dump({"words": W}, open(HERE / "transcripts/REELS3_refined.json", "w", encoding="utf8"), ensure_ascii=False, indent=0)

# ---------- segments: split wherever the pause is longer than MAX_GAP ----------
groups, cur = [], [0]
for k in range(1, len(W)):
    if W[k]["start"] - W[k - 1]["end"] > MAX_GAP:
        groups.append(cur)
        cur = []
    cur.append(k)
groups.append(cur)

segs, off = [], 0
for g in groups:
    s = max(0.0, W[g[0]]["start"] - (PAD_IN if segs else 0.0))        # the very first frame is already speech
    e = W[g[-1]]["end"] + (LAST_PAD if g[-1] == len(W) - 1 else PAD_OUT + HOLD.get(g[-1], 0.0))
    if segs:
        s = max(s, segs[-1]["end"])            # never overlap the previous segment
    f0 = int(np.floor(s * FPS))
    f1 = int(np.ceil(e * FPS))
    if segs and f0 < segs[-1]["f1"]:
        f0 = segs[-1]["f1"]
    segs.append({"i": len(segs), "f0": f0, "f1": f1, "start": f0 / FPS, "end": f1 / FPS, "out": off / FPS,
                 "words": g, "text": " ".join(W[k]["text"] for k in g)})
    off += f1 - f0
total_frames = off
json.dump(segs, open(HERE / "segments.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)

words_out = []
for sg in segs:
    for k in sg["words"]:
        w = W[k]
        words_out.append({"i": k, "seg": sg["i"], "text": w["text"],
                          "start": round(w["start"] - sg["start"] + sg["out"], 3),
                          "end": round(w["end"] - sg["start"] + sg["out"], 3)})
json.dump(words_out, open(HERE / "words_out.json", "w", encoding="utf8"), ensure_ascii=False, indent=0)
for sg in segs:
    print(f'{sg["i"]:2d} src {sg["start"]:6.2f}-{sg["end"]:6.2f} -> out {sg["out"]:6.2f}  {sg["text"]}')
print(f"total {total_frames / FPS:.2f}s ({total_frames} frames) from {len(segs)} segments")

# ---------- video: per-segment extract (graded, autorotated to 1080x1920) -> concat copy ----------
clips = HERE / "clips_graded"
clips.mkdir(exist_ok=True)
lst = []
for sg in segs:
    nf = sg["f1"] - sg["f0"]
    out = clips / f'seg_{sg["f0"]:05d}_{nf:04d}.mp4'      # keyed by content, not index
    ok = False
    if out.exists():
        r = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0", "-show_entries",
                            "stream=nb_read_frames", "-of", "csv=p=0", str(out)], capture_output=True, text=True)
        ok = r.stdout.strip() == str(nf)
    if not ok:
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f'{sg["start"]:.5f}', "-i", SRC, "-frames:v", str(nf), "-an",
                        "-vf", f"{GRADE},fps={FPS},format=yuv420p,setsar=1",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "14", "-g", "30",
                        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", str(out)], check=True)
    lst.append(f"file '{out.as_posix()}'")
(HERE / "concat.txt").write_text("\n".join(lst), encoding="utf8")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(HERE / "concat.txt"), "-c", "copy",
                str(HERE / "video_only.mp4")], check=True)

# ---------- audio: slice in numpy with 30 ms fades, light voice polish ----------
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-vn", "-ac", "1", "-ar", "48000", str(HERE / "source_48k.wav")], check=True)
a, sr = sf.read(str(HERE / "source_48k.wav"), dtype="float32")
fade = int(0.03 * sr)
ramp = np.linspace(0, 1, fade, dtype="float32")
parts = []
for sg in segs:
    x = a[int(round(sg["start"] * sr)): int(round(sg["start"] * sr)) + (sg["f1"] - sg["f0"]) * sr // FPS].copy()
    x[:fade] *= ramp
    x[-fade:] *= ramp[::-1]
    parts.append(x)
sf.write(str(HERE / "audio_raw.wav"), np.concatenate(parts), sr)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / "audio_raw.wav"), "-af",
                "highpass=f=85,afftdn=nr=8:nf=-45,acompressor=threshold=-20dB:ratio=3:attack=8:release=120:makeup=3,"
                "equalizer=f=3200:t=q:w=1.2:g=2", str(HERE / "audio_voice.wav")], check=True)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(HERE / "video_only.mp4"), "-i", str(HERE / "audio_voice.wav"),
                "-c:v", "copy", "-c:a", "aac", "-b:a", "256k", "-shortest", str(HERE / "base.mp4")], check=True)
r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=width,height,nb_frames", "-of", "csv=p=0",
                    str(HERE / "base.mp4")], capture_output=True, text=True)
print("base.mp4:", r.stdout.replace("\n", " | "))
