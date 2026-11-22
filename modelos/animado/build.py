"""Monta a composição do vídeo animado (9:16, 30 fps, tela cheia em 3D).

Uso: python build.py <pasta do vídeo>   ->   hf/index.html
Lê roteiro.json e out/words.json (gerado pelo voz.py). As cenas ficam em hf/cenas.js; o kit comum, em hf/kit.js.
"""
import json, math, os, re, shutil, sys
from pathlib import Path

raiz = Path(sys.argv[1] if len(sys.argv) > 1 else ".").resolve()
REPO = next(p for p in [raiz, *raiz.parents] if (p / "assets" / "astronauta.js").is_file())
hf = raiz / "hf"
(hf / "assets").mkdir(parents=True, exist_ok=True)
for n in ["gsap.min.js", "astronauta.js"]:
    shutil.copy(REPO / "assets" / n, hf / "assets" / n)
for n in ["three", "fonts"]:
    shutil.copytree(REPO / "assets" / n, hf / "assets" / n, dirs_exist_ok=True)

W, H, FPS = 1080, 1920, 30
V = json.load(open(raiz / "out" / "words.json", encoding="utf8"))
TOTAL = math.ceil(V["total"] * FPS) / FPS

# legendas: trechos de até 3 palavras, quebrados na pontuação e na troca de cena
trechos, atual = [], []
for c in V["cenas"]:
    for w in c["w"]:
        atual.append(w)
        if len(atual) == 3 or sum(len(x["w"]) for x in atual) > 15 or re.search(r"[.,:;!?]$", w["w"]):
            trechos.append(atual); atual = []
    if atual:
        trechos.append(atual); atual = []
caps, html = [], []
for k, ws in enumerate(trechos):
    prox = trechos[k + 1][0]["t0"] if k + 1 < len(trechos) else TOTAL
    fim = prox if prox - ws[-1]["t1"] < 0.5 else ws[-1]["t1"] + 0.3
    caps.append({"id": f"cap{k}", "s": round(ws[0]["t0"], 3), "e": round(min(fim, TOTAL), 3),
                 "w": [{"id": f"cap{k}w{i}", "t": round(w["t0"], 3)} for i, w in enumerate(ws)]})
    spans = "".join(f'<span id="cap{k}w{i}" class="w">{re.sub(r"[.,:;]+$", "", w["w"])}</span>' for i, w in enumerate(ws))
    html.append(f'<div id="cap{k}" class="cap"><span class="pill">{spans}</span></div>')

# o 3D é desenhado por software (sem placa de vídeo): a 75% e ampliado fica ~40% mais rápido; textos e legendas seguem em 1080. ESCALA=1 desliga
ANIM = {"W": W, "H": H, "fps": FPS, "total": TOTAL, "cenas": V["cenas"], "caps": caps, "q": {"escala": float(os.environ.get("ESCALA", "0.75"))}}
FONTES = [("Inter", 400, "Inter-400-latin.woff2"), ("Inter", 700, "Inter-700-latin.woff2"), ("Bebas Neue", 400, "bebas-neue-latin-400-normal.woff2")]
CSS = "".join(f'@font-face{{font-family:"{n}";font-weight:{p};src:url("assets/fonts/{a}") format("woff2")}}' for n, p, a in FONTES) + f"""
html,body{{margin:0;background:#000}}
#root{{position:relative;width:{W}px;height:{H}px;overflow:hidden;background:#8fd0ff}}
#gl,#hud,#caps{{position:absolute;left:0;top:0;width:{W}px;height:{H}px}}
.cap{{position:absolute;left:0;top:1585px;width:{W}px;text-align:center;visibility:hidden}}
.pill{{display:inline-block;padding:16px 38px;border-radius:999px;background:#0b2266;color:#fff;font:700 68px/88px "Inter";box-shadow:0 12px 36px rgba(0,0,0,.45);white-space:nowrap}}
.w{{display:inline-block;margin:0 9px;opacity:.5}}
"""
(hf / "index.html").write_text(f"""<!doctype html>
<html lang="pt-BR">
<head><meta charset="utf-8"><title>{json.load(open(raiz / "roteiro.json", encoding="utf8"))["titulo"]}</title><style>{CSS}</style></head>
<body>
<div id="root" data-composition-id="main" data-start="0" data-duration="{TOTAL:.4f}" data-fps="{FPS}" data-width="{W}" data-height="{H}">
  <canvas id="gl" width="{W}" height="{H}"></canvas>
  <div id="hud"></div>
  <div id="caps">{"".join(html)}</div>
</div>
<script src="assets/gsap.min.js"></script>
<script>
window.ANIM = {json.dumps(ANIM, ensure_ascii=False)};
window.tl = gsap.timeline({{ paused: true }});
window.__timelines = window.__timelines || {{}}; window.__timelines["main"] = window.tl;
window.__hf = window.__hf || {{}}; window.__hf.buildReady = window.__hf.buildReady || {{}};
window.__hf.buildReady.cenas = new Promise((ok) => {{ window.__cenasProntas = ok; }});
</script>
<script type="importmap">{{"imports": {{"three": "./assets/three/three.module.js", "three/addons/": "./assets/three/addons/"}}}}</script>
<script type="module" src="cenas.js"></script>
</body>
</html>
""", encoding="utf8")
print(f"composição ok: {TOTAL:.2f} s, {len(V['cenas'])} cenas, {len(caps)} legendas -> {hf / 'index.html'}")
