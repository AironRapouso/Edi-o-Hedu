"""SHORT 03 cover (1080x1920 JPG) — session 2: the cover style of REELS 1-2 again (the user rejected the first
version of this short, made by the written script, as a whole).

Host cut out of a direct-gaze frame over the blue panel, big navy headline + one gold highlight, two small icons.
Headline = the script's "Título" (Seu chefe já fez essa conta) + the script's cover text (VOCÊ X FERRAMENTA) in the
gold box, so it reads literally: "seu chefe já fez essa conta: você x ferramenta".

Lessons kept (memory thumbnail-standard): fill the whole frame, big centred face with direct gaze and closed mouth,
nothing in front of it, every text inside y 240-1680 (the 3:4 crop of the profile grid). rembg swallows the dark
wall panel behind his head, so the hair contour is traced against the dark area and everything above it is removed.

Run: python -X utf8 make_cover.py   (then snapshot hf/ with HyperFrames, see project.md)
"""
import re
import shutil
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from rembg import new_session, remove
from scipy import ndimage as ndi

HERE = Path(__file__).parent
EDIT = HERE.parent
FRAME = HERE / "cand" / "f_13.35.png"                         # the pause after "pela metade do preço.": direct gaze, mouth closed
ASSETS = HERE / "hf" / "assets"
(ASSETS / "fonts").mkdir(parents=True, exist_ok=True)
for f in (EDIT / "hf" / "assets" / "fonts").iterdir():
    shutil.copy(f, ASSETS / "fonts" / f.name)
shutil.copy(EDIT / "hf" / "assets" / "gsap.min.js", ASSETS / "gsap.min.js")

# ---------------------------------------------------------------- cutout
src = Image.open(FRAME).convert("RGB")
raw = remove(src, session=new_session("u2net_human_seg"))
al = np.asarray(raw.getchannel("A")) > 128
rgb = np.asarray(src).astype(float)
luma = rgb @ [0.299, 0.587, 0.114]
sm = ndi.uniform_filter(luma, 5)
mean = ndi.uniform_filter(luma, 7)
std = np.sqrt(np.maximum(ndi.uniform_filter(luma ** 2, 7) - mean ** 2, 0))
hairy = (sm > 64) | (std > 13)
dark = sm < 52
top = np.full(1080, np.nan)
for x in range(1080):
    d = ndi.uniform_filter1d(dark[250:900, x].astype(float), 15)
    di = np.nonzero(d > 0.9)[0]
    if not len(di):
        continue                                             # no dark wall above the head in this column
    y0 = 250 + di[0] + 8                                     # inside the dark wall
    run = ndi.uniform_filter1d(hairy[y0:900, x].astype(float), 9)
    idx = np.nonzero(run > 0.75)[0]
    if len(idx):
        top[x] = y0 + idx[0] - 4
cols = np.nonzero(~np.isnan(top))[0]
m = al.copy()
if len(cols) > 40:
    # the wall is one contiguous block of columns: keep the longest run
    runs = np.split(cols, np.nonzero(np.diff(cols) > 3)[0] + 1)
    wall = max(runs, key=len)
    x0, x1 = wall[0], wall[-1] + 1
    seg = top[x0:x1]
    xs = np.arange(len(seg))
    ok = ~np.isnan(seg)
    seg = np.interp(xs, xs[ok], seg[ok])
    seg = ndi.gaussian_filter1d(ndi.median_filter(seg, 31, mode="nearest"), 4, mode="nearest")
    for x in range(x0, x1):
        m[: int(seg[x - x0]) + 2, x] = False
    print(f"dark wall columns {x0}-{x1}: hair contour traced")
yy, xx = np.ogrid[-8:9, -8:9]
opened = ndi.binary_opening(m, structure=xx * xx + yy * yy <= 64)   # drops thin spikes at the wall edges
m[:720] = opened[:720]
lab, n = ndi.label(m)
m = lab == (1 + int(np.argmax(ndi.sum(m, lab, range(1, n + 1)))))
m = ndi.binary_fill_holes(m)
a = Image.fromarray((m * 255).astype("uint8")).filter(ImageFilter.GaussianBlur(2.2))
cut = src.copy()
cut.putalpha(a)
cut.save(ASSETS / "host_cut.png")
for name, color in (("mask_check.jpg", (255, 0, 255)), ("mask_check_paper.jpg", (244, 242, 236))):
    bg = Image.new("RGB", cut.size, color)
    bg.paste(cut, (0, 0), cut)
    bg.crop((200, 380, 1000, 1200)).save(HERE / name, quality=90)

rows = np.nonzero(m[:, 300:800].any(1))[0]
htop = int(rows[0])
band = np.nonzero(m[htop + 150: htop + 300].any(0))[0]
cx, hw = (band[0] + band[-1]) / 2, band[-1] - band[0]
SC = max(1.11, 500 / hw)                                       # head ~500 px wide, shoulders past both canvas edges
SC = max(SC, 1080 / (2 * min(cx, 1080 - cx)) + 0.01)
left, topo = round(540 - cx * SC), round(903 - htop * SC)
print(f"head top {htop}, centre x {cx:.0f}, width {hw} -> scale {SC:.3f}, left {left}, top {topo}")

# ---------------------------------------------------------------- page
page = (EDIT / "hf" / "index.html").read_text(encoding="utf8")
compass = re.search(r'<svg class="compass" width="34".*?</svg>', page, re.S).group(0).replace('width="34" height="34"', 'width="56" height="56"')
html = f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8" />
<meta name="viewport" content="width=1080, height=1920" />
<title>REELS 3 — capa</title>
<style>
@font-face {{ font-family: "Inter"; src: url("assets/fonts/Inter-700-latin.woff2") format("woff2"); font-weight: 700; font-display: block; }}
@font-face {{ font-family: "Bebas Neue"; src: url("assets/fonts/bebas-neue-latin-400-normal.woff2") format("woff2"); font-weight: 400; font-display: block; }}
@font-face {{ font-family: "Mono"; src: url("assets/fonts/consolab.ttf") format("truetype"); font-weight: 700; font-display: block; }}
* {{ margin: 0; padding: 0; box-sizing: border-box; }}
html, body {{ width: 1080px; height: 1920px; overflow: hidden; background: #F4F2EC; }}
#root {{ position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #F4F2EC; color: #010B25;
  background-image: radial-gradient(rgba(1,11,37,.085) 1.6px, transparent 1.7px); background-size: 36px 36px; }}
.abs {{ position: absolute; }}
.bebas {{ font-family: "Bebas Neue", sans-serif; font-weight: 400; line-height: 1; letter-spacing: .015em; }}
.mono {{ font-family: "Mono", monospace; font-weight: 700; }}
#wm {{ left: 0; right: 0; top: 132px; display: flex; align-items: center; justify-content: center; gap: 16px; font-size: 27px; letter-spacing: .26em; color: rgba(1,11,37,.66); }}
.l {{ left: 0; right: 0; text-align: center; white-space: nowrap; }}
#l3 {{ left: 0; right: 0; top: 722px; text-align: center; z-index: 5; }}
#l3 span {{ display: inline-block; font-size: 134px; background: #F4B04A; padding: 18px 42px 2px; border-radius: 28px; transform: rotate(-2deg); box-shadow: 0 16px 36px rgba(1,11,37,.25); white-space: nowrap; }}
#l3 i {{ font-style: normal; color: #FFFFFF; padding: 0 .06em; }}
#panel {{ left: 0; right: 0; top: 1150px; bottom: 0; border-radius: 80px 80px 0 0; background: linear-gradient(180deg, #0A63F2 0%, #0457E7 30%, #031954 100%); }}
#clip {{ left: 0; right: 0; top: 0; bottom: 0; overflow: hidden; z-index: 3; }}
#host {{ position: absolute; left: {left}px; top: {topo}px; width: {round(1080 * SC)}px; filter: drop-shadow(0 10px 28px rgba(1,11,37,.35)); }}
.chip {{ left: 884px; top: 958px; width: 140px; height: 140px; border-radius: 34px; background: #010B25; color: #F6F6F8; font-size: 84px; display: flex; align-items: center;
  justify-content: center; padding-top: 8px; transform: rotate(9deg); z-index: 4; box-shadow: 0 0 0 9px rgba(4,87,231,.18), 0 18px 40px rgba(4,87,231,.4); }}
.chip b {{ color: #F4B04A; font-weight: 400; }}
#mini {{ left: 62px; top: 940px; width: 196px; height: 226px; border-radius: 22px; background: #fff; transform: rotate(-8deg); z-index: 2; overflow: hidden;
  border: 2px solid rgba(1,11,37,.07); box-shadow: 0 20px 44px rgba(1,11,37,.18); }}
#mini .hd {{ height: 44px; background: #0B2266; }}
#mini .gr {{ position: absolute; left: 0; right: 0; top: 44px; bottom: 0; display: grid; grid-template-columns: 34px 1fr 1fr; grid-template-rows: repeat(4, 1fr); }}
#mini .gr div {{ border-right: 2px solid #D9DEE9; border-bottom: 2px solid #D9DEE9; display: flex; align-items: center; padding: 0 9px; }}
#mini .gr div:nth-child(3n+1) {{ background: #EEF1F6; }}
#mini u {{ display: block; height: 13px; border-radius: 7px; background: #C3CADA; width: 78%; }}
#mini u.g {{ background: #F4B04A; height: 17px; width: 92%; }}
</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="1" data-fps="30" data-width="1080" data-height="1920">
  <div id="wm" class="abs mono">{compass}<span>A NOVA ORDEM EDUCACIONAL</span></div>
  <div class="abs l bebas" style="top:262px;font-size:158px">SEU CHEFE JÁ FEZ</div>
  <div class="abs l bebas" style="top:414px;font-size:248px">ESSA CONTA</div>
  <div class="abs bebas" id="l3"><span>VOCÊ <i>X</i> FERRAMENTA</span></div>
  <div class="abs" id="panel"></div>
  <div class="abs" id="mini"><div class="hd"></div><div class="gr">
    <div></div><div><u></u></div><div><u style="width:60%"></u></div>
    <div></div><div><u style="width:64%"></u></div><div><u class="g"></u></div>
    <div></div><div><u style="width:84%"></u></div><div><u style="width:48%"></u></div>
    <div></div><div><u style="width:56%"></u></div><div><u style="width:72%"></u></div>
  </div></div>
  <div class="abs chip bebas">R<b>$</b></div>
  <div class="abs" id="clip"><img id="host" src="assets/host_cut.png" alt=""></div>
</div>
<script src="assets/gsap.min.js"></script>
<script>
window.__timelines = window.__timelines || {{}};
const tl = gsap.timeline({{ paused: true }});
tl.to("#root", {{ opacity: 1, duration: 1 }}, 0);
window.__timelines["main"] = tl;
</script>
</body></html>"""
(HERE / "hf" / "index.html").write_text(html, encoding="utf8")
print("hf/index.html written")
