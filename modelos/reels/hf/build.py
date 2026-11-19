"""REELS 3 = SHORT 03 "Planilha do chefe" (Dr. Hélio), 9:16, 30 fps — session 2: back to the split-panel look.

The user rejected the first version (full-frame talking head by the written script) with "tá ruim, volta pra pegada
antiga e aprimora tudo". This is the REELS 1-2 pattern again (paper panel with 3D on top / face below, navy pill
captions on the seam, full-screen takeovers, comment CTA), with these upgrades:
  - captions light up word by word (the chunk shows dimmed, each word turns on when he says it)
  - the face panel follows his eye line: every jump cut lands on the same spot, punch-ins are centred on the eyes,
    and 60 % of his slow drift is taken out (track.json, one row per frame)
  - one 3D world for the whole story (the same gold "VOCÊ" pawn, the robot, the spreadsheet) - scene3d.js

This script only writes index.html + reel.json: the clips (captions, CTA card) and the numbers the two static scripts
read (window.REEL). timeline.js = DOM tweens + face framing; scene3d.js = 3D scenes. Every time is anchored to a
SOURCE word index, so a re-cut never misplaces a graphic.

Run: python -X utf8 build.py   ->  index.html, reel.json
"""
import json
import math
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter1d

HERE = Path(__file__).parent
EDIT = HERE.parent
FPS = 30
W, H, SEAM = 1080, 1920, 712
PH = H - SEAM                                   # height of the face panel
WORDS = json.load(open(EDIT / "words_out.json", encoding="utf8"))
SEGS = json.load(open(EDIT / "segments.json", encoding="utf8"))
TRACK = json.load(open(EDIT / "track.json", encoding="utf8"))
NF = sum(s["f1"] - s["f0"] for s in SEGS)
TOTAL = NF / FPS
BY = {w["i"]: w for w in WORDS}
assert len(TRACK) == NF, "track.json is from another cut: run track_face.py"


def fr(t):
    return round(t * FPS) / FPS


def q(t):
    return f"{fr(t):.4f}"


def S(i):
    return fr(BY[i]["start"])


def E(i):
    return fr(BY[i]["end"])


def seg(k):
    return fr(SEGS[k]["out"])


# ---------------------------------------------------------------- scene windows (output seconds)
T = {
    "fs1": seg(1),     # "Pode ter sido sobre o quanto você custa por mês,"      -> FULL SCREEN (the cost sheet, the pawn, the coins)
    "sc3": seg(2),     # "e quanto custa uma ferramenta / que faz as suas entregas / pela metade do preço."  -> split (robot, parcels, 1/2)
    "sc4": seg(5),     # "Não é maldade,"                                        -> split (the little devil, crossed out)
    "fs2": seg(6),     # "é planilha, e planilha não tem sentimento."            -> FULL SCREEN (the sheet, the heart turns into 0)
    "sc5": seg(8),     # "Então me diz, o que você entrega que não cabe nessa conta?" -> split (the gift that does not fit + comment CTA)
    "total": fr(TOTAL),
    "S": {str(w["i"]): S(w["i"]) for w in WORDS},
    "E": {str(w["i"]): E(w["i"]) for w in WORDS},
    "seg": [seg(k) for k in range(len(SEGS))],
}
assert SEGS[1]["text"].startswith("Pode") and SEGS[2]["text"].startswith("e quanto") and SEGS[5]["text"].startswith("Não é") \
    and SEGS[6]["text"].startswith("é planilha") and SEGS[8]["text"].startswith("Então") and len(SEGS) == 11, "segments moved: fix the scene windows"

# ---------------------------------------------------------------- captions: (first word, last word, text override, gold word)
# The script says "conta" where the automatic transcription heard "cota": the caption follows the script.
CHUNKS = [
    (0, 2, None, "REUNIÃO"), (3, 5, None, None), (6, 9, None, "CHAMADO?"), (10, 12, None, None), (13, 15, None, None),
    (16, 17, None, "CUSTA"), (18, 19, None, "MÊS"), (20, 22, None, None), (23, 24, None, "FERRAMENTA"), (25, 26, None, None),
    (27, 29, None, "ENTREGAS"), (30, 31, None, "METADE"), (32, 33, None, "PREÇO"), (34, 36, None, "MALDADE"), (37, 38, None, "PLANILHA"),
    (39, 40, None, None), (41, 43, None, "SENTIMENTO"), (44, 46, None, None), (47, 50, None, "ENTREGA"), (51, 53, None, None),
    (54, 55, "NESSA CONTA?", "CONTA?"),
]
assert sum(b - a + 1 for a, b, _, _ in CHUNKS) == len(WORDS)
cap_html, caps = [], []
for k, (a, b, text, gold) in enumerate(CHUNKS):
    s = fr(max(0.0, BY[a]["start"] - 0.04))
    e = fr(BY[CHUNKS[k + 1][0]]["start"] - 0.04) if k + 1 < len(CHUNKS) else fr(TOTAL)
    e = min(e, fr(BY[b]["end"] + 0.9))
    words = (text or " ".join(BY[i]["text"] for i in range(a, b + 1))).upper().split()
    assert len(words) == b - a + 1, (k, words)
    parts, lit = [], []
    for j, wd in enumerate(words):
        wd = wd.rstrip(",.:!")
        cls = "w g" if gold and wd == gold else "w"
        parts.append(f'<span class="{cls}" id="w{a + j}">{wd}</span>')
        lit.append({"id": f"w{a + j}", "t": s if j == 0 else S(a + j)})          # each word lights up when he says it
    if gold:
        assert any('class="w g"' in p for p in parts), (k, gold)
    cap_html.append(f'<div id="cap{k}" class="clip cap" data-start="{q(s)}" data-duration="{e - s:.4f}" data-track-index="8">'
                    f'<div class="pill mono">{" ".join(parts)}</div></div>')
    caps.append({"id": f"cap{k}", "s": s, "w": lit})

# ---------------------------------------------------------------- CTA typing
TYPED = "EU ENTREGO…"
typed_html = "".join(f'<span class="ch" id="ty{k}">{c if c != " " else "&nbsp;"}</span>' for k, c in enumerate(TYPED))
t0, t1 = S(51), E(55) - 0.12
typed = [fr(t0 + (t1 - t0) * k / len(TYPED)) for k in range(len(TYPED))]

# ---------------------------------------------------------------- face panel: one transform per frame
# The blue rim of his glasses is tracked on every frame (track.json). Each cut segment is placed from its first frames, so
# every jump cut lands his eyes on (XA, YA) with the same face size; inside a segment FOLLOW of his slow drift is taken out.
# In the half second after the last word the framing eases back to exactly the framing of frame 0 (the Reel loops).
XA, YA = 548.0, 400.0                           # where his eye line sits inside the face panel (panel px)
G0 = 396.0                                      # width of his glasses at zoom 1.0 (px); REELS 2 was about 376
FOLLOW = 0.6
ZOOM = {0: 1.06, 1: 1.0, 2: 1.0, 3: 1.06, 4: 1.13, 5: 1.0, 6: 1.0, 7: 1.0, 8: 1.09, 9: 1.0, 10: 1.06}   # hard punch-ins on the jump cuts


def column(key):
    v = np.array([np.nan if r[key] is None else r[key] for r in TRACK], float)
    bad = np.isnan(v)
    v[bad] = np.interp(np.nonzero(bad)[0], np.nonzero(~bad)[0], v[~bad])
    return v


TX, TY, TW = column("x"), column("y"), column("w")
face, shots, off = [], [], 0
t_last = E(55)
for k, sg in enumerate(SEGS):
    n = sg["f1"] - sg["f0"]
    xs = gaussian_filter1d(TX[off: off + n], 4, mode="nearest")
    ys = gaussian_filter1d(TY[off: off + n], 4, mode="nearest")
    ws = gaussian_filter1d(TW[off: off + n], 6, mode="nearest")
    xr, yr, wr = float(xs[:3].mean()), float(ys[:3].mean()), float(np.median(ws[:6]))
    s0 = max(G0 * ZOOM[k] / wr, 1.004)
    for j in range(n):
        kf, ks = FOLLOW, 0.0
        if k == len(SEGS) - 1:
            u = min(1.0, max(0.0, ((off + j) / FPS - t_last) / (TOTAL - 1 / FPS - t_last)))
            u = u * u * (3 - 2 * u)
            kf, ks = FOLLOW + (1 - FOLLOW) * u, u
        sc = max(s0 * (wr / ws[j]) ** ks, 1.004)
        ex, ey = xr + kf * (xs[j] - xr), yr + kf * (ys[j] - yr)
        tx = min(0.0, max(W * (1 - sc), XA - sc * ex))
        ty = min(0.0, max(PH - H * sc, YA - sc * ey))
        face.append([round(tx, 1), round(ty, 1), round(sc, 4)])
    shots.append({"seg": k, "t": seg(k), "zoom": ZOOM[k], "scale": round(s0, 4), "ref": [round(xr, 1), round(yr, 1), round(wr, 1)]})
    off += n

REEL = {"T": T, "caps": caps, "typed": typed, "total": fr(TOTAL), "face": face, "shots": shots, "anchor": [XA, YA], "seam": SEAM}


def compass(px, cls="compass"):
    R, r, ri = 50, 30, 8.5
    polys = []

    def point(a_deg, rad, c1, c2):
        a = math.radians(a_deg)
        tip = (rad * math.cos(a), rad * math.sin(a))
        l = (ri * math.cos(a - math.pi / 4), ri * math.sin(a - math.pi / 4))
        rr = (ri * math.cos(a + math.pi / 4), ri * math.sin(a + math.pi / 4))
        f = lambda p: f"{p[0]:.2f},{p[1]:.2f}"
        polys.append(f'<polygon points="0,0 {f(tip)} {f(l)}" fill="{c1}"/>')
        polys.append(f'<polygon points="0,0 {f(tip)} {f(rr)}" fill="{c2}"/>')

    for a in (45, 135, 225, 315):
        point(a - 90, r, "#5CA2EE", "#0457E7")
    polys.append('<circle r="21" fill="none" stroke="#1892F0" stroke-width="2.2"/>')
    for a in (0, 90, 180, 270):
        point(a - 90, R, "#F6F6F8", "#8E97AA")
    polys.append('<circle r="2.6" fill="#010B25"/>')
    return f'<svg class="{cls}" width="{px}" height="{px}" viewBox="-55 -55 110 110">' + "".join(polys) + "</svg>"


CSS = """
@font-face { font-family: "Inter"; src: url("assets/fonts/Inter-400-latin.woff2") format("woff2"); font-weight: 400; font-display: block; }
@font-face { font-family: "Inter"; src: url("assets/fonts/inter-latin-600-normal.woff2") format("woff2"); font-weight: 600; font-display: block; }
@font-face { font-family: "Inter"; src: url("assets/fonts/Inter-700-latin.woff2") format("woff2"); font-weight: 700; font-display: block; }
@font-face { font-family: "Bebas Neue"; src: url("assets/fonts/bebas-neue-latin-400-normal.woff2") format("woff2"); font-weight: 400; font-display: block; }
@font-face { font-family: "Playfair Display"; src: url("assets/fonts/playfair-display-latin-700-normal.woff2") format("woff2"); font-weight: 700; font-display: block; }
@font-face { font-family: "Mono"; src: url("assets/fonts/consolab.ttf") format("truetype"); font-weight: 700; font-display: block; }

* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { width: 1080px; height: 1920px; overflow: hidden; background: #F4F2EC; }
body { font-family: "Inter", sans-serif; color: #010B25; }
#root { position: relative; width: 1080px; height: 1920px; overflow: hidden; background: #F4F2EC; }
#paper { position: absolute; inset: 0; background-image: radial-gradient(rgba(1,11,37,.085) 1.6px, transparent 1.7px); background-size: 36px 36px; }
#glowp { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px;
  background: radial-gradient(ellipse 62% 30% at 50% 21%, rgba(255,255,255,.7) 0%, rgba(255,255,255,0) 100%); }

#cam { position: absolute; left: 0; top: 712px; width: 1080px; height: 1208px; overflow: hidden; border-radius: 40px 40px 0 0; z-index: 1; background: #111; }
#zoom { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; transform-origin: 0 0; }
#vid { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; display: block; }
#vig { position: absolute; inset: 0; background: radial-gradient(ellipse 78% 62% at 50% 36%, rgba(0,0,0,0) 58%, rgba(0,0,0,.26) 100%); }
#cover { position: absolute; left: 0; top: 700px; width: 1080px; height: 1220px; background: #F4F2EC; z-index: 2; transform-origin: 50% 0%;
  background-image: radial-gradient(rgba(1,11,37,.085) 1.6px, transparent 1.7px); background-size: 36px 36px; background-position: 0 -16px; }
#gl { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; z-index: 3; pointer-events: none; display: block; }

.clip { position: absolute; left: 0; top: 0; width: 1080px; height: 1920px; pointer-events: none; }
.scene { z-index: 4; }
.bebas { font-family: "Bebas Neue", sans-serif; font-weight: 400; letter-spacing: .02em; line-height: 1; }
.mono { font-family: "Mono", monospace; font-weight: 700; }
.play { font-family: "Playfair Display", serif; font-weight: 700; }
.card { position: absolute; background: #FFFFFF; border-radius: 30px; border: 2px solid rgba(1,11,37,.07);
  box-shadow: 0 22px 54px rgba(1,11,37,.13), 0 3px 8px rgba(1,11,37,.06); }

#wm { position: absolute; left: 0; right: 0; top: 64px; z-index: 5; display: flex; align-items: center; justify-content: center; gap: 12px;
  font-size: 19px; letter-spacing: .26em; color: rgba(1,11,37,.5); }

/* captions: navy pill on the seam, each word lights up as he says it */
.cap { z-index: 9; }
.pill { position: absolute; left: 50%; top: 712px; transform: translate(-50%, -50%); white-space: nowrap; background: #010B25; color: #F6F6F8;
  font-size: 44px; letter-spacing: .13em; padding: 15px 30px 13px 34px; border-radius: 16px; box-shadow: 0 8px 22px rgba(1,11,37,.35); }
.pill .w { display: inline-block; opacity: .34; }
.pill .g { color: #F4B04A; }

/* CTA card (right half of the top panel; the 3D sheet with the gift lives on the left) */
#cta { left: 508px; top: 118px; width: 536px; height: 530px; padding: 22px 26px 0; overflow: hidden; }
#cta .who { display: flex; align-items: center; gap: 14px; height: 86px; border-bottom: 3px solid #ECEAE3; padding-bottom: 14px; }
#cta .av { width: 68px; height: 68px; border-radius: 50%; background: #010B25; display: flex; align-items: center; justify-content: center; flex: none; }
#cta .nm { font-size: 25px; font-weight: 700; line-height: 1.12; }
#fol { margin-left: auto; position: relative; width: 152px; height: 58px; flex: none; }
#fol div { position: absolute; inset: 0; border-radius: 14px; display: flex; align-items: center; justify-content: center; font-size: 26px; font-weight: 700; }
#fol .a { background: #0457E7; color: #fff; }
#fol .b { background: #ECEAE3; color: #010B25; }
#cta .ask { display: flex; align-items: center; gap: 12px; margin-top: 20px; font-size: 22px; letter-spacing: .22em; color: #0457E7; }
#cta .qq { font-size: 51px; line-height: 1.1; margin-top: 12px; }
#cta .qq b { background: linear-gradient(transparent 58%, #F9D48B 58%); font-weight: 700; }
#field { position: absolute; left: 26px; right: 26px; bottom: 26px; height: 92px; border-radius: 22px; border: 4px solid #D9D6CD; background: #FAF9F6;
  display: flex; align-items: center; padding: 0 20px; }
#field .ph { position: absolute; left: 22px; font-size: 27px; color: rgba(1,11,37,.38); }
#field .tx { font-family: "Bebas Neue"; font-size: 58px; padding-top: 8px; letter-spacing: .04em; white-space: nowrap; }
#field .ch { display: none; }
#field .cur { display: inline-block; width: 5px; height: 50px; background: #0457E7; margin-left: 6px; vertical-align: -6px; }
#send { margin-left: auto; width: 60px; height: 60px; border-radius: 17px; background: #0457E7; display: flex; align-items: center; justify-content: center; flex: none; }
"""

f0 = face[0]
HTML = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width={W}, height={H}" />
<title>REELS 3 — Planilha do chefe</title>
<style>{CSS}</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{q(TOTAL)}" data-fps="30" data-width="{W}" data-height="{H}">
  <div id="paper"></div>
  <div id="glowp"></div>
  <div id="cam"><div id="zoom" data-layout-allow-overflow style="transform: translate({f0[0]}px, {f0[1]}px) scale({f0[2]})">
    <video id="vid" src="assets/base.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{q(TOTAL)}" data-track-index="0"></video>
  </div><div id="vig"></div></div>
  <div id="cover"></div>
  <canvas id="gl" width="{W}" height="{H}"></canvas>
  <div id="wm" class="mono">{compass(34)}<span>A NOVA ORDEM EDUCACIONAL</span></div>

  <!-- CTA: "Então me diz: o que você entrega que não cabe nessa conta?" -->
  <div id="sc6" class="clip scene" data-start="{q(T["sc5"])}" data-duration="{q(TOTAL - T["sc5"])}" data-track-index="2">
    <div class="card" id="cta">
      <div class="who"><div class="av">{compass(52)}</div>
        <div class="nm">A Nova Ordem<br>Educacional</div>
        <div id="fol"><div class="b">Seguindo</div><div class="a" id="fola">Seguir</div></div></div>
      <div class="ask mono"><svg width="30" height="30" viewBox="0 0 34 34"><path d="M4 6h26v18H15l-8 7v-7H4Z" fill="#0457E7"/></svg>COMENTE AQUI</div>
      <div class="qq play">O que você <b>entrega</b> que não cabe na planilha?</div>
      <div id="field"><span class="ph" id="ph">Adicione um comentário…</span><span class="tx">{typed_html}<span class="cur" id="cur"></span></span>
        <div id="send"><svg width="32" height="32" viewBox="0 0 34 34"><path d="M17 28V7M7 16 17 6l10 10" fill="none" stroke="#fff" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg></div></div>
    </div>
  </div>

  {chr(10).join(cap_html)}
</div>
<script src="assets/gsap.min.js"></script>
<script>window.REEL = {json.dumps(REEL)};</script>
<script src="timeline.js"></script>
<script>window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = window.tl;</script>
<script type="importmap">{{"imports": {{"three": "./assets/three/three.module.js", "three/addons/": "./assets/three/addons/"}}}}</script>
<script type="module" src="scene3d.js"></script>
</body>
</html>
"""
(HERE / "index.html").write_text(HTML, encoding="utf8")
json.dump({k: v for k, v in REEL.items() if k != "face"} | {"face_first": face[0], "face_last": face[-1]},
          open(HERE / "reel.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(f"index.html: {TOTAL:.2f}s ({NF} frames), {len(caps)} captions")
print("scenes:", {k: v for k, v in T.items() if k in ("fs1", "sc3", "sc4", "fs2", "sc5", "total")})
off = 0
for k, sg in enumerate(SEGS):
    n = sg["f1"] - sg["f0"]
    a, b = face[off], face[off + n - 1]
    eye = lambda fr_, i: (fr_[0] + fr_[2] * TX[i], fr_[1] + fr_[2] * TY[i], fr_[2] * TW[i])
    ea, eb = eye(a, off), eye(b, off + n - 1)
    print(f'  seg {k:2d} zoom {ZOOM[k]:.2f} scale {a[2]:.3f}->{b[2]:.3f}  eyes first ({ea[0]:5.0f},{ea[1]:5.0f}) w {ea[2]:4.0f} | last ({eb[0]:5.0f},{eb[1]:5.0f}) w {eb[2]:4.0f}   {sg["text"][:34]}')
    off += n
