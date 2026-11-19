"""Measure rendered frames (snapshots or frames of the final video): where the glasses (eye line) ended up,
how wide the caption is and where it sits. Used to verify the framing rules of the editing script on real pixels.

Usage (from REELS_3/edit):  python -X utf8 measure_render.py <png> [<png> ...]
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

for name in sys.argv[1:]:
    a = np.asarray(Image.open(name).convert("RGB")).astype(int)
    H, W = a.shape[:2]
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    out = [Path(name).name.ljust(26)]
    # glasses: saturated blue-violet rim, looked for between the top band and the caption
    m = (b > r + 30) & (b > g + 22) & (b > 70)
    m[: int(H * 0.235)] = False
    m[int(H * 0.56):] = False
    ys, xs = np.nonzero(m)
    if len(xs) > 150:
        x0, x1 = np.percentile(xs, [3, 97])
        ey = float(np.median(ys)) + 0.123 * (x1 - x0)        # same definition as track_face.py: top rim + 0.123 x width
        out.append(f"eyes ({(x0 + x1) / 2:6.1f}, {ey:6.1f}) glasses {x1 - x0:5.1f} px")
    else:
        out.append("eyes: not found".ljust(40))
    # caption: pure white / gold fill with a black outline, between 55 % and 67 % of the height
    band = a[int(H * 0.55): int(H * 0.67)]
    rr, gg, bb = band[..., 0], band[..., 1], band[..., 2]
    white = (rr > 248) & (gg > 248) & (bb > 248)
    gold = (abs(rr - 244) < 8) & (abs(gg - 176) < 8) & (abs(bb - 74) < 10)
    black = (rr < 6) & (gg < 6) & (bb < 6)
    txt = white | gold
    cols = np.nonzero(txt.sum(0) > 2)[0]
    rows = np.nonzero(txt.sum(1) > 2)[0]
    brows = np.nonzero(black.sum(1) > 20)[0]
    bcols = np.nonzero(black.sum(0) > 6)[0]
    if len(cols) and len(brows):
        y0, y1 = brows[0] + int(H * 0.55), brows[-1] + int(H * 0.55)
        out.append(f"caption x {bcols[0]:4d}-{bcols[-1]:4d} (width {bcols[-1] - bcols[0]:4d}), y {y0}-{y1} = {y0 / H * 100:.1f}-{y1 / H * 100:.1f} %")
    print("  ".join(out))
