"""Generate index.html for REFLEXÃO "Aula invertida com IA em 5 passos"

Every cue is anchored to a SOURCE word index (transcripts/EP7_refined.json) and mapped to the
output timeline through segments.json, so re-cutting never leaves graphics on the wrong words.
A cue on a word that was cut raises an error instead of landing somewhere else.
Run: python -X utf8 build.py  ->  index.html
"""
import json, math, re, subprocess, unicodedata
from pathlib import Path

HERE = Path(__file__).parent
EDIT = HERE.parent
FPS = 30
SEGS = json.load(open(EDIT / "segments.json", encoding="utf8"))
TOTAL = sum(s["frames"] for s in SEGS) / FPS
SRCW = [w for w in json.load(open(EDIT / "transcripts/EP7_refined.json", encoding="utf8"))["words"] if w.get("type", "word") == "word"]


def _norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9%]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


def _out(t_src):
    for sg in SEGS:
        if sg["kind"] == "src" and sg["s"] - 1e-3 <= t_src <= sg["e"] + 1e-3:
            return t_src - sg["s"] + sg["out"]
    return None


def T(i, dt=0.0):
    """output time of the start of source word i"""
    t = _out(SRCW[i]["start"])
    if t is None:
        t = _out(SRCW[i]["start"] + 0.06)
    if t is None:
        raise ValueError(f"word {i} '{SRCW[i]['text']}' is not in the cut")
    return t + dt


def TE(i, dt=0.0):
    t = _out(SRCW[i]["end"]) or _out(SRCW[i]["end"] - 0.06)
    if t is None:
        raise ValueError(f"word {i} '{SRCW[i]['text']}' is not in the cut")
    return t + dt


def K(prefix, after):
    """index of the first source word >= after whose text starts with prefix (accent/case-insensitive)"""
    p = _norm(prefix)
    for i in range(after, len(SRCW)):
        if _norm(SRCW[i]["text"]).startswith(p):
            return i
    raise ValueError(f"'{prefix}' not found after {after}")


def KT(prefix, after, dt=0.0):
    return T(K(prefix, after), dt)


def gap(label):
    g = next(x for x in SEGS if x["kind"] == "gap" and x["label"] == label)
    return g["out"], g["out"] + g["frames"] / FPS


def qd(t):
    return f"{round(t * FPS) / FPS:.4f}"


q = qd
els, js, auds = [], [], []


TRACKS = {}  # track -> [(start, end)]; overlapping clips never share a track


def alloc(pref, s, e):
    pool = [1, 12, 13, 14] if pref == 1 else ([pref] + [k for k in range(3, 9) if k != pref])
    for k in pool:
        if all(e <= a + 0.001 or s >= b - 0.001 for a, b in TRACKS.get(k, [])):
            TRACKS.setdefault(k, []).append((s, e))
            return k
    raise RuntimeError(f"no free track for {s:.2f}-{e:.2f}")


def clip(cid, start, end, inner, cls="", style="", track=3):
    assert end > start, (cid, start, end)
    track = alloc(track, start, end)
    els.append(f'<div id="{cid}" class="clip {cls}" data-start="{q(start)}" data-duration="{(round(end * FPS) - round(start * FPS)) / FPS:.4f}" '
               f'data-track-index="{track}" style="{style}">{inner}</div>')


FROMTOS = {}


def tw(sel, frm, to, t, d=0.5, ease="power3.out"):
    FROMTOS.setdefault(sel, []).append((t, len(js)))
    js.append([sel, frm, to, t, d, ease])


def render_js():
    late = set()
    for lst in FROMTOS.values():
        for _, idx in sorted(lst)[1:]:
            late.add(idx)
    out = []
    for i, x in enumerate(js):
        if isinstance(x, list):
            sel, frm, to, t, d, ease = x
            ir = ",immediateRender:false" if i in late else ""
            x = f'tl.fromTo({json.dumps(sel)},{frm},{{...{to},duration:{d},ease:"{ease}"{ir}}},{q(t)});'
        out.append(x)
    return "\n".join(out)


def appear(sel, t, d=0.45, y=24, x=0):
    tw(sel, f"{{opacity:0,y:{y},x:{x}}}", "{opacity:1,y:0,x:0}", t, d)


def pop(sel, t, d=0.35):
    tw(sel, "{opacity:0,scale:.6}", "{opacity:1,scale:1}", t, d, "back.out(2)")


def vanish(sel, t, d=0.35):
    js.append(f'tl.to({json.dumps(sel)},{{opacity:0,duration:{d},ease:"power2.in"}},{q(t)});')


def life(cid, start, end, d_in=0.4, d_out=0.35):
    tw(f"#{cid} > .in", "{opacity:0}", "{opacity:1}", start, d_in, "power2.out")
    vanish(f"#{cid} > .in", end - d_out, d_out)


def strike(sel, t, d=0.35):
    tw(sel, '{scaleX:0,transformOrigin:"left center"}', "{scaleX:1}", t, d, "power2.inOut")


def count(sel, frm, to, t, d=1.0, suffix=""):
    js.append(f'(function(){{const o={{v:{frm}}};const el=document.querySelector({json.dumps(sel)});'
              f'tl.fromTo(o,{{v:{frm}}},{{v:{to},duration:{d},ease:"power2.out",onUpdate:function(){{'
              f'el.textContent=Math.round(o.v)+{json.dumps(suffix)};}},immediateRender:false}},{q(t)});}})();')


def sfx(name, t, vol, dur=None):
    lens = {"whoosh": 0.8, "tick": 0.09, "pop": 0.18, "bell": 1.1, "sting": 3.2, "mech": 8.0, "strike": 0.3}
    d = dur or lens[name]
    auds.append(f'<audio id="sfx{len(auds)}" src="assets/sfx/{name}.wav" data-start="{q(t)}" '
                f'data-duration="{qd(d)}" data-track-index="{9 + len(auds) % 3}" data-volume="{vol}"></audio>')


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
    ring = '<circle r="21" fill="none" stroke="#1892F0" stroke-width="2.2"/><circle r="25" fill="none" stroke="#0457E7" stroke-width="0.8" opacity=".7"/>'
    polys.insert(8, ring)
    for a in (0, 90, 180, 270):
        point(a - 90, R, "#F6F6F8", "#8E97AA")
    polys.append('<circle r="2.6" fill="#010B25"/>')
    return (f'<svg class="compass {cls}" width="{px}" height="{px}" viewBox="-55 -55 110 110">'
            + "".join(polys) + "</svg>")


def logo(scale=1.0):
    s = scale
    return (f'<div class="logo" style="gap:{int(34*s)}px">{compass(int(190*s))}'
            f'<div class="logo-t"><div style="font-size:{int(92*s)}px;line-height:.95">A NOVA</div>'
            f'<div style="font-size:{int(92*s)}px;line-height:.95;color:var(--ordem)">ORDEM</div>'
            f'<div style="font-size:{int(52*s)}px;font-weight:400;letter-spacing:.02em">EDUCACIONAL</div>'
            f'<div class="pod" style="font-size:{int(22*s)}px">PODCAST <span class="wave">'
            + "".join(f'<i style="height:{int((6+10*abs(math.sin(i*1.7)))*s)}px"></i>' for i in range(14))
            + "</span></div></div></div>")


def words_html(cid, words, cls="w"):
    return "".join(f'<span id="{cid}-w{i}" class="{cls}">{w}</span> ' for i, w in enumerate(words))


def phrase(cid, i0, i1, lines, size=62, hold=0.5):
    """Playfair thesis band synced word by word to source words i0..i1 (one word per source word)"""
    span = lambda w: w[1] if isinstance(w, tuple) else 1
    n = sum(span(w) for l in lines for w in l)
    assert n == i1 - i0 + 1, (cid, n, i1 - i0 + 1)
    s, e = T(i0, -0.15), TE(i1, hold)
    html, k = "", 0
    bottoms = [72 + 78 * (len(lines) - 1 - i) for i in range(len(lines))]
    for li, (ws, b) in enumerate(zip(lines, bottoms)):
        html += f'<div class="phrase play" style="bottom:{b}px;font-size:{size}px">{words_html(f"{cid}l{li}", [w[0] if isinstance(w, tuple) else w for w in ws])}</div>'
    clip(cid, s, e, f'<div class="in"><div class="band"></div>{html}</div>')
    life(cid, s, e, 0.3)
    k = 0
    for li, ws in enumerate(lines):
        for wi, w in enumerate(ws):
            appear(f"#{cid}l{li}-w{wi}", T(i0 + k, -0.05), 0.32, 14)
            k += span(w)


def lower_third(cid, s, e, role):
    clip(cid, s, e, f'<div class="in"><div id="{cid}-p" class="lt">{compass(78)}<div><div class="lt-n">HÉLIO LARANJEIRA</div>'
         f'<div class="lt-r">{role}</div><div id="{cid}-u" class="lt-u gold-bg"></div></div></div></div>')
    life(cid, s, e, 0.2)
    tw(f"#{cid}-p", '{clipPath:"inset(0 100% 0 0)"}', '{clipPath:"inset(0 0% 0 0)"}', s + 0.05, 0.7, "power3.inOut")
    tw(f"#{cid} .compass", "{rotation:-90}", "{rotation:0}", s + 0.05, 0.9)
    strike(f"#{cid}-u", s + 0.5, 0.5)


BROLL_USED = set()


def broll(name, s, e, mstart=0.0, push=1.07):
    assert name not in BROLL_USED, f"B-roll {name} used twice"  # standing rule: never repeat a clip
    BROLL_USED.add(name)
    # never run past the end of the staged clip (it would freeze on its last frame)
    src = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                str(EDIT / "broll" / f"{name}.mp4")], capture_output=True, text=True).stdout)
    avail = min(src, 16.0) - mstart - 0.2
    if e - s > avail:
        print(f"  b-roll {name}: window {e - s:.2f}s capped to {avail:.2f}s")
        e = s + avail
    bid = f"br_{name}"
    tk = alloc(1, s, e)
    els.append(f'<div id="{bid}w" class="brw"><video id="{bid}" class="clip broll" src="assets/broll/{name}.mp4" muted playsinline '
               f'data-start="{q(s)}" data-duration="{qd(e - s)}" data-media-start="{mstart}" data-track-index="{tk}"></video></div>')
    tw(f"#{bid}w", "{scale:1}", f"{{scale:{push}}}", s, e - s, "none")




INTERTITLES = {
    "I1": ("PARTE 1", "AS NOVAS DIRETRIZES"),
    "I2": ("PARTE 2", "UM PAÍS, MUITAS REALIDADES"),
    "I3": ("PARTE 3", "O QUE O TRABALHADOR JÁ SABE"),
    "I4": ("PARTE 4", "A IA E O PROFESSOR"),
    "I5": ("PARTE 5", "O QUE OS NÚMEROS NÃO MOSTRAM"),
    "I6": ("PARTE 6", "IMAGINE ALGO DIFERENTE"),
    "I7": ("PARA FECHAR", "A EDUCAÇÃO PROFISSIONAL DO FUTURO"),
}


def intertitle(label):
    cid = label.lower()
    s, e = gap(label)
    k, title = INTERTITLES[label]
    size = 150 if len(title) <= 24 else 118
    clip(cid, s, e, f'<div class="in full bg-brand center"><div class="grid"></div><div class="divider"><i id="{cid}-l" class="dl"></i>{compass(96)}'
         f'<i id="{cid}-r" class="dl"></i></div><div class="kicker2" style="margin-top:22px">{k}</div>'
         f'<div id="{cid}-t" class="bebas" style="font-size:{size}px;margin-top:6px;max-width:1700px;text-align:center">{title}</div></div>', track=4)
    life(cid, s, e, 0.25, 0.3)
    tw(f"#{cid} .compass", "{rotation:-180,scale:.4}", "{rotation:0,scale:1}", s, 0.9, "expo.out")
    tw(f"#{cid}-l", '{scaleX:0,transformOrigin:"right center"}', "{scaleX:1}", s + 0.2, 0.6)
    tw(f"#{cid}-r", '{scaleX:0,transformOrigin:"left center"}', "{scaleX:1}", s + 0.2, 0.6)
    tw(f"#{cid}-t", "{opacity:0,scale:1.12}", "{opacity:1,scale:1}", s + 0.3, 0.9, "power3.out")
    sfx("whoosh", s - 0.12, 0.5)


def beats(cid, s, e, words, times, gold_last=True, size=230):
    clip(cid, s, e, '<div class="in full dim center">' + "".join(
        f'<div id="{cid}-{i}" class="bebas beat {"gold" if gold_last and i == len(words) - 1 else ""}" style="font-size:{size}px">{w}</div>'
        for i, w in enumerate(words)) + "</div>")
    life(cid, s, e, 0.15)
    for i, t in enumerate(times):
        tw(f"#{cid}-{i}", "{opacity:0,scale:1.25}", "{opacity:1,scale:1}", t, 0.22, "power3.out")
        if i < len(times) - 1:
            js.append(f'tl.set("#{cid}-{i}",{{opacity:0}},{q(times[i+1])});')
        sfx("tick", t, 0.45)


def stack2(cid, s, e, lines, times, size=110):
    """centered lines that stay on screen, one appearing per cue (final question / contrasts)"""
    clip(cid, s, e, '<div class="in full dim center"><div class="stack" style="position:static;gap:26px;align-items:center">'
         + "".join(f'<div id="{cid}-{i}" class="bebas" style="font-size:{size}px;text-align:center;max-width:1700px">{t}</div>' for i, t in enumerate(lines))
         + "</div></div>", track=4)
    life(cid, s, e, 0.3)
    for i, t in enumerate(times):
        appear(f"#{cid}-{i}", t, 0.4)
        sfx("tick", t, 0.4)


def pills(cid, s, e, items, times, label=None, bottom=120, size=None):
    lab = f'<span class="tlab">{label}</span>' if label else ""
    st = f' style="font-size:{size}px;padding:14px 26px"' if size else ""
    clip(cid, s, e, f'<div class="in"><div class="grad-b"></div><div class="row wrap" style="bottom:{bottom}px;gap:20px">{lab}'
         + "".join(f'<span id="{cid}-{i}" class="pill"{st}>{t}</span>' for i, t in enumerate(items)) + "</div></div>", track=4)
    life(cid, s, e, 0.2, 0.2)
    for i, t in enumerate(times):
        pop(f"#{cid}-{i}", t)
        sfx("pop", t, 0.3)


def checks(cid, s, e, items, side="left", title=None):
    """stack of ✓ / ✗ lines; items = [(text, ok, t)]; ✗ lines are the gold accent"""
    pos = "left:110px" if side == "left" else "right:110px;align-items:flex-end"
    grad = "grad-l" if side == "left" else "grad-r"
    head = f'<div class="kicker2">{title}</div>' if title else ""
    rows = "".join(f'<div id="{cid}-{i}" class="chk {"ok" if ok else "no"}"><span class="mk">{"✓" if ok else "✗"}</span>{txt}</div>'
                   for i, (txt, ok, _) in enumerate(items))
    top = 330 if len(items) <= 4 else 260
    clip(cid, s, e, f'<div class="in"><div class="{grad}"></div><div class="stack" style="{pos};top:{top}px;gap:18px">{head}{rows}</div></div>', track=4)
    life(cid, s, e, 0.25)
    for i, (_, ok, t) in enumerate(items):
        appear(f"#{cid}-{i}", t, 0.35, 0, -40 if side == "left" else 40)
        sfx("pop" if ok else "strike", t, 0.3 if ok else 0.4)


def chain(cid, s, e, steps, times, label=None, gold_last=True, size=34):
    """horizontal chain of step boxes joined by arrows (bottom band)"""
    lab = f'<div class="kicker2" style="text-align:center;margin-bottom:18px">{label}</div>' if label else ""
    boxes = ""
    for i, st in enumerate(steps):
        g = " goldb" if gold_last and i == len(steps) - 1 else ""
        boxes += (f'<span id="{cid}-a{i}" class="carr">→</span>' if i else "") + f'<span id="{cid}-{i}" class="cbox{g}" style="font-size:{size}px">{st}</span>'
    clip(cid, s, e, f'<div class="in"><div class="grad-b" style="height:520px"></div><div class="chainw">{lab}<div class="chain">{boxes}</div></div></div>', track=4)
    life(cid, s, e, 0.25)
    for i, t in enumerate(times):
        if i:
            appear(f"#{cid}-a{i}", t - 0.1, 0.25, 0, -20)
        appear(f"#{cid}-{i}", t, 0.35, 20)
        sfx("tick", t, 0.4)


def pair(cid, s, e, a, b, ta, tb, mid="OU", label=None):
    """two boxes side by side (bottom band), the second in gold"""
    lab = f'<div id="{cid}-k" class="kicker2 pairk">{label}</div>' if label else ""
    clip(cid, s, e, f'<div class="in"><div class="grad-b" style="height:520px"></div><div class="pairw">'
         f'<span id="{cid}-0" class="cbox">{a}</span><span id="{cid}-p" class="bebas gold" style="font-size:80px">{mid}</span>'
         f'<span id="{cid}-1" class="cbox goldb">{b}</span></div>{lab}</div>', track=4)
    life(cid, s, e, 0.3)
    appear(f"#{cid}-0", ta, 0.35)
    pop(f"#{cid}-p", tb - 0.15, 0.3)
    appear(f"#{cid}-1", tb, 0.35)
    sfx("pop", ta, 0.3)
    sfx("pop", tb, 0.3)


def qstack(cid, s, e, qs, times, side="right", title=None):
    pos = "right:110px;align-items:flex-end" if side == "right" else "left:110px"
    grad = "grad-r" if side == "right" else "grad-l"
    head = f'<div class="kicker2">{title}</div>' if title else ""
    rows = "".join(f'<div id="{cid}-{i}" class="qrow bebas">{t}</div>' for i, t in enumerate(qs))
    clip(cid, s, e, f'<div class="in"><div class="{grad}"></div><div class="stack" style="{pos};top:280px;gap:16px">{head}{rows}</div></div>', track=4)
    life(cid, s, e, 0.25)
    for i, t in enumerate(times):
        appear(f"#{cid}-{i}", t, 0.32, 0, 40 if side == "right" else -40)
        sfx("tick", t, 0.4)


def optstack(cid, s, e, rows, times, side="left", title=None, size=50):
    pos = "left:110px" if side == "left" else "right:110px;align-items:flex-end"
    grad = "grad-l" if side == "left" else "grad-r"
    head = f'<div class="kicker2">{title}</div>' if title else ""
    body = "".join(f'<div id="{cid}-{i}" class="optl{" gold" if i == len(rows) - 1 else ""}" style="font-size:{size}px">{t}</div>' for i, t in enumerate(rows))
    clip(cid, s, e, f'<div class="in"><div class="{grad}"></div><div class="stack" style="{pos};top:300px;gap:20px">{head}{body}</div></div>', track=4)
    life(cid, s, e, 0.3)
    for i, t in enumerate(times):
        appear(f"#{cid}-{i}", t, 0.35, 0, -40 if side == "left" else 40)
        sfx("pop", t, 0.3)


NEUTRAL = []  # (start, end) windows with the camera at 1.0
CLOSE = []    # (start, end, zoom) emphasis windows


def zoom_plan():
    src = [s for s in SEGS if s["kind"] == "src"]
    words_out = json.load(open(EDIT / "words_out.json", encoding="utf8"))
    last_text = {}
    for w in words_out:
        last_text[w["seg"]] = w["text"]
    alt, prev = 0, None
    for s in src:
        t = s["out"]
        new_sentence = prev is None or last_text.get(prev["i"], ".")[-1:] in ".?!:" or prev["label"] != s["label"]
        if new_sentence:
            alt ^= 1
        prev = s
        if any(a - 0.8 <= t < b + 0.4 for a, b in NEUTRAL):
            z = 1.0
        else:
            close = next((c for a, b, c in CLOSE if a <= t + 0.05 < b), None)
            z = (close + (0.06 if alt else 0)) if close else (1.11 if alt else 1.0)
        js.append(f'tl.set("#zoom",{{scale:{z}}},{qd(t)});')


def G(txt):
    return f'<em class="gold">{txt}</em>'


def emph(cid, i0, i1, lines, size=62, hold=0.6, zoom=1.16):
    phrase(cid, i0, i1, lines, size, hold)
    CLOSE.append((T(i0, -0.2), TE(i1, hold + 0.2), zoom))



exec(open(HERE / "ep7_cues.py", encoding="utf8").read())

zoom_plan()

# ---------------------------------------------------------------- HTML
CSS = Path(HERE / "style.css").read_text(encoding="utf8")
html = f"""<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=1920, height=1080" />
<title>A educação profissional do futuro</title>
<style>
{CSS}
</style>
</head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{qd(TOTAL)}" data-fps="30" data-width="1920" data-height="1080">
  <div id="cam"><div id="zoom" data-layout-allow-overflow>
    <video id="base" src="assets/base.mp4" playsinline data-has-audio="true" data-start="0" data-duration="{qd(TOTAL)}" data-track-index="0"></video>
  </div></div>
  {chr(10).join(els)}
  {chr(10).join(auds)}
</div>
<script src="assets/gsap.min.js"></script>
<script>
const tl = gsap.timeline({{ paused: true }});
tl.set("#zoom", {{ scale: 1 }}, 0);
{render_js()}
window.__timelines["main"] = tl;
</script>
</body>
</html>
"""
(HERE / "index.html").write_text(html, encoding="utf8")
assert '<video id="vin"' in html, "vinheta missing"  # EP3 shipped without it once
print(f"index.html: {len(els)} elements, {len(js)} tweens, {len(auds)} sfx, {len(BROLL_USED)} b-roll clips, duration {TOTAL:.2f}s")
