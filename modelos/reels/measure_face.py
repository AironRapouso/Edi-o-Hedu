"""Where are his eyes at the first and last frame of every cut segment?

The glasses have a saturated blue-violet frame, easy to find by colour: its centre is the eye line.
Used by hf/build.py to place each shot so the eyes land on the same spot (clean jump cuts, and the last
frame of the short matches the first one for the loop).

Run from REELS_3/edit:  python -X utf8 measure_face.py   ->  face.json + verify/face_check.jpg
"""
import json
import subprocess
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

HERE = Path(__file__).parent
SEGS = json.load(open(HERE / "segments.json", encoding="utf8"))
FPS = 30
tmp = HERE / "verify" / "_f.png"
out, tiles = [], []
for sg in SEGS:
    n = sg["f1"] - sg["f0"]
    row = {"i": sg["i"], "out": sg["out"], "text": sg["text"]}
    for key, fidx in (("first", 0), ("last", n - 1)):
        t = sg["out"] + (fidx + 0.5) / FPS          # the middle of the frame, so the seek cannot round into a neighbour
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.4f}", "-i", str(HERE / "base.mp4"), "-frames:v", "1", str(tmp)], check=True)
        im = Image.open(tmp).convert("RGB")
        a = np.asarray(im).astype(int)
        r, g, b = a[..., 0], a[..., 1], a[..., 2]
        m = (b > r + 30) & (b > g + 22) & (b > 70)
        m[:420] = False
        m[1150:] = False
        m[:, :250] = False
        m[:, 950:] = False
        ys, xs = np.nonzero(m)
        if len(xs) < 150:
            row[key] = None
            continue
        # robust centre: trim the 3 % tails
        x0, x1 = np.percentile(xs, [3, 97])
        y0, y1 = np.percentile(ys, [3, 97])
        row[key] = {"x": round(float((x0 + x1) / 2), 1), "y": round(float((y0 + y1) / 2), 1), "w": round(float(x1 - x0), 1), "n": int(len(xs))}
        d = ImageDraw.Draw(im)
        d.rectangle([x0, y0, x1, y1], outline=(255, 0, 0), width=5)
        tiles.append(im.resize((216, 384)))
    out.append(row)
    print(row["i"], row["text"][:28].ljust(28), row["first"], row["last"])
json.dump(out, open(HERE / "face.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
sheet = Image.new("RGB", (216 * 11, 384 * 2))
for k, t in enumerate(tiles):
    sheet.paste(t, ((k // 2) * 216, (k % 2) * 384))
sheet.save(HERE / "verify" / "face_check.jpg", quality=88)
tmp.unlink()
