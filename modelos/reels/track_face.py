"""Track his eye line on EVERY frame of base.mp4 (the cut), so the framing can follow him smoothly.

The glasses have a saturated blue-violet rim, found by colour inside a window around the previous position.
x and w come from the horizontal extent (stable). The bottom rim flickers in the mask, so y comes from the
median row of the mask (the thick top rim) plus 0.123 x width = the centre of the lenses.
Output: track.json = one row per frame {x, y, w, n} in source pixels (1080x1920). hf/build.py takes the first
frames of each cut segment (the last frames of the final one) to place every shot on the same eye line.

Run from the edit folder:  python -X utf8 track_face.py
"""
import json
import subprocess
from pathlib import Path

import numpy as np

HERE = Path(__file__).parent
SEGS = json.load(open(HERE / "segments.json", encoding="utf8"))
N = sum(s["f1"] - s["f0"] for s in SEGS)
SC = 2                                    # analyse at half resolution
W, H = 1080 // SC, 1920 // SC
p = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(HERE / "base.mp4"), "-vf", f"scale={W}:{H}", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"],
                     stdout=subprocess.PIPE)
rows, prev = [], None
for f in range(N):
    buf = p.stdout.read(W * H * 3)
    if len(buf) < W * H * 3:
        break
    a = np.frombuffer(buf, np.uint8).reshape(H, W, 3).astype(np.int16)
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = (b > r + 26) & (b > g + 18) & (b > 62)
    m[: 400 // SC] = False
    m[1180 // SC:] = False
    m[:, : 230 // SC] = False
    m[:, 970 // SC:] = False
    if prev is not None:                  # only look around where the glasses were one frame ago
        x, y, w = prev
        m[: int((y - 150) / SC)] = False
        m[int((y + 150) / SC):] = False
        m[:, : max(0, int((x - w * 0.5 - 130) / SC))] = False
        m[:, int((x + w * 0.5 + 130) / SC):] = False
    ys, xs = np.nonzero(m)
    if len(xs) < 60:
        rows.append({"f": f, "x": None, "y": None, "w": None, "n": int(len(xs))})
        continue
    x0, x1 = np.percentile(xs, [3, 97])
    y0, y1 = np.percentile(ys, [3, 97])
    wpx = (x1 - x0) * SC
    cur = ((x0 + x1) / 2 * SC, float(np.median(ys)) * SC + 0.123 * wpx, wpx)
    rows.append({"f": f, "x": round(cur[0], 1), "y": round(cur[1], 1), "w": round(cur[2], 1), "n": int(len(xs))})
    prev = cur
p.stdout.close()
p.wait()
json.dump(rows, open(HERE / "track.json", "w", encoding="utf8"))
ok = [r for r in rows if r["x"] is not None]
print(f"{len(rows)} frames read ({N} expected), glasses found on {len(ok)}")
off = 0
for sg in SEGS:
    n = sg["f1"] - sg["f0"]
    seg = [r for r in rows[off: off + n] if r["x"] is not None]
    xs, ys, ws = (np.array([r[k] for r in seg]) for k in ("x", "y", "w"))
    jump = max(np.abs(np.diff(xs)).max(), np.abs(np.diff(ys)).max()) if len(seg) > 1 else 0
    print(f'{sg["i"]:2d} {sg["text"][:26]:26s} x {xs.min():5.0f}-{xs.max():5.0f}  y {ys.min():5.0f}-{ys.max():5.0f}  w {ws.min():4.0f}-{ws.max():4.0f}  '
          f'biggest frame-to-frame move {jump:4.1f} px  min pixels {min(r["n"] for r in seg)}')
    off += n
