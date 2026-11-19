"""EP7 — "A educação profissional do futuro" (YouTube 16:9, 30 fps). Generates index.html + sfx.json.

The Reels dynamics brought to the landscape format:
  talk  : full-frame face, punch-ins on the jump cuts, word-by-word pill captions
  side  : the face slides left and a paper panel with a 3D scene comes in from the right
  full  : a paper cover wipes over everything and a 3D scene takes the whole frame
  pip   : the face shrinks to a rounded box bottom-right and a paper sheet takes the screen (the exercise)
Every cue is anchored to a SOURCE word index (words_out.json); a cue on a word that was cut raises an error.
Run: python -X utf8 build.py
"""
import json
import math
import re
import unicodedata
from pathlib import Path

HERE = Path(__file__).parent
EDIT = HERE.parent
FPS = 30
W, H = 1920, 1080
PANEL_X = 1020                      # side panel: x 1020..1920
FACE = (960, 449)                  # his face in the staged frame (zoom origin)
CAM_SIDE_X = -430
PIP = dict(x=1223, y=669, s=0.34)
SEGS = json.load(open(EDIT / "segments.json", encoding="utf8"))
WO = json.load(open(EDIT / "words_out.json", encoding="utf8"))
TOTAL = sum(s["frames"] for s in SEGS) / FPS
BYI = {w["i"]: w for w in WO}
ALLW = [w for w in json.load(open(EDIT / "transcripts/EP7_refined.json", encoding="utf8"))["words"]]


def fr(t):
    return round(t * FPS) / FPS


def q(t):
    return f"{fr(t):.4f}"


def T(i, dt=0.0):
    if i not in BYI:
        raise ValueError(f"word {i} '{ALLW[i]['text']}' is not in the cut")
    return BYI[i]["start"] + dt


def TE(i, dt=0.0):
    if i not in BYI:
        raise ValueError(f"word {i} '{ALLW[i]['text']}' is not in the cut")
    return BYI[i]["end"] + dt


def _norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9%]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


def K(prefix, after):
    p = _norm(prefix)
    for i in range(after, len(ALLW)):
        if i in BYI and _norm(ALLW[i]["text"]).startswith(p):
            return i
    raise ValueError(f"'{prefix}' not found after {after}")


def gap(label):
    g = next(x for x in SEGS if x["kind"] == "gap" and x["label"] == label)
    return g["out"], g["out"] + g["frames"] / FPS


els, js, SFX, SCENES, MODES = [], [], [], [], []      # MODES: (t0, t1, mode)


def sfx(t, kind, peak=-20, pan=0.0, why=""):
    SFX.append({"t": round(t, 3), "k": kind, "peak": peak, "pan": pan, "why": why})


def clip(cid, s, e, inner, cls="", style="", z=5):
    assert e > s, (cid, s, e)
    els.append(f'<div id="{cid}" class="clip {cls}" data-start="{q(s)}" data-duration="{(round(e * FPS) - round(s * FPS)) / FPS:.4f}" '
               f'data-track-index="{3 + len(els) % 6}" style="z-index:{z};{style}">{inner}</div>')


def tw(sel, frm, to, t, d=0.4, ease="power3.out", ir=True):
    js.append(f'tl.fromTo({json.dumps(sel)},{frm},{{...{to},duration:{d},ease:"{ease}"{"" if ir else ",immediateRender:false"}}},{q(t)});')


def setp(sel, props, t):
    js.append(f'tl.set({json.dumps(sel)},{props},{q(t)});')


# ---------------------------------------------------------------- scene helpers (3D, declarative)
SFX_FOR = {"pawn": ("pop", -19), "pawnX": ("thud", -18), "robot": ("servo", -21), "plate": ("pop_hi", -21), "text": ("thud", -15),
           "numeral": ("thud", -14), "coins": ("coins", -19), "calendar": ("paper", -21), "parcel": ("box", -18), "badge": ("buzz", -18),
           "nosign": ("clang", -15), "doc": ("paper", -20), "bubble": ("bloop", -19), "iceberg": ("rumble", -18), "belt": ("servo", -24),
           "armbot": ("servo", -21), "counter": ("thud", -19), "atm": ("thud", -18), "door": ("thud", -19), "clock": ("pop", -19),
           "alarm": ("pop", -18), "folder": ("paper", -19), "bar": ("zip", -19), "hbar": ("zip", -20), "grid": ("pop", -20),
           "slot": ("thud", -19), "sheet3": ("paper", -19), "star": ("chime", -25), "box": ("pop", -21), "sel": ("tick", -22), "beam": ("scan", -24)}


def it(k, **kw):
    return dict(k=k, **kw)


def scene(sid, mode, t0, t1, items, cam=(0, 3.0, 14), look=(0, 2.2, 0), moves=None, auto_sfx=True, **kw):
    t0, t1 = fr(t0), fr(t1)
    for o in items:                                   # nothing may appear before the cover/panel has arrived
        if o.get("t") is not None:
            o["t"] = max(o["t"], t0 + (0.2 if mode == "full" else 0.12))
            if auto_sfx and not o.get("quiet"):
                kind, pk = SFX_FOR.get(o["k"], ("pop", -21))
                if o.get("drop") and kind in ("pop", "pop_hi"):
                    kind = "clack"
                pan = 0.45 if mode == "side" else max(-0.6, min(0.6, (o.get("p") or [0])[0] / 8))
                sfx(o["t"] + (0.3 if o.get("drop") else 0.0), kind, pk + o.get("louder", 0), pan, f"{sid}:{o['k']}")
    k = 1.17 if mode == "side" else 1.0              # the side panel is narrow: pull every side camera back a little
    zoom_out = lambda c, l: [l[j] + (c[j] - l[j]) * k for j in range(3)]
    cam = zoom_out(cam, look)
    mv, lk = [], list(look)
    for m in (moves or []):
        lk = list(m[3]) if len(m) > 3 and m[3] else lk
        mv.append([m[0], m[1], zoom_out(m[2], lk)] + list(m[3:]))
    if not mv:                                       # no camera move written: a slow push-in, so the frame is never still
        push = [look[j] + (cam[j] - look[j]) * 0.93 for j in range(3)]
        mv = [[t0, max(0.5, t1 - t0), push, None, "sine.inOut"]]
    firsts = [o["t"] for o in items if o.get("t") is not None]
    if firsts and min(firsts) > t0 + 0.9:
        print(f"  WARNING scene {sid}: nothing appears for {min(firsts) - t0:.1f}s")
    SCENES.append(dict(id=sid, mode=mode, t0=t0, t1=t1, items=items, cam=list(cam), look=list(look), camMoves=mv, **kw))
    MODES.append((t0, t1, mode))


def side(sid, t0, t1, items, **kw):
    scene(sid, "side", t0, t1, items, **kw)


def full(sid, t0, t1, items, **kw):
    scene(sid, "full", t0, t1, items, cam=kw.pop("cam", (0, 3.4, 19)), look=kw.pop("look", (0, 3.0, 0)), **kw)


def pip(t0, t1):
    MODES.append((fr(t0), fr(t1), "pip"))


def G(txt):
    return f'<b class="g">{txt}</b>'


CHIPS = []


CHIP_Q = []


def chip(*a, **k):
    CHIP_Q.append((a, k))                           # built after all cues, when every scene window is known


def _chip(cid, t0, t1, lines, red=None, side_="left", strike=None):
    """big Bebas lines beside his head (talk mode); each line = (html, t)"""
    for a_, b_, m_ in MODES:                      # never start under a panel / cover that is still on screen
        if a_ < t0 < b_:
            t0 = b_ + 0.05
    lines = [(x, max(t, t0 + 0.02)) for x, t in lines]
    nxt = [a for a, b, m in MODES if a > t0 + 0.3]
    if nxt and min(nxt) - 0.12 < t1:
        t1 = min(nxt) - 0.12                         # never over the next panel / cover
    rows = "".join(f'<div id="{cid}-{k}" class="chipl">{txt}</div>' for k, (txt, _) in enumerate(lines))
    pos = "left:96px" if side_ == "left" else "right:96px;align-items:flex-end"
    clip(cid, t0, t1, f'<div class="in"><div class="chipshade {side_}"></div><div class="chipst" style="{pos}">{rows}</div></div>', z=6)
    tw(f"#{cid} > .in", "{opacity:0}", "{opacity:1}", t0, 0.2, "power2.out")
    js.append(f'tl.to("#{cid} > .in",{{opacity:0,duration:.25,ease:"power2.in"}},{q(t1 - 0.25)});')
    for k, (_, t) in enumerate(lines):
        tw(f"#{cid}-{k}", "{opacity:0,x:-60,scale:.9}", "{opacity:1,x:0,scale:1}", t, 0.32, "back.out(1.8)")
        sfx(t, "whoosh_s" if k == 0 else "pop_hi", -21, -0.5, f"{cid} line {k}")
    if strike:
        k, t = strike
        js.append(f'tl.fromTo("#{cid}-{k} .sk",{{backgroundSize:"0% 10px"}},{{backgroundSize:"100% 10px",duration:.5,ease:"power1.inOut"}},{q(t)});')
        sfx(t, "strike", -17, -0.5, f"{cid} strike")
    CHIPS.append((t0, t1))


ZOOMS = []                                            # (t0, t1, zoom) emphasis windows (talk mode)


def emph(t0, t1, z=1.2):
    ZOOMS.append((t0, t1, z))


exec(open(HERE / "cues.py", encoding="utf8").read())
for _a, _k in CHIP_Q:
    _chip(*_a, **_k)


# ---------------------------------------------------------------- captions (word by word, pill on the bottom)
KEY = {"educação", "profissional", "escolas", "técnicas", "diretrizes", "competências", "competência", "oportunidade", "oportunidades", "futuro",
       "qualidade", "aprendizagem", "professor", "professores", "estudante", "estudantes", "trabalho", "tecnologia", "inteligência", "artificial",
       "cooperação", "diploma", "diplomas", "resultados", "investimento", "realidade", "organizar", "organização", "suficiente", "presencial", "digital",
       "combinar", "ilusão", "centro", "dignidade", "recomeço", "possibilidade", "desenvolvimento", "humano", "emprego", "renda", "produtividade"}
FIX = {"1926,": "2026,", "arquivos": "artigos", "nascer": "nasceu", "desverecer": "desmerecer", "apostas.": "opostas.", "mediada": "medida", "Sinaepte.": "SINAEPT.",
       "-vindos": "VINDOS", "-me": "ME", "-se": "SE", "Helio": "HÉLIO", "%": "%"}


FIXI = {K("sobre", 1500): "sob", K("sabe", 1700): "sabem"}


def mode_at(t):
    m = "talk"
    for a, b, mm in MODES:
        if a - 0.1 <= t < b:
            m = mm
    return m


chunks, cur = [], []
for k, w in enumerate(WO):
    txt = FIXI.get(w["i"], FIX.get(w["text"], w["text"]))
    if w["text"] == "%" and cur:
        cur[-1] = dict(cur[-1], text=cur[-1]["text"] + "%")
        continue
    nxt = WO[k + 1] if k + 1 < len(WO) else None
    cur.append(dict(w, text=txt))
    chars = sum(len(x["text"]) + 1 for x in cur)
    end_here = (nxt is None or nxt["seg"] != w["seg"] and nxt["start"] - w["end"] > 0.25 or w["text"][-1:] in ".?!,"
                or len(cur) >= 4 or chars >= 20 or (nxt and nxt["label"] != w["label"]))
    if end_here:
        chunks.append(cur)
        cur = []
if cur:
    chunks.append(cur)
LTS = [(T(92, -0.1), TE(100, 0.3)), (T(2209, -0.1), TE(2219, 0.4))]      # lower thirds: captions move right meanwhile


def cap_left(t):
    if any(a - 0.2 <= t <= b for a, b in LTS):
        return 1300
    return {"side": (PANEL_X + CAM_SIDE_X * 0 + 0) / 2, "pip": 610}.get(mode_at(t), 960)


def build_captions():
    for k, c in enumerate(chunks):
        s = fr(max(0.0, c[0]["start"] - 0.05))
        e = fr(chunks[k + 1][0]["start"] - 0.05) if k + 1 < len(chunks) else fr(c[-1]["end"] + 0.6)
        e = min(e, fr(c[-1]["end"] + 0.7))
        if e - s < 0.1:
            continue
        if any(a <= s < b for a, b in [gap("VINHETA"), gap("TELA_FINAL")]):
            continue
        spans = []
        for j, w in enumerate(c):
            t = w["text"].upper().rstrip(",.:;!")
            g = " g" if _norm(w["text"]) in {_norm(x) for x in KEY} else ""
            spans.append(f'<span class="w{g}" id="cw{k}_{j}">{t}</span>')
        left = cap_left(s)
        clip(f"cap{k}", s, e, f'<div class="pill mono" style="left:{left}px">{" ".join(spans)}</div>', cls="cap", z=9)
        tw(f"#cap{k} .pill", "{opacity:.55,scale:.9,y:6}", "{opacity:1,scale:1,y:0}", s, 0.12, "back.out(2.2)")
        for j, w in enumerate(c):
            setp(f"#cw{k}_{j}", "{opacity:1}", max(s, w["start"] - 0.02))


# ---------------------------------------------------------------- camera / panel / cover / pip state machine
def state(mode):
    return {"talk": dict(cx=0, cy=0, cs=1, px=980, pb=0, br=0), "side": dict(cx=CAM_SIDE_X, cy=0, cs=1, px=0, pb=0, br=0),
            "pip": dict(cx=PIP["x"], cy=PIP["y"], cs=PIP["s"], px=980, pb=1, br=64), "full": None}[mode]


def build_modes():
    win = sorted(MODES)
    for a, b in zip(win, win[1:]):
        assert a[1] <= b[0] + 1e-6, f"overlapping windows {a} {b}"
    timeline = []                                       # merged: list of (t0, t1, mode) with talk filled in
    t = 0.0
    for a, b, m in win:
        if a - t > 1e-6:
            timeline.append((t, a, "talk"))
        timeline.append((a, b, m))
        t = b
    if TOTAL - t > 1e-6:
        timeline.append((t, TOTAL, "talk"))
    # initial state
    first = timeline[0][2]
    st0 = state(first) or state("talk")
    setp("#cam", f"{{x:{st0['cx']},y:{st0['cy']},scale:{st0['cs']},borderRadius:{st0['br']}}}", 0)
    setp("#panel", f"{{x:{st0['px']}}}", 0)
    setp("#pipbg", f"{{opacity:{st0['pb']}}}", 0)
    setp("#cover", "{scaleY:%d}" % (1 if first == "full" else 0), 0)
    last_vis = st0
    for k, (a, b, m) in enumerate(timeline):
        if k == 0:
            continue
        prev = timeline[k - 1][2]
        if m == "full":
            js.append(f'tl.fromTo("#cover",{{scaleY:0,transformOrigin:"50% 0%"}},{{scaleY:1,duration:.26,ease:"power3.inOut",immediateRender:false}},{q(a - 0.06)});')
            sfx(a - 0.06, "whoosh_down", -16, 0, "cover in")
            sfx(a - 0.42, "riser", -19, 0, "riser into full")
            sfx(a + 0.2, "thud", -17, 0, "cover lands")
            continue
        new = state(m)
        if prev == "full":
            # under the cover: jump straight to the next state, then the cover wipes up
            setp("#cam", f"{{x:{new['cx']},y:{new['cy']},scale:{new['cs']},borderRadius:{new['br']}}}", a - 0.08)
            setp("#panel", f"{{x:{new['px']}}}", a - 0.08)
            setp("#pipbg", f"{{opacity:{new['pb']}}}", a - 0.08)
            js.append(f'tl.fromTo("#cover",{{scaleY:1,transformOrigin:"50% 100%"}},{{scaleY:0,duration:.28,ease:"power3.inOut",immediateRender:false}},{q(a - 0.02)});')
            sfx(a - 0.02, "whoosh_up", -18, 0, "cover out")
        else:
            o = last_vis
            d = 0.5
            js.append(f'tl.fromTo("#cam",{{x:{o["cx"]},y:{o["cy"]},scale:{o["cs"]},borderRadius:{o["br"]}}},{{x:{new["cx"]},y:{new["cy"]},scale:{new["cs"]},borderRadius:{new["br"]},duration:{d},ease:"power3.inOut",immediateRender:false}},{q(a - 0.25)});')
            if o["px"] != new["px"]:
                js.append(f'tl.fromTo("#panel",{{x:{o["px"]}}},{{x:{new["px"]},duration:{d},ease:"power3.inOut",immediateRender:false}},{q(a - 0.25)});')
                sfx(a - 0.25, "whoosh", -19, 0.5 if new["px"] == 0 else -0.2, f"panel {'in' if new['px'] == 0 else 'out'}")
            if o["pb"] != new["pb"]:
                js.append(f'tl.fromTo("#pipbg",{{opacity:{o["pb"]}}},{{opacity:{new["pb"]},duration:.35,ease:"power2.inOut",immediateRender:false}},{q(a - 0.25)});')
                sfx(a - 0.25, "whoosh", -18, 0.3, "pip")
        last_vis = new
    return timeline


def build_zoom(timeline):
    """punch-in per sentence in talk mode (alternating 1.0 / 1.1), emphasis windows bigger, 1.0 elsewhere"""
    def mode(t):
        return next((m for a, b, m in timeline if a <= t < b), "talk")
    alt, prev_end = 0, ""
    ev = []
    for s in SEGS:
        if s["kind"] != "src":
            continue
        t = s["out"]
        if prev_end[-1:] in ".?!:," or not prev_end:
            alt ^= 1
        prev_end = s["text"].strip()
        z = 1.1 if alt else 1.0
        zz = next((c for a, b, c in ZOOMS if a - 0.05 <= t < b), None)
        if zz:
            z = zz + (0.04 if alt else 0)
        ev.append((t, z if mode(t + 0.01) == "talk" else 1.0))
    for a, b, c in ZOOMS:
        if mode(a + 0.01) == "talk":
            ev.append((a, c))
    for a, b, m in timeline:                          # never zoomed inside side / pip / full windows
        if m != "talk":
            ev.append((a - 0.25, 1.0))
        else:
            z_in = next((z for tt, z in sorted(ev) if a - 1e-3 <= tt < a + 0.3), None)
            if z_in is None:
                last = [z for tt, z in sorted(ev) if tt <= a + 0.3 and mode(tt + 0.01) == "talk"]
                ev.append((a + 0.25, last[-1] if last else 1.0))
    for t, z in sorted(ev):
        setp("#zoom", f"{{scale:{z}}}", max(0, t))


def normalize():
    """adjacent windows may overlap by their padding: the earlier one ends where the next begins"""
    MODES.sort()
    for k in range(len(MODES) - 1):
        a0, a1, am = MODES[k]
        b0, b1, bm = MODES[k + 1]
        if a1 > b0:
            MODES[k] = (a0, b0, am)
            for sc in SCENES:
                if abs(sc["t0"] - a0) < 1e-6 and abs(sc["t1"] - a1) < 1e-6:
                    sc["t1"] = b0


normalize()
timeline = build_modes()
build_zoom(timeline)
build_captions()

# ---------------------------------------------------------------- compass / logo (brand)


def compass(px, cls=""):
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
    polys.insert(8, '<circle r="21" fill="none" stroke="#1892F0" stroke-width="2.2"/>')
    for a in (0, 90, 180, 270):
        point(a - 90, R, "#F6F6F8", "#8E97AA")
    polys.append('<circle r="2.6" fill="#010B25"/>')
    return f'<svg class="compass {cls}" width="{px}" height="{px}" viewBox="-55 -55 110 110">' + "".join(polys) + "</svg>"


exec(open(HERE / "dom_cues.py", encoding="utf8").read())     # lower thirds, vinheta, exercise sheet, CTA cards, end screen

CSS = (HERE / "style.css").read_text(encoding="utf8")
EPDATA = {"scenes": SCENES, "panelX": PANEL_X}
html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width={W}, height={H}" />
<title>A educação profissional do futuro</title>
<style>
{CSS}
#zoom {{ transform-origin: {FACE[0]}px {FACE[1]}px; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{q(TOTAL)}" data-fps="30" data-width="{W}" data-height="{H}">
  <div id="pipbg"></div>
  <div id="cam"><div id="zoom" data-layout-allow-overflow>
    <video id="base" src="assets/base.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{q(TOTAL)}" data-track-index="0"></video>
  </div><div id="vig"></div></div>
  <div id="panel"><div class="dots"></div></div>
  <div id="cover"><div class="dots"></div></div>
  <canvas id="gl" width="{W}" height="{H}"></canvas>
  {chr(10).join(els)}
</div>
<script src="assets/gsap.min.js"></script>
<script>
window.__timelines = window.__timelines || {{}};
window.__hf = window.__hf || {{}};
window.__hf.buildReady = window.__hf.buildReady || {{}};
window.__hf.buildReady.scene3d = new Promise((resolve) => {{ window.__scene3dReady = resolve; }});
const tl = gsap.timeline({{ paused: true }});
window.tl = tl;
window.EP = {json.dumps(EPDATA, ensure_ascii=False)};
{chr(10).join(js)}
window.__timelines["main"] = tl;
</script>
<script type="importmap">{{"imports": {{"three": "./assets/three/three.module.js", "three/addons/": "./assets/three/addons/"}}}}</script>
<script type="module" src="scene3d.js"></script>
</body>
</html>
"""
(HERE / "index.html").write_text(html, encoding="utf8")
assert '<video id="vin"' in html, "vinheta missing"
json.dump(sorted(SFX, key=lambda e: e["t"]), open(HERE / "sfx.json", "w", encoding="utf8"), ensure_ascii=False, indent=0)
json.dump({"T": {"vin": gap("VINHETA"), "end": gap("TELA_FINAL")}, "total": TOTAL, "modes": timeline}, open(HERE / "reel.json", "w", encoding="utf8"), indent=1)
print(f"index.html: {TOTAL:.2f}s, {len(SCENES)} 3D scenes, {len(els)} DOM clips, {len(js)} tweens, {len(SFX)} sfx, {len(chunks)} caption chunks")
from collections import Counter
print("time per mode:", {m: round(sum(b - a for a, b, mm in timeline if mm == m), 1) for m in ("talk", "side", "full", "pip")})
