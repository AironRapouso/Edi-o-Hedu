"""Frame-exact checks of the FINAL video (split-panel version, session 2):
  - eye line and face size in the face panel on the first frame, the last frame (loop) and right after every jump cut
    that is visible (expected: the anchor of hf/build.py, glasses = G0 x the punch-in of that segment)
  - the caption pill is there on every single frame
  - the two full-screen takeovers really cover the face, and the face is back afterwards
Run from the edit folder:  python -X utf8 verify_final.py
"""
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image

HERE = Path(__file__).parent
FIN = HERE.parent / f"{HERE.parent.name}_final.mp4"
R = json.load(open(HERE / "hf" / "reel.json", encoding="utf8"))
T, SEAM = R["T"], R["seam"]
XA, YA = R["anchor"]
N = round(R["total"] * 30)
out = HERE / "verify" / "final2"
out.mkdir(parents=True, exist_ok=True)


def hidden(t):                      # the paper cover is over the face (or still moving)
    return (T["fs1"] - 0.06 <= t < T["sc3"] + 0.26) or (T["fs2"] - 0.06 <= t < T["sc5"] + 0.26)


frames = {"first": 0, "last": N - 1}
for sh in R["shots"]:
    if sh["t"] > 0 and not hidden(sh["t"]):
        frames[f'seg{sh["seg"]:02d} cut'] = round(sh["t"] * 30)
for k, key in ((2, "sc3"), (8, "sc5")):
    frames[f"seg{k:02d} +0.3s"] = round((T[key] + 0.3) * 30)
order = {f: i + 1 for i, f in enumerate(sorted(set(frames.values())))}
sel = "+".join(f"eq(n\\,{f})" for f in order)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(FIN), "-vf", f"select='{sel}'", "-fps_mode", "passthrough", str(out / "f_%03d.png")], check=True)


def eyes(name):
    a = np.asarray(Image.open(out / f"f_{order[frames[name]]:03d}.png").convert("RGB")).astype(int)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = (b > r + 26) & (b > g + 18) & (b > 62)
    m[: SEAM + 170] = False
    m[SEAM + 640:] = False
    m[:, :190] = False
    m[:, 930:] = False
    ys, xs = np.nonzero(m)
    if len(xs) < 150:
        return None
    x0, x1 = np.percentile(xs, [3, 97])
    return (x0 + x1) / 2, float(np.median(ys)) + 0.123 * (x1 - x0), x1 - x0


zoom = {s["seg"]: s["zoom"] for s in R["shots"]}
print(f"{FIN.name}: {N} frames; expected eye line ({XA:.0f}, {SEAM + YA:.0f})")
for name in sorted(frames, key=lambda k: frames[k]):
    e = eyes(name)
    print(f"  frame {frames[name]:4d} {name:12s} " + (f"eyes ({e[0]:6.1f}, {e[1]:6.1f})  off ({e[0] - XA:+5.1f}, {e[1] - SEAM - YA:+5.1f})  glasses {e[2]:5.1f} px" if e else "glasses not found"))
a, b = eyes("first"), eyes("last")
print(f"loop: last frame vs first frame -> eyes differ by ({b[0] - a[0]:+.1f}, {b[1] - a[1]:+.1f}) px, face size by {(b[2] / a[2] - 1) * 100:+.1f} %")

# ---- every frame at quarter size: the pill, and what the face region holds
W4, H4 = 270, 480
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(FIN), "-vf", f"scale={W4}:{H4}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
no_pill, paper, n = [], [], 0
while True:
    buf = p.stdout.read(W4 * H4 * 3)
    if len(buf) < W4 * H4 * 3:
        break
    f = np.frombuffer(buf, np.uint8).reshape(H4, W4, 3).astype(int)
    band = f[SEAM // 4 - 4: SEAM // 4 + 5]
    navy = (band[..., 0] < 45) & (band[..., 1] < 55) & (band[..., 2] < 95) & (band[..., 2] > band[..., 0] + 8)
    if navy.any(0).mean() < 0.12:
        no_pill.append(n)
    reg = f[330:460, 20:250]                                    # lower part of the face panel
    paper.append(bool((reg.min(-1) > 205).mean() > 0.9))
    n += 1
p.stdout.close()
p.wait()
starts = {round(c["s"] * 30) for c in R["caps"]}                 # on its first frame the pill is at 55 % opacity (it pops in)
other = [f for f in no_pill if f not in starts]
print(f"frames read: {n}; solid caption pill missing on {len(no_pill)} frames: {len(no_pill) - len(other)} are the first frame of a caption "
      f"(pill at 55 % while it pops in), others: {other}")
runs, s0 = [], None
for i, v in enumerate(paper + [False]):
    if v and s0 is None:
        s0 = i
    if not v and s0 is not None:
        runs.append((s0, i - 1))
        s0 = None
print("face fully covered by paper on frames:", ", ".join(f"{a}-{b} ({a / 30:.2f}-{(b + 1) / 30:.2f} s)" for a, b in runs))
print(f"expected full screens: {T['fs1']:.2f}-{T['sc3']:.2f} s and {T['fs2']:.2f}-{T['sc5']:.2f} s (the wipe takes 0.26 s on each side)")
