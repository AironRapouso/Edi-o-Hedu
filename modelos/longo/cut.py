"""EP7 (YouTube, 16:9) — cut the take into the output timeline.

Output timeline = HOOK (cold open, source spans) + VINHETA (8 s gap, the channel intro) + BODY (source spans, every
pause > MAX_GAP removed, DROP ranges removed) + TELA_FINAL (20 s gap, end screen).
Video comes from ../raw/staged.mp4 (already cropped so the BIGVU watermark corner is outside the frame, 1920x1080).

plan.py defines:  HOOK = [(i0, i1), ...]   source word ranges played before the vinheta (in this order)
                  DROP = [(i0, i1, why), ...]  source word ranges removed from the body
                  HOLD = {i: seconds}          extra air after word i
Outputs: transcripts/EP7_refined.json, segments.json, words_out.json, video_only.mp4, audio_raw.wav (output timeline,
silence in the gaps), source_48k.wav
Run: python -X utf8 cut.py
"""
import json
import subprocess
from pathlib import Path

import numpy as np
import soundfile as sf

HERE = Path(__file__).parent
SRC = HERE.parent / "raw" / "source.mp4"
STAGED = SRC
FPS = 30
PAD_IN, PAD_OUT = 0.05, 0.10
MAX_GAP = 0.28
GAPS = {"VINHETA": 8.0, "TELA_FINAL": 20.0, **{f"I{k}": 2.2 for k in range(1, 10)}}
exec(open(HERE / "plan.py", encoding="utf8").read())          # HOOK, DROP, HOLD

# ---------- refine word edges (energy) ----------
d = json.load(open(HERE / "transcripts/EP7.json", encoding="utf8"))
a16, sr16 = sf.read(str(HERE / "transcripts/EP7.16k.wav"), dtype="float32")
hop = sr16 // 100
n = len(a16) // hop
db = 20 * np.log10(np.sqrt((a16[: n * hop].reshape(n, hop) ** 2).mean(1) + 1e-12))
thr = np.percentile(db, 10) + 14
loud = db > thr
W = [w for w in d["words"] if w["type"] == "word"]
SIL, s0 = [], None
for i, v in enumerate(np.append(loud, True)):
    if not v and s0 is None:
        s0 = i
    if v and s0 is not None:
        if i - s0 >= 15:
            SIL.append((s0 / 100, i / 100))
        s0 = None
for k in range(len(W) - 1):                                    # move boundaries into the real pauses
    wk, wn = W[k], W[k + 1]
    bnd = wn["start"]
    for (p, q) in SIL:
        if bnd <= p and p - bnd <= 0.30 and q < wn["end"] - 0.04 and loud[int(q * 100): int(wn["end"] * 100)].any():
            wk["end"], wn["start"] = p, q
            break
        if q <= bnd and bnd - q <= 0.25 and p > wk["start"] + 0.02:
            wk["end"], wn["start"] = p, q
            break
for w in W:
    i0, i1 = int(w["start"] * 100), max(int(w["start"] * 100) + 1, int(np.ceil(w["end"] * 100)))
    idx = np.nonzero(loud[i0:i1])[0]
    if len(idx) == 0:
        continue
    run = np.convolve(loud[i0:i1 + 4].astype(int), np.ones(5, int), "valid")
    st = np.nonzero(run >= 5)[0]
    first = st[0] if len(st) else idx[0]
    s = max(w["start"], (i0 + first) / 100 - 0.03)
    e = min(w["end"], (i0 + idx[-1] + 1) / 100 + 0.04)
    if e - s >= 0.08:
        w["start"], w["end"] = round(s, 3), round(e, 3)
json.dump({"words": W}, open(HERE / "transcripts/EP7_refined.json", "w", encoding="utf8"), ensure_ascii=False, indent=0)


def groups_of(idx):
    """split a sorted list of word indices into runs without long pauses / jumps"""
    out, cur = [], []
    for k in idx:
        if cur and (k != cur[-1] + 1 or W[k]["start"] - W[cur[-1]]["end"] > MAX_GAP):
            out.append(cur)
            cur = []
        cur.append(k)
    if cur:
        out.append(cur)
    return out


dropped = set()
for a, b, _ in DROP:
    dropped.update(range(a, b + 1))
hook_idx = [list(range(a, b + 1)) for a, b in HOOK]
in_hook = {k for r in hook_idx for k in r}
body_idx = [k for k in range(len(W)) if k not in dropped and k not in in_hook]

plan = []                                                     # ("src", label, [word idx]) | ("gap", label)
for r in hook_idx:
    plan += [("src", "HOOK", g) for g in groups_of(r)]
plan.append(("gap", "VINHETA"))
INTER = globals().get("INTER", {})                 # {source word index: gap label} -> intertitle gap before that word
for g in groups_of(body_idx):
    cur = []
    for k in g:
        if k in INTER:
            if cur:
                plan.append(("src", "BODY", cur))
                cur = []
            plan.append(("gap", INTER[k]))
        cur.append(k)
    if cur:
        plan.append(("src", "BODY", cur))
plan.append(("gap", "TELA_FINAL"))

segs, off = [], 0
for p in plan:
    if p[0] == "gap":
        nf = int(round(GAPS[p[1]] * FPS))
        segs.append({"i": len(segs), "kind": "gap", "label": p[1], "out": off / FPS, "frames": nf})
        off += nf
        continue
    _, label, g = p
    prev_src = segs[-1] if segs and segs[-1]["kind"] == "src" and segs[-1]["label"] == label else None
    s = max(0.0, W[g[0]]["start"] - PAD_IN)
    e = W[g[-1]]["end"] + PAD_OUT + HOLD.get(g[-1], 0.0)
    if prev_src and g[0] == prev_src["words"][-1] + 1:
        s = max(s, prev_src["e"])
    f0, f1 = int(np.floor(s * FPS)), int(np.ceil(e * FPS))
    if prev_src and g[0] == prev_src["words"][-1] + 1 and f0 < prev_src["f1"]:
        f0 = prev_src["f1"]
    segs.append({"i": len(segs), "kind": "src", "label": label, "f0": f0, "f1": f1, "s": f0 / FPS, "e": f1 / FPS,
                 "out": off / FPS, "frames": f1 - f0, "words": g, "text": " ".join(W[k]["text"] for k in g)})
    off += f1 - f0
TOTAL_F = off
json.dump(segs, open(HERE / "segments.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)

words_out = []
for sg in segs:
    if sg["kind"] != "src":
        continue
    for k in sg["words"]:
        w = W[k]
        words_out.append({"i": k, "seg": sg["i"], "label": sg["label"], "text": w["text"],
                          "start": round(w["start"] - sg["s"] + sg["out"], 3), "end": round(w["end"] - sg["s"] + sg["out"], 3)})
json.dump(words_out, open(HERE / "words_out.json", "w", encoding="utf8"), ensure_ascii=False, indent=0)
nsrc = sum(1 for s in segs if s["kind"] == "src")
print(f"total {TOTAL_F / FPS:.2f}s ({TOTAL_F} frames), {nsrc} source segments, {len(words_out)} words kept of {len(W)}")
for a, b, why in DROP:
    print(f"  dropped {a}-{b} ({why}): {' '.join(W[k]['text'] for k in range(a, b + 1))[:110]}")

# ---------- video: per-segment extract from the staged (cropped) source, gaps = black ----------
clips = HERE / "clips"
clips.mkdir(exist_ok=True)
lst = []
for sg in segs:
    nf = sg["frames"]
    if sg["kind"] == "gap":
        out = clips / f"gap_{nf:05d}.mp4"
        if not out.exists():
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"color=c=0x010B25:s=1920x1080:r={FPS}", "-frames:v", str(nf),
                            "-vf", "format=yuv420p,setsar=1", "-c:v", "libx264", "-preset", "veryfast", "-crf", "18", "-g", "30",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", str(out)], check=True)
    else:
        out = clips / f"seg_{sg['f0']:06d}_{nf:05d}.mp4"
        ok = False
        if out.exists():
            r = subprocess.run(["ffprobe", "-v", "error", "-count_packets", "-select_streams", "v:0", "-show_entries",
                                "stream=nb_read_packets", "-of", "csv=p=0", str(out)], capture_output=True, text=True)
            ok = r.stdout.strip() == str(nf)
        if not ok:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{sg['s']:.5f}", "-i", str(STAGED), "-frames:v", str(nf), "-an",
                            "-vf", f"crop=1600:900:122:30,scale=1920:1080:flags=lanczos,fps={FPS},format=yuv420p,setsar=1", "-c:v", "libx264", "-preset", "veryfast", "-crf", "15", "-g", "30",
                            "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709", str(out)], check=True)
    lst.append(f"file '{out.as_posix()}'")
(HERE / "concat.txt").write_text("\n".join(lst), encoding="utf8")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", str(HERE / "concat.txt"), "-c", "copy",
                str(HERE / "video_only.mp4")], check=True)

# ---------- audio on the output timeline: numpy slices with 25 ms fades, silence in the gaps ----------
if not (HERE / "source_48k.wav").exists():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(SRC), "-vn", "-ac", "1", "-ar", "48000", str(HERE / "source_48k.wav")], check=True)
a, sr = sf.read(str(HERE / "source_48k.wav"), dtype="float32")
fade = int(0.025 * sr)
ramp = np.linspace(0, 1, fade, dtype="float32")
parts = []
for sg in segs:
    n = sg["frames"] * sr // FPS
    if sg["kind"] == "gap":
        parts.append(np.zeros(n, "float32"))
        continue
    i0 = int(round(sg["s"] * sr))
    x = a[i0: i0 + n].copy()
    if len(x) < n:
        x = np.pad(x, (0, n - len(x)))
    x[:fade] *= ramp
    x[-fade:] *= ramp[::-1]
    parts.append(x)
sf.write(str(HERE / "audio_raw.wav"), np.concatenate(parts), sr)
r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(HERE / "video_only.mp4")],
                   capture_output=True, text=True)
print("video_only.mp4:", r.stdout.strip(), "s | expected", TOTAL_F / FPS)
