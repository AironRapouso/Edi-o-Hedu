"""EP7 — the three 9:16 shorts (Reels / Shorts) in THE Reels look: paper panel with the episode's 3D scene on top,
his face below, navy pill captions on the seam, end card "vídeo completo no canal".

Nothing is re-animated by hand: the 16:9 cue sheet (hf/cues.py + hf/dom_cues.py) is executed again, so the 3D scenes,
their timing and the exercise sheet are exactly the episode's. The vertical page keeps the episode's GSAP timeline
(EP6 output seconds) and drives it through one tweenFromTo per range, so a cut can join two stretches of the episode.

Inputs: ../hf (build.py helpers, cues, scene3d.js, assets), ../words_out.json, ../segments.json,
        ../hf/assets/base.mp4 (picture), ../../EP7_final.mp4 (treated voice + effects, -14 LUFS)
Run: python -X utf8 build_vert.py [c1 c2 ...]   -> cN/index.html, cN/assets/clip.mp4
"""
import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
EDIT = HERE.parent
HF = EDIT / "hf"
FINAL = EDIT.parent / "EP7_final.mp4"
W, H = 1080, 1920
END = 2.6
VFOV = {}                                       # tall scenes that need a wider lens in the short panel
SRC_V = ""

# ---------------------------------------------------------------- run the episode's cue sheet (no page written)
src = (HF / "build.py").read_text(encoding="utf8")
pre = src[: src.index('exec(open(HERE / "cues.py"')]
ns = {"__name__": "ep7cues", "__file__": str(HF / "build.py")}
exec(compile(pre, str(HF / "build.py"), "exec"), ns)
exec(compile((HF / "cues.py").read_text(encoding="utf8"), str(HF / "cues.py"), "exec"), ns)
exec(compile(src[src.index("KEY = {"): src.index("def mode_at(")], "keys", "exec"), ns)
a0 = src.index("def normalize():")
exec(compile(src[a0: src.index("normalize()\ntimeline")], "normalize", "exec"), ns)
ns["normalize"]()
c0 = src.index("def compass(px")
exec(compile(src[c0: src.index('exec(open(HERE / "dom_cues.py"')], "compass", "exec"), ns)
n_els, n_js = len(ns["els"]), len(ns["js"])
exec(compile((HF / "dom_cues.py").read_text(encoding="utf8"), str(HF / "dom_cues.py"), "exec"), ns)
DOM_ELS = {re.search(r'id="([^"]+)"', e).group(1): e for e in ns["els"][n_els:]}
DOM_JS = ns["js"][n_js:]
SCENES, CHIPQ, T, TE, KEY, FIX, _norm = ns["SCENES"], ns["CHIP_Q"], ns["T"], ns["TE"], ns["KEY"], ns["FIX"], ns["_norm"]
WO = json.load(open(EDIT / "words_out.json", encoding="utf8"))
SEGS = json.load(open(EDIT / "segments.json", encoding="utf8"))
BYI = {w["i"]: w for w in WO}
FPS = 30


def fr(t):
    return round(t * FPS) / FPS


def q(t):
    return f"{fr(t):.4f}"


def rng(i0, i1, pre=0.14, post=0.4):
    a, b = BYI[i0]["start"] - pre, BYI[i1]["end"] + post
    prv, nxt = BYI.get(i0 - 1), BYI.get(i1 + 1)
    if prv and prv["seg"] == BYI[i0]["seg"] or prv and BYI[i0]["start"] - prv["end"] < 0.5:
        a = max(a, prv["end"] + 0.06)
    if nxt:
        b = min(b, nxt["start"] - 0.06)
    return [fr(max(0.0, a)), fr(b)]


CUTS = {
    # 1 = chamamento: the episode's main question + its closing idea (posted together with the long video)
    "c1": dict(name="mais_escolas_tecnicas", ranges=[rng(49, 69), rng(2147, 2185)], seam=712,
               title=["SÓ MAIS", "ESCOLAS TÉCNICAS", '<b class="hl">RESOLVE?</b>']),
    "c2": dict(name="ia_nao_resolve_sozinha", ranges=[rng(1129, 1183)], seam=712,
               title=["A IA RESOLVE", "A EDUCAÇÃO", '<b class="hl">SOZINHA?</b>']),
    "c3": dict(name="10_mil_matriculados", ranges=[rng(1277, 1328)], seam=712,
               title=["10 MIL", "MATRÍCULAS:", '<b class="hl">QUANTOS APRENDERAM?</b>']),
}


def build(cid):
    C = CUTS[cid]
    R = C["ranges"]
    SEAM = C["seam"]
    PH = H - SEAM
    offs, o = [], 0.0
    for a, b in R:
        offs.append(o)
        o += b - a
    CL = fr(o)                                           # clip length (vertical seconds), then the end card
    TOT = CL + END

    def vt(t):                                           # episode seconds -> vertical seconds (None if outside)
        for (a, b), of in zip(R, offs):
            if a - 1e-6 <= t <= b + 1e-6:
                return of + t - a
        return None

    def span(s, e):                                      # episode window -> list of vertical windows
        out = []
        for (a, b), of in zip(R, offs):
            x, y = max(s, a), min(e, b)
            if y - x > 0.05:
                out.append((of + x - a, of + y - a))
        return out

    els, js = [], []

    def clip(cid_, s, e, inner, z=5, cls=""):
        els.append(f'<div id="{cid_}" class="clip {cls}" data-start="{q(s)}" data-duration="{(round(e * FPS) - round(s * FPS)) / FPS:.4f}" '
                   f'data-track-index="{3 + len(els) % 6}" style="z-index:{z}">{inner}</div>')

    # ---- which panel content covers which vertical time: 3D scenes, chips, the exercise sheet
    cover = []                                           # (vs, ve, kind, ref)
    for sc in SCENES:
        for vs, ve in span(sc["t0"], sc["t1"]):
            cover.append([vs, ve, "scene", sc["id"]])
    chips = []
    for a_, k_ in CHIPQ:
        cid_, t0, t1, lines = a_[0], a_[1], a_[2], a_[3]
        for sc in SCENES:                                # a chip never starts under a scene that is still on
            if sc["t0"] < t0 < sc["t1"]:
                t0 = sc["t1"] + 0.05
        lines = [(x, max(tt, t0 + 0.02)) for x, tt in lines]
        nxt = [sc["t0"] for sc in SCENES if sc["t0"] > t0 + 0.3]
        t1 = min([t1] + [n - 0.05 for n in nxt])
        if t1 - t0 < 0.3:
            continue
        for vs, ve in span(t0, t1):
            cover.append([vs, ve, "chip", cid_])
            chips.append((cid_, vs, ve, lines, k_.get("strike")))
    ex = None
    if "exs" in DOM_ELS:
        m = re.search(r'data-start="([\d.]+)" data-duration="([\d.]+)"', DOM_ELS["exs"])
        es, ed = float(m.group(1)), float(m.group(2))
        for vs, ve in span(es, es + ed):
            cover.append([vs, ve, "sheet", "exs"])
            ex = (vs, ve)
    cover.sort()
    for k in range(len(cover) - 1):                      # short holes: the earlier item stays until the next one
        if 0 < cover[k + 1][0] - cover[k][1] < 0.9:
            cover[k][1] = cover[k + 1][0]
        cover[k][1] = min(cover[k][1], cover[k + 1][0])
    holes, t = [], 0.0
    for vs, ve, _, _ in cover:
        if vs - t > 0.05:
            holes.append((t, vs))
        t = max(t, ve)
    if CL - t > 0.05:
        holes.append((t, CL))
    ext = {c[3]: c for c in cover}

    # ---- 3D scenes in the panel (episode time; scene3d maps the seek time)
    scenes = []
    for sc in SCENES:
        if span(sc["t0"], sc["t1"]):
            s2 = dict(sc)
            c = ext.get(sc["id"])
            if c:                                        # a stretched hole: keep rendering the scene a bit longer
                k = max(j for j in range(len(R)) if offs[j] <= c[1] - 1e-6)
                s2["t1"] = max(sc["t1"], R[k][0] + c[1] - offs[k] + 0.04)
            if sc["id"] in VFOV:
                s2["fov"] = VFOV[sc["id"]]
            scenes.append(s2)
    asp = W / SEAM
    fov_full = math.degrees(2 * math.atan((1920 / 1080) / asp * math.tan(math.radians(15))))
    fov_full = max(30.0, fov_full)

    # ---- chips -> big navy lines on the paper
    for k, (ccid, vs, ve, lines, strike) in enumerate(chips):
        ve = ext.get(ccid, [0, ve])[1]
        rows = "".join(f'<div id="v{ccid}-{j}" class="vl">{txt}</div>' for j, (txt, _) in enumerate(lines))
        clip(f"v{ccid}", vs, ve, f'<div class="vchip">{rows}</div>', z=3)
        for j, (_, tt) in enumerate(lines):
            js.append(f'vt.fromTo("#v{ccid}-{j}",{{opacity:0,y:40,scale:.92}},{{opacity:1,y:0,scale:1,duration:.32,ease:"back.out(1.8)"}},{q(max(vs, vt(tt) or vs))});')
        if strike:
            j, tt = strike
            js.append(f'vt.fromTo("#v{ccid}-{j} .sk",{{backgroundSize:"0% 12px"}},{{backgroundSize:"100% 12px",duration:.5,ease:"power1.inOut"}},{q(vt(tt) or vs)});')

    # ---- holes -> the cut's title on the paper
    for k, (hs, he) in enumerate(holes):
        rows = "".join(f'<div class="vl">{x}</div>' for x in C["title"])
        clip(f"hole{k}", hs, he, f'<div class="vchip title">{rows}</div>', z=3)
        js.append(f'vt.fromTo("#hole{k} .vchip",{{opacity:0,scale:.94}},{{opacity:1,scale:1,duration:.3,ease:"back.out(1.6)"}},{q(hs)});')

    # ---- hook: the cut's title covers the panel for the first 1.7 s, then wipes up to reveal the scene
    rows = "".join(f'<div class="vl">{x}</div>' for x in C["title"])
    clip("hook0", 0, 2.0, f'<div class="vhook" style="height:{SEAM}px"><div class="vchip title" style="height:{SEAM}px">{rows}</div></div>', z=7)
    js.append('vt.fromTo("#hook0 .vchip",{scale:.9},{scale:1,duration:.35,ease:"back.out(1.9)"},0.0);')
    js.append('vt.to("#hook0 .vhook",{yPercent:-105,duration:.32,ease:"power3.in"},1.62);')

    # ---- the exercise sheet (episode DOM + episode tweens), scaled into the tall panel
    if ex:
        inner = re.sub(r'^<div id="exs"[^>]*>', "", DOM_ELS["exs"])[: -len("</div>")]
        clip("exs", ex[0], ex[1], f'<div class="exwrap">{inner}</div>', z=3)

    # ---- data source (c4)
    if C.get("source"):
        ch = next(s for s in SCENES if s["id"] == "chart")
        for vs, ve in span(ch["t0"] + 0.3, ch["t1"]):
            clip("vsrc", vs, ve, f'<div class="vsrc">{SRC_V}</div>', z=8)

    # ---- captions on the seam (word by word)
    words = []
    for w in WO:
        v = vt(w["start"])
        if v is None or v > CL - 0.05:
            continue
        words.append(dict(w, text=FIX.get(w["text"], w["text"]), vs=v, ve=min(CL, v + w["end"] - w["start"])))
    chunks, cur = [], []
    for k, w in enumerate(words):
        if w["text"] == "%" and cur:
            cur[-1]["text"] += "%"
            continue
        cur.append(w)
        nx = words[k + 1] if k + 1 < len(words) else None
        chars = sum(len(x["text"]) + 1 for x in cur)
        if nx is None or w["text"][-1:] in ".?!," or len(cur) >= 3 or chars >= 17 or nx["vs"] - w["ve"] > 0.3:
            chunks.append(cur)
            cur = []
    for k, c in enumerate(chunks):
        s = max(0.0, c[0]["vs"] - 0.05)
        e = chunks[k + 1][0]["vs"] - 0.05 if k + 1 < len(chunks) else min(CL, c[-1]["ve"] + 0.6)
        e = min(e, c[-1]["ve"] + 0.7)
        if e - s < 0.1:
            continue
        spans = []
        for j, w in enumerate(c):
            tx = w["text"].upper().rstrip(",.:;!")
            g = " g" if _norm(w["text"]) in {_norm(x) for x in KEY} else ""
            spans.append(f'<span class="w{g}" id="cw{k}_{j}">{tx}</span>')
        clip(f"cap{k}", s, e, f'<div class="pill mono">{" ".join(spans)}</div>', z=9, cls="cap")
        js.append(f'vt.fromTo("#cap{k} .pill",{{opacity:.55,scale:.9,y:6}},{{opacity:1,scale:1,y:0,duration:.12,ease:"back.out(2.2)"}},{q(s)});')
        for j, w in enumerate(c):
            js.append(f'vt.set("#cw{k}_{j}",{{opacity:1}},{q(max(s, w["vs"] - 0.02))});')

    # ---- face: punch-in per sentence (1.0 / 1.08) around the eyes
    FS = 1.25 if PH > 1000 else 1.0
    fx, fy = 1000 * FS, 430 * FS
    vl, vtp = 540 - fx, PH * 0.42 - fy
    vtp = min(0.0, max(PH - 1080 * FS, vtp))
    alt, prev = 0, ""
    for sg in SEGS:
        if sg["kind"] != "src":
            continue
        v = vt(sg["out"] + 0.001)
        if v is None:
            continue
        if not prev or prev[-1:] in ".?!:,":
            alt ^= 1
        prev = sg["text"].strip()
        js.append(f'vt.set("#zoom",{{scale:{1.08 if alt else 1.0}}},{q(max(0, v - 0.001))});')

    # ---- end card
    logo = (f'<div class="logo" style="gap:30px">{ns["compass"](150)}<div class="logo-t">'
            '<div style="font-size:74px;line-height:.95">A NOVA</div><div style="font-size:74px;line-height:.95;color:#5CA2EE">ORDEM</div>'
            '<div style="font-size:42px;font-weight:400">EDUCACIONAL</div></div></div>')
    clip("endc", CL, TOT, f'<div class="endv"><div class="grid"></div>{logo}<div id="endt" class="bebas e1">VÍDEO COMPLETO</div>'
                          '<div id="endt2" class="bebas e1">NO <span class="g">CANAL</span></div><div id="endu" class="rule"></div></div>', z=30)
    js.append(f'vt.fromTo("#endc .endv",{{opacity:0}},{{opacity:1,duration:.25,ease:"power2.out"}},{q(CL)});')
    js.append(f'vt.fromTo("#endc .compass",{{rotation:-120,scale:.5}},{{rotation:0,scale:1,duration:.8,ease:"expo.out"}},{q(CL)});')
    js.append(f'vt.fromTo("#endt",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.4,ease:"power3.out"}},{q(CL + 0.25)});')
    js.append(f'vt.fromTo("#endt2",{{opacity:0,y:30}},{{opacity:1,y:0,duration:.4,ease:"power3.out"}},{q(CL + 0.4)});')
    js.append(f'vt.fromTo("#endu",{{scaleX:0}},{{scaleX:1,duration:.5,ease:"power2.inOut"}},{q(CL + 0.6)});')

    # ---- project folder
    out = HERE / cid
    (out / "assets").mkdir(parents=True, exist_ok=True)
    for sub in ("fonts", "three"):
        if not (out / "assets" / sub).exists():
            shutil.copytree(HF / "assets" / sub, out / "assets" / sub)
    shutil.copy(HF / "assets" / "gsap.min.js", out / "assets" / "gsap.min.js")
    shutil.copy(EDIT.parent.parent / "EP5" / "edit" / "hf_vert" / "c1" / "assets" / "sting.wav", out / "assets" / "sting.wav")
    s3 = (HF / "scene3d.js").read_text(encoding="utf8")
    for a_, b_ in [("const W = 1920, H = 1080, PANEL_X = EP.panelX;", "const W = EP.W, H = EP.H, PANEL_X = 0;"),
                   ("const aspect = full ? W / H : (W - PANEL_X) / H;", "const aspect = W / H;"),
                   ("new THREE.PerspectiveCamera(spec.fov ?? 30,", "new THREE.PerspectiveCamera(spec.fov ?? (full ? EP.fovFull : EP.fovSide),"),
                   ("const vx = s.full ? 0 : PANEL_X, vw = s.full ? W : W - PANEL_X;", "const vx = 0, vw = W;"),
                   ('e.detail && typeof e.detail.time === "number" ? e.detail.time : tl.time();',
                    'e.detail && typeof e.detail.time === "number" ? EP.map(e.detail.time) : tl.time();')]:
        assert a_ in s3, a_
        s3 = s3.replace(a_, b_)
    (out / "scene3d.js").write_text(s3, encoding="utf8")

    css = (HF / "style.css").read_text(encoding="utf8")
    css = re.sub(r"html, body \{[^}]*\}", "", css)
    css += (HERE / "vertical.css").read_text(encoding="utf8")
    EPD = {"scenes": scenes, "panelX": 0, "W": W, "H": SEAM, "fovFull": round(fov_full, 2), "fovSide": 27.5 if SEAM < 900 else 30, "R": R, "offs": offs}
    drive = "\n".join(f"vt.add(tl.tweenFromTo({a:.4f},{b:.4f},{{ease:'none',duration:{b - a:.4f}}}),{of:.4f});" for (a, b), of in zip(R, offs))
    html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width={W}, height={H}" />
<title>EP7 vertical {cid}</title>
<style>
{css}
#panel {{ height: {SEAM}px; }}
#gl {{ height: {SEAM}px; }}
#face {{ top: {SEAM}px; height: {PH}px; }}
#vid {{ left: {vl:.1f}px; top: {vtp:.1f}px; width: {1920 * FS:.0f}px; height: {1080 * FS:.0f}px; }}
#zoom {{ transform-origin: 540px {PH * 0.42:.0f}px; }}
.cap .pill {{ top: {SEAM - 38}px; }}
.vchip {{ height: {SEAM}px; }}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{q(TOT)}" data-fps="30" data-width="{W}" data-height="{H}">
  <div id="face"><div id="zoom" data-layout-allow-overflow>
    <video id="vid" src="assets/clip.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{q(CL)}" data-track-index="0"></video>
  </div><div class="fshade"></div></div>
  <div id="panel"><div class="dots"></div><div class="brand mono">{ns["compass"](30)}A NOVA ORDEM EDUCACIONAL</div></div>
  <canvas id="gl" width="{W}" height="{SEAM}"></canvas>
  {chr(10).join(els)}
  <audio id="sting" src="assets/sting.wav" data-start="{q(CL)}" data-duration="{q(END)}" data-track-index="9" data-volume="1.2"></audio>
</div>
<script src="assets/gsap.min.js"></script>
<script>
window.__timelines = window.__timelines || {{}};
window.__hf = window.__hf || {{}};
window.__hf.buildReady = window.__hf.buildReady || {{}};
window.__hf.buildReady.scene3d = new Promise((resolve) => {{ window.__scene3dReady = resolve; }});
const tl = gsap.timeline({{ paused: true }});
window.tl = tl;
window.EP = {json.dumps(EPD, ensure_ascii=False)};
window.EP.map = (v) => {{ const R = window.EP.R, O = window.EP.offs; let k = 0; for (let i = 0; i < O.length; i++) if (v >= O[i]) k = i;
  return Math.min(R[k][1], R[k][0] + v - O[k]); }};
{chr(10).join(DOM_JS)}
const vt = gsap.timeline({{ paused: true }});
{drive}
{chr(10).join(js)}
vt.to({{}}, {{ duration: 0.001 }}, {q(TOT - 0.001)});
window.__timelines["main"] = vt;
</script>
<script type="importmap">{{"imports": {{"three": "./assets/three/three.module.js", "three/addons/": "./assets/three/addons/"}}}}</script>
<script type="module" src="scene3d.js"></script>
</body>
</html>
"""
    (out / "index.html").write_text(html, encoding="utf8")
    # ---- the clip: picture from the cut (no overlays), sound from the finished episode mix
    if "--noclip" not in sys.argv:
        parts = []
        for k, (a, b) in enumerate(R):
            p = HERE / f"_{cid}_p{k}.mp4"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.4f}", "-t", f"{b - a:.4f}", "-i", str(HF / "assets" / "base.mp4"),
                            "-ss", f"{a:.4f}", "-t", f"{b - a:.4f}", "-i", str(FINAL), "-map", "0:v", "-map", "1:a",
                            "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-g", "30", "-pix_fmt", "yuv420p", "-r", "30",
                            "-c:a", "pcm_s16le", "-ar", "48000", str(p)], check=True)
            parts.append(p)
        ins = sum([["-i", str(p)] for p in parts], [])
        n = len(parts)
        fc = "".join(f"[{i}:v][{i}:a]" for i in range(n)) + f"concat=n={n}:v=1:a=1[v][a]"
        subprocess.run(["ffmpeg", "-v", "error", "-y", *ins, "-filter_complex", fc, "-map", "[v]", "-map", "[a]",
                        "-c:v", "libx264", "-preset", "medium", "-crf", "15", "-g", "30", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "256k", str(out / "assets" / "clip.mp4")], check=True)
        for p in parts:
            p.unlink()
    print(f"{cid}: {CL:.1f}s (+{END}s card), ranges {R}, {len(scenes)} scenes, {len(chips)} chips, {len(holes)} title holes "
          f"{[(round(a, 1), round(b, 1)) for a, b in holes]}, sheet={ex is not None}, fovFull={fov_full:.1f}")


if __name__ == "__main__":
    for c in [a for a in sys.argv[1:] if not a.startswith("--")] or list(CUTS):
        build(c)
