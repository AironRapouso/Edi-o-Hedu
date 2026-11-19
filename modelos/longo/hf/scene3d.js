// EP6 — 3D layer (three.js r181, vendored). Same visual language as the Reels (paper, gold pawn = VOCÊ, robot = IA,
// navy plates with Bebas text), driven by a declarative scene list written by build.py (window.EP.scenes).
// Pure function of the timeline time: HyperFrames seeks the GSAP timeline and dispatches "hf-seek"; we render that frame.
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { FontLoader } from "three/addons/loaders/FontLoader.js";
import { TextGeometry } from "three/addons/geometries/TextGeometry.js";

const ready = window.__scene3dReady || (() => {});
const problems = [];
try { await build(); } catch (err) { problems.push(err); }
if (problems.length) {
  const d = document.createElement("div");
  d.id = "err3d";
  d.style.cssText = "position:absolute;left:0;top:0;z-index:99;width:1920px;background:#c00;color:#fff;font:20px monospace;white-space:pre-wrap;padding:12px";
  d.textContent = problems.map((e) => "scene3d: " + (e && e.stack ? e.stack : e)).join("\n\n");
  document.getElementById("root").appendChild(d);
  problems.forEach((e) => console.error("scene3d", e));
}
ready();

async function build() {
  const tl = window.tl;
  const EP = window.EP;
  const W = 1920, H = 1080, PANEL_X = EP.panelX;               // side scenes render right of PANEL_X
  const IR = { immediateRender: false };
  await Promise.all(['400 120px "Bebas Neue"', '700 60px "Inter"', '700 60px "Playfair Display"', '700 40px "Mono"'].map((f) => document.fonts.load(f)));
  const font = new FontLoader().parse(await (await fetch("assets/three/fonts/helvetiker_bold.typeface.json")).json());

  // ------------------------------------------------------------------ renderer, light, materials
  const canvas = document.getElementById("gl");
  const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(W, H, false);
  renderer.setClearColor(0x000000, 0);
  renderer.autoClear = false;
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.NeutralToneMapping;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;
  const scene = new THREE.Scene();
  scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.75;
  const key = new THREE.DirectionalLight(0xffffff, 2.1);
  key.position.set(6, 12, 9);
  key.target.position.set(0, 2.6, 0);
  key.castShadow = true;
  key.shadow.mapSize.set(2048, 2048);
  Object.assign(key.shadow.camera, { left: -14, right: 14, top: 14, bottom: -14, near: 1, far: 50 });
  key.shadow.bias = -0.0005;
  key.shadow.normalBias = 0.03;
  const rim = new THREE.DirectionalLight(0xbfd8ff, 0.85);
  rim.position.set(-8, 7, -7);
  scene.add(key, key.target, rim, new THREE.HemisphereLight(0xffffff, 0xdfe6f5, 0.55));

  const mat = (hex, o = {}) => new THREE.MeshPhysicalMaterial({ color: hex, roughness: o.r ?? 0.42, metalness: o.m ?? 0, clearcoat: o.cc ?? 0.5, clearcoatRoughness: 0.3 });
  const basic = (hex, o = 1) => new THREE.MeshBasicMaterial({ color: hex, transparent: o < 1, opacity: o, toneMapped: false });
  const MATS = {
    gold: () => mat(0xf4b04a, { r: 0.28, m: 0.35, cc: 0.9 }), goldD: () => mat(0xdc9a36, { r: 0.3, m: 0.4, cc: 0.9 }),
    navy: () => mat(0x0b2266, { r: 0.4 }), ink: () => mat(0x05103a, { r: 0.3, cc: 0.9 }), blue: () => mat(0x0457e7, { r: 0.35 }),
    sky: () => mat(0x5ca2ee, { r: 0.4 }), white: () => mat(0xf8f6f1, { r: 0.55, cc: 0.25 }), grey: () => mat(0xa9afbd, { r: 0.5, cc: 0.2 }),
    greyD: () => mat(0x7d8496, { r: 0.5, cc: 0.2 }), red: () => mat(0xe5484d, { r: 0.4 }), green: () => mat(0x2fb36b, { r: 0.4 }),
    kraft: () => mat(0xdcae72, { r: 0.75, cc: 0.05 }), kraftD: () => mat(0xb9864a, { r: 0.75, cc: 0.05 }), plate: () => mat(0x071447, { r: 0.7, cc: 0 }),
    ice: () => mat(0xeaf4ff, { r: 0.25, cc: 1.0 }), iceD: () => mat(0x9cc6ef, { r: 0.3, cc: 0.8 }), cream: () => mat(0xf3e9d6, { r: 0.6, cc: 0.15 }),
    belt: () => mat(0x2a3142, { r: 0.8, cc: 0.0 }),
  };
  const M = {};
  for (const k in MATS) M[k] = MATS[k]();
  const BLUE = basic(0x0457e7), GLOW = basic(0xffc85e);

  // ------------------------------------------------------------------ builders
  const sh = (m) => { m.castShadow = true; m.receiveShadow = true; return m; };
  const rbox = (w, h, d, r, material) => sh(new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 5, Math.min(r, w / 2 - 0.001, h / 2 - 0.001, d / 2 - 0.001)), material));
  const cyl = (rt, rb, h, material, seg = 48) => sh(new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg), material));
  const sph = (r, material) => sh(new THREE.Mesh(new THREE.SphereGeometry(r, 48, 28), material));
  function text3d(str, size, depth, material) {
    const g = new TextGeometry(str, { font, size, depth, curveSegments: 10, bevelEnabled: true, bevelThickness: size * 0.035, bevelSize: size * 0.025, bevelSegments: 3 });
    g.computeBoundingBox();
    const b = g.boundingBox;
    g.translate(-(b.min.x + b.max.x) / 2, -b.min.y, -(b.min.z + b.max.z) / 2);
    return sh(new THREE.Mesh(g, material));
  }
  function textPlane(w, h, draw, ppu = 220) {
    const c = document.createElement("canvas");
    c.width = Math.round(w * ppu);
    c.height = Math.round(h * ppu);
    draw(c.getContext("2d", { willReadFrequently: true }), c.width, c.height);   // CPU raster: the GPU glyph cache garbled random letters
    const tex = new THREE.CanvasTexture(c);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;
    return new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tex, transparent: true, toneMapped: false }));
  }
  const bebas = (x, px, ls = 0.03) => { x.font = `400 ${Math.round(px)}px "Bebas Neue"`; x.letterSpacing = "0px"; x._ls = Math.round(px * ls); };
  {
    const P = CanvasRenderingContext2D.prototype, mt = P.measureText, ft = P.fillText;
    if (!P._spaced) {
      P._spaced = true;
      P.measureText = function (t) { const m = mt.call(this, t); if (!this._ls || !t) return m; const w = m.width + this._ls * ([...t].length - 1);
        return { width: w, actualBoundingBoxAscent: m.actualBoundingBoxAscent, actualBoundingBoxDescent: m.actualBoundingBoxDescent,
                 actualBoundingBoxLeft: m.actualBoundingBoxLeft, actualBoundingBoxRight: m.actualBoundingBoxRight }; };
      P.fillText = function (t, a, b, mw) {
        if (!this._ls || !t) return ft.call(this, t, a, b, mw);
        const ch = [...String(t)], ws = ch.map((c) => mt.call(this, c).width), tot = ws.reduce((u, v) => u + v, 0) + this._ls * (ch.length - 1);
        const al = this.textAlign; let cx = al === "center" ? a - tot / 2 : (al === "right" || al === "end") ? a - tot : a;
        this.textAlign = "left";
        ch.forEach((c, k) => { ft.call(this, c, cx, b); cx += ws[k] + this._ls; });
        this.textAlign = al;
      };
    }
  }
  const rr = (x, a, b, w, h, r) => { x.beginPath(); x.roundRect(a, b, w, h, r); };
  function fitText(x, txt, w, h, fs, ls) {                       // shrink a single line until it fits
    let px = h * fs;
    bebas(x, px, ls);
    while (x.measureText(txt).width > w * 0.9 && px > 8) { px *= 0.95; bebas(x, px, ls); }
  }
  const label = (txt, color, fs = 0.62, ty = 0.56) => (x, w, h) => {
    x.fillStyle = color;
    fitText(x, txt, w, h, fs, 0.05);
    x.textAlign = "center";
    x.textBaseline = "middle";
    x.fillText(txt, w / 2, h * ty);
  };
  const PLATE_BG = { plate: "plate", white: "white", gold: "gold", red: "red", blue: "blue", grey: "greyD", green: "green" };
  const PLATE_FG = { plate: "#F6F6F8", white: "#0B2266", gold: "#0B2266", red: "#FFFFFF", blue: "#FFFFFF", grey: "#FFFFFF", green: "#FFFFFF" };
  function plate(o) {
    const w = o.w ?? Math.max(1.3, 0.34 * (o.txt || "").length + 0.5), h = o.h ?? 0.62, d = o.d ?? 0.14, bg = o.bg ?? "plate";
    const g = new THREE.Group();
    const body = rbox(w, h, d, h * 0.28, o.own ? MATS[PLATE_BG[bg]]() : M[PLATE_BG[bg]]);
    g.add(body);
    const face = textPlane(w, h, label(o.txt, o.fg ?? PLATE_FG[bg], o.fs ?? 0.64));
    face.position.z = d / 2 + 0.006;
    g.add(face);
    g.userData.body = body;
    return g;
  }
  function star(r) {
    const s = new THREE.Shape();
    for (let i = 0; i < 8; i++) {
      const a = (i * Math.PI) / 4, rad = i % 2 ? r * 0.2 : r;
      if (i) s.lineTo(Math.cos(a) * rad, Math.sin(a) * rad); else s.moveTo(Math.cos(a) * rad, Math.sin(a) * rad);
    }
    s.closePath();
    return new THREE.Mesh(new THREE.ExtrudeGeometry(s, { depth: r * 0.1, bevelEnabled: false }), basic(0xffd98a));
  }
  function frame(w, h, t, material, d = 0.06) {
    const g = new THREE.Group();
    [[0, h / 2, w + t, t], [0, -h / 2, w + t, t], [-w / 2, 0, t, h + t], [w / 2, 0, t, h + t]].forEach(([x, y, bw, bh]) => {
      const m = new THREE.Mesh(new THREE.BoxGeometry(bw, bh, d), material);
      m.position.set(x, y, 0);
      g.add(m);
    });
    return g;
  }
  function robotHead() {
    const h = new THREE.Group();
    h.add(rbox(2.3, 1.5, 1.4, 0.36, M.white));
    const visor = rbox(1.8, 0.8, 0.12, 0.2, M.ink);
    visor.position.set(0, 0, 0.68);
    h.add(visor);
    const eyeM = basic(0x8fd8ff);
    [-0.42, 0.42].forEach((x) => { const e = new THREE.Mesh(new THREE.CircleGeometry(0.17, 32), eyeM); e.position.set(x, 0.02, 0.745); h.add(e); });
    [-1.2, 1.2].forEach((x) => { const ear = cyl(0.24, 0.24, 0.14, M.sky); ear.rotation.z = Math.PI / 2; ear.position.x = x; h.add(ear); });
    const ant = cyl(0.045, 0.045, 0.42, M.navy, 12);
    ant.position.y = 0.95;
    const tip = sph(0.14, M.gold);
    tip.position.y = 1.22;
    h.add(ant, tip);
    h.userData.eyeM = eyeM;
    return h;
  }
  function robot() {
    const g = new THREE.Group();
    const rh = robotHead();
    rh.position.y = 3.0;
    const neck = cyl(0.24, 0.24, 0.26, M.navy);
    neck.position.y = 2.15;
    const body = rbox(2.0, 1.65, 1.3, 0.32, M.blue);
    body.position.y = 1.25;
    const chest = rbox(1.15, 0.62, 0.08, 0.12, M.white);
    chest.position.set(0, 1.4, 0.66);
    const lamp = new THREE.Mesh(new THREE.CircleGeometry(0.1, 24), basic(0xf4b04a));
    lamp.position.set(0.32, 1.42, 0.705);
    const b1 = rbox(0.5, 0.09, 0.03, 0.03, M.sky);
    b1.position.set(-0.2, 1.48, 0.705);
    const b2 = rbox(0.34, 0.09, 0.03, 0.03, M.sky);
    b2.position.set(-0.28, 1.31, 0.705);
    g.add(rh, neck, body, chest, lamp, b1, b2);
    [-0.5, 0.5].forEach((x) => { const leg = cyl(0.3, 0.34, 0.5, M.navy); leg.position.set(x, 0.25, 0); g.add(leg); });
    const arms = [-1, 1].map((sg) => {
      const pivot = new THREE.Group();
      pivot.position.set(sg * 1.24, 1.85, 0.05);
      const arm = sh(new THREE.Mesh(new THREE.CapsuleGeometry(0.19, 0.75, 8, 20), M.sky));
      arm.position.y = -0.55;
      pivot.add(arm);
      pivot.rotation.z = sg * 0.22;
      g.add(pivot);
      return pivot;
    });
    g.userData = { head: rh, arms, eyeM: rh.userData.eyeM };
    return g;
  }
  function pawn(material) {
    const g = new THREE.Group();
    const base = cyl(0.98, 1.04, 0.18, material, 64);
    base.position.y = 0.09;
    const body = cyl(0.46, 0.86, 2.05, material, 64);
    body.position.y = 1.2;
    const collar = cyl(0.64, 0.64, 0.14, material, 64);
    collar.position.y = 2.28;
    const head = sph(0.62, material);
    head.position.y = 2.95;
    g.add(base, body, collar, head);
    return g;
  }
  function pawnCrossed(material) {                              // pawn with folded arms (the refusal)
    const g = pawn(material);
    const arm = sh(new THREE.Mesh(new THREE.CapsuleGeometry(0.17, 1.15, 8, 20), material));
    arm.rotation.z = Math.PI / 2;
    arm.position.set(0, 1.75, 0.62);
    const arm2 = arm.clone();
    arm2.position.set(0, 1.55, 0.7);
    g.add(arm, arm2);
    return g;
  }
  function coinStack(n, r) {
    const g = new THREE.Group();
    for (let k = 0; k < n; k++) {
      const c = cyl(r, r, 0.17, k % 2 ? M.goldD : M.gold, 56);
      c.position.set((((k * 37) % 7) - 3) * 0.012, 0.085 + k * 0.178, (((k * 53) % 5) - 2) * 0.012);
      g.add(c);
    }
    return g;
  }
  function calendar(txt) {
    const cal = new THREE.Group();
    cal.add(rbox(2.8, 2.3, 0.36, 0.14, M.white));
    const chead = rbox(2.84, 0.62, 0.4, 0.14, M.red);
    chead.position.y = 0.86;
    cal.add(chead);
    [-0.8, 0.8].forEach((x) => { const r = sh(new THREE.Mesh(new THREE.TorusGeometry(0.16, 0.05, 12, 32), M.ink)); r.position.set(x, 1.2, 0); r.rotation.y = Math.PI / 2; cal.add(r); });
    const ct = textPlane(2.6, 1.5, label(txt, "#0B2266", 0.9, 0.56));
    ct.position.set(0, -0.32, 0.19);
    cal.add(ct);
    return cal;
  }
  function parcel() {
    const g = new THREE.Group();
    g.add(rbox(0.96, 0.76, 0.8, 0.06, M.kraft), rbox(0.2, 0.775, 0.815, 0.02, M.kraftD));
    return g;
  }
  function badge(r, kind) {                                       // red ✕ or green ✓ disc
    const g = new THREE.Group();
    const disc = cyl(r, r, 0.14, kind === "ok" ? M.green : M.red, 56);
    disc.rotation.x = Math.PI / 2;
    g.add(disc);
    if (kind === "ok") {
      const a = rbox(r * 0.55, r * 0.24, 0.06, 0.03, M.white); a.rotation.z = -Math.PI / 4; a.position.set(-r * 0.22, -r * 0.08, 0.09);
      const b = rbox(r * 1.0, r * 0.24, 0.06, 0.03, M.white); b.rotation.z = Math.PI / 4.4; b.position.set(r * 0.16, r * 0.1, 0.09);
      g.add(a, b);
    } else {
      [-1, 1].forEach((sg) => { const b = rbox(r * 1.15, r * 0.24, 0.06, 0.03, M.white); b.rotation.z = (sg * Math.PI) / 4; b.position.z = 0.09; g.add(b); });
    }
    return g;
  }
  function nosign(R) {
    const g = new THREE.Group();
    g.add(sh(new THREE.Mesh(new THREE.TorusGeometry(R, R * 0.1, 20, 72), M.red)));
    const bar = rbox(R * 1.95, R * 0.2, R * 0.16, R * 0.05, M.red);
    bar.rotation.z = -Math.PI / 4;
    g.add(bar);
    return g;
  }
  function doc(o) {                                               // a sheet of paper with a title and lines
    const w = o.w ?? 2.0, h = o.h ?? 2.6;
    const g = new THREE.Group();
    g.add(rbox(w, h, 0.06, 0.06, M.white));
    const face = textPlane(w, h, (x, cw, ch) => {
      x.fillStyle = "#FFFFFF"; x.fillRect(0, 0, cw, ch);
      x.fillStyle = o.head ?? "#0B2266"; x.fillRect(0, 0, cw, ch * 0.2);
      x.fillStyle = "#F6F6F8"; fitText(x, o.txt || "", cw, ch * 0.2, 0.62, 0.05);
      x.textAlign = "center"; x.textBaseline = "middle"; x.fillText(o.txt || "", cw / 2, ch * 0.11);
      x.fillStyle = "#C9CEDB";
      for (let i = 0; i < 6; i++) x.fillRect(cw * 0.1, ch * (0.3 + i * 0.11), cw * [0.78, 0.6, 0.72, 0.5, 0.66, 0.42][i], ch * 0.04);
      if (o.big) { x.fillStyle = o.bigColor ?? "#E5484D"; bebas(x, ch * 0.42, 0.02); x.textAlign = "center"; x.fillText(o.big, cw * 0.72, ch * 0.72); }
    });
    face.position.z = 0.032;
    g.add(face);
    return g;
  }
  function bubble(o) {                                            // chat bubble with text
    const w = o.w ?? 2.6, h = o.h ?? 1.2;
    const g = new THREE.Group();
    const m = o.bg === "blue" ? M.blue : M.white;
    g.add(rbox(w, h, 0.3, 0.4, m));
    const tail = sh(new THREE.Mesh(new THREE.ConeGeometry(0.22, 0.6, 4), m));
    tail.position.set(-w / 2 + 0.4, -h / 2 - 0.15, 0);
    tail.rotation.z = 2.4;
    g.add(tail);
    const t = textPlane(w, h, label(o.txt || "", o.bg === "blue" ? "#FFFFFF" : "#0B2266", 0.48));
    t.position.z = 0.16;
    g.add(t);
    return g;
  }
  function iceberg() {
    const g = new THREE.Group();
    const tip = sh(new THREE.Mesh(new THREE.IcosahedronGeometry(1.0, 0), M.ice));
    tip.scale.set(1.3, 1.4, 1.0);
    tip.position.y = 0.55;
    const base = sh(new THREE.Mesh(new THREE.IcosahedronGeometry(1.0, 1), M.iceD));
    base.scale.set(3.1, 2.4, 2.2);
    base.position.y = -2.6;
    const water = new THREE.Mesh(new THREE.PlaneGeometry(14, 0.06), basic(0x1892f0, 0.9));
    water.position.set(0, 0, 1.8);
    const sea = new THREE.Mesh(new THREE.PlaneGeometry(14, 6.5), basic(0x5ca2ee, 0.22));
    sea.position.set(0, -3.25, 1.75);
    g.add(tip, base, water, sea);
    g.userData = { tip, base };
    return g;
  }
  function belt(len) {                                            // conveyor belt with rollers
    const g = new THREE.Group();
    g.add(rbox(len, 0.25, 1.4, 0.1, M.belt));
    for (let i = 0; i < 2; i++) { const leg = rbox(0.25, 1.2, 1.2, 0.05, M.greyD); leg.position.set((i ? 1 : -1) * (len / 2 - 0.4), -0.7, 0); g.add(leg); }
    const stripes = [];
    for (let i = 0; i < Math.round(len / 0.6); i++) {
      const s = new THREE.Mesh(new THREE.BoxGeometry(0.08, 0.02, 1.35), basic(0x4b5568));
      s.position.set(-len / 2 + 0.3 + i * 0.6, 0.13, 0);
      g.add(s);
      stripes.push(s);
    }
    g.userData = { stripes, len };
    return g;
  }
  function armBot() {                                             // industrial robot arm
    const g = new THREE.Group();
    const base = cyl(0.6, 0.75, 0.4, M.navy);
    base.position.y = 0.2;
    const j1 = new THREE.Group();
    j1.position.y = 0.4;
    const up = rbox(0.42, 2.0, 0.42, 0.14, M.gold);
    up.position.y = 1.0;
    const j2 = new THREE.Group();
    j2.position.y = 2.0;
    const fore = rbox(1.8, 0.36, 0.36, 0.12, M.gold);
    fore.position.x = 0.9;
    const claw = rbox(0.3, 0.6, 0.5, 0.08, M.ink);
    claw.position.set(1.8, -0.3, 0);
    j2.add(sph(0.3, M.ink), fore, claw);
    j1.add(sph(0.34, M.ink), up, j2);
    g.add(base, j1);
    g.userData = { j1, j2 };
    return g;
  }
  function counter(txt) {                                         // bank teller counter
    const g = new THREE.Group();
    const desk = rbox(3.6, 1.4, 1.2, 0.08, M.white);
    desk.position.y = 0.7;
    const top = rbox(3.8, 0.12, 1.4, 0.04, M.navy);
    top.position.y = 1.45;
    const glass = new THREE.Mesh(new THREE.PlaneGeometry(3.4, 1.4), basic(0xcfe8ff, 0.3));
    glass.position.set(0, 2.2, 0.2);
    const sign = plate({ txt, w: 2.0, h: 0.6, bg: "plate" });
    sign.position.set(0, 3.25, 0.1);
    g.add(desk, top, glass, sign);
    return g;
  }
  function atm() {
    const g = new THREE.Group();
    const body = rbox(1.6, 2.8, 1.0, 0.12, M.navy);
    body.position.y = 1.4;
    const screen = rbox(1.1, 0.75, 0.05, 0.05, M.sky);
    screen.position.set(0, 2.15, 0.51);
    const pad = rbox(0.9, 0.4, 0.05, 0.04, M.white);
    pad.position.set(0, 1.45, 0.51);
    const slot = rbox(0.8, 0.08, 0.05, 0.02, M.ink);
    slot.position.set(0, 1.05, 0.51);
    const s = textPlane(1.1, 0.75, label("24H", "#FFFFFF", 0.62));
    s.position.set(0, 2.15, 0.54);
    g.add(body, screen, pad, slot, s);
    return g;
  }
  function door() {
    const g = new THREE.Group();
    [-1.29, 1.29].forEach((x) => { const j = rbox(0.26, 4.3, 0.5, 0.06, M.navy); j.position.set(x, 2.15, -0.3); g.add(j); });
    const lintel = rbox(2.84, 0.26, 0.5, 0.06, M.navy);
    lintel.position.set(0, 4.31, -0.3);
    const leaf = new THREE.Group();                               // hinged on the left jamb: the leaf swings open, the knob goes with it
    leaf.position.set(-1.15, 0, -0.2);
    const panel = rbox(2.3, 4.15, 0.16, 0.05, M.blue);
    panel.position.set(1.15, 2.08, 0);
    const knob = sph(0.14, M.gold);
    knob.position.set(2.0, 2.0, 0.2);
    leaf.add(panel, knob);
    g.add(lintel, leaf);
    g.userData = { leaf };
    return g;
  }
  function clockPie(o) {                                          // a clock face whose sector fills (time share)
    const g = new THREE.Group();
    const face = cyl(1.5, 1.5, 0.24, M.white, 64);
    face.rotation.x = Math.PI / 2;
    const ring = sh(new THREE.Mesh(new THREE.TorusGeometry(1.52, 0.1, 16, 72), M.navy));
    g.add(face, ring);
    for (let i = 0; i < 12; i++) {
      const a = (i * Math.PI) / 6, tk = rbox(0.06, i % 3 ? 0.14 : 0.26, 0.04, 0.015, M.navy);
      tk.position.set(Math.sin(a) * 1.22, Math.cos(a) * 1.22, 0.14);
      tk.rotation.z = -a;
      g.add(tk);
    }
    const sectorM = basic(o.color ?? 0xe5484d, 0.85);
    sectorM.side = THREE.DoubleSide;
    const sector = new THREE.Mesh(new THREE.CircleGeometry(1.08, 64, Math.PI / 2, 0.0001), sectorM);
    sector.position.z = 0.13;
    g.add(sector);
    g.userData = { sector, frac: { v: 0 } };
    return g;
  }
  function alarm() {
    const g = new THREE.Group();
    const body = cyl(1.2, 1.2, 0.7, M.red, 64);
    body.rotation.x = Math.PI / 2;
    const face = cyl(1.0, 1.0, 0.72, M.white, 64);
    face.rotation.x = Math.PI / 2;
    face.position.z = 0.02;
    const hh = rbox(0.1, 0.55, 0.05, 0.03, M.ink); hh.position.set(0, 0.25, 0.4);
    const mh = rbox(0.07, 0.8, 0.05, 0.03, M.ink); mh.position.set(0.25, 0.3, 0.42); mh.rotation.z = -0.7;
    const bells = [-1, 1].map((sg) => { const b = sph(0.42, M.gold); b.scale.set(1, 0.8, 1); b.position.set(sg * 0.85, 1.1, 0); return b; });
    const legs = [-1, 1].map((sg) => { const l = cyl(0.08, 0.08, 0.5, M.ink, 12); l.position.set(sg * 0.7, -1.25, 0); l.rotation.z = sg * 0.5; return l; });
    const hammer = rbox(0.12, 0.5, 0.12, 0.04, M.ink); hammer.position.set(0, 1.35, 0);
    g.add(body, face, hh, mh, hammer, ...bells, ...legs);
    return g;
  }
  function folder() {
    const g = new THREE.Group();
    const back = rbox(2.6, 2.0, 0.08, 0.06, M.kraftD);
    const tab = rbox(0.9, 0.3, 0.08, 0.06, M.kraftD); tab.position.set(-0.75, 1.1, 0);
    const paperIn = doc({ txt: "CERTIFICADO", w: 2.2, h: 1.6, head: "#C9A45A" }); paperIn.position.set(0, 0.25, 0.06); paperIn.rotation.z = 0.04;
    const front = rbox(2.6, 1.55, 0.08, 0.06, M.kraft); front.position.set(0, -0.22, 0.14);
    g.add(back, tab, paperIn, front);
    g.userData = { paperIn };
    return g;
  }
  function numeral(txt, size = 2.4, m = M.gold) { return text3d(txt, size, size * 0.27, m); }
  function bar(o) {                                               // a bar that grows from its base (scale.y)
    const g = new THREE.Group();
    const m = o.mat ? (M[o.mat] || M.blue) : M.blue;
    const b = rbox(o.w ?? 1.4, o.h ?? 3, o.d ?? 1.0, 0.12, m);
    b.position.y = (o.h ?? 3) / 2;
    g.add(b);
    g.userData = { grow: g };
    return g;
  }
  function hbar(o) {                                              // a horizontal bar that grows to the right (scale.x)
    const g = new THREE.Group();
    const b = rbox(o.w ?? 4, o.h ?? 0.6, 0.4, 0.1, M[o.mat || "red"]);
    b.position.x = (o.w ?? 4) / 2;
    g.add(b);
    return g;
  }
  function gridPanel(o) {                                         // lit squares that go dark one by one (blackout)
    const g = new THREE.Group();
    const cells = [];
    const n = o.n ?? 6, m = o.m ?? 4, s = 0.62;
    for (let i = 0; i < n; i++) for (let j = 0; j < m; j++) {
      const mm = basic(0xffc85e);
      const c = new THREE.Mesh(new THREE.BoxGeometry(s * 0.86, s * 0.86, 0.1), mm);
      c.position.set((i - (n - 1) / 2) * s, (j - (m - 1) / 2) * s, 0);
      g.add(c);
      cells.push(c);
    }
    const back = rbox(n * s + 0.3, m * s + 0.3, 0.12, 0.1, M.ink); back.position.z = -0.08;
    g.add(back);
    g.userData = { cells };
    return g;
  }
  function slotPiece(o) {                                         // a "job opening": board with a star-shaped hole, and pawn-shaped pieces that don't fit
    const g = new THREE.Group();
    const board = rbox(2.4, 2.4, 0.3, 0.12, M.white);
    const hole = new THREE.Mesh(new THREE.CircleGeometry(0.7, 5), basic(0x0b2266));
    hole.position.z = 0.16;
    g.add(board, hole);
    return g;
  }
  function sheet3(o) {                                            // three-column paper sheet (exercise)
    const w = o.w ?? 6.4, h = o.h ?? 3.8;
    const g = new THREE.Group();
    g.add(rbox(w, h, 0.08, 0.1, M.white));
    const face = textPlane(w, h, (x, cw, ch) => {
      x.fillStyle = "#FFFFFF"; x.fillRect(0, 0, cw, ch);
      const cols = o.cols || ["FRENTE", "MEIO", "FIM"];
      const colors = ["#E5484D", "#F4B04A", "#2FB36B"];
      for (let i = 0; i < 3; i++) {
        x.fillStyle = colors[i]; x.fillRect(i * cw / 3 + cw * 0.02, ch * 0.05, cw / 3 - cw * 0.04, ch * 0.16);
        x.fillStyle = "#FFFFFF"; fitText(x, cols[i], cw / 3, ch * 0.16, 0.6, 0.05); x.textAlign = "center"; x.textBaseline = "middle";
        x.fillText(cols[i], i * cw / 3 + cw / 6, ch * 0.135);
        if (i) { x.fillStyle = "#CDD4E2"; x.fillRect(i * cw / 3 - 2, ch * 0.05, 4, ch * 0.9); }
      }
    });
    face.position.z = 0.042;
    g.add(face);
    return g;
  }

  // ------------------------------------------------------------------ factory table: item spec -> Object3D
  const FACT = {
    pawn: (o) => pawn(o.own ? MATS[o.mat || "gold"]() : M[o.mat || "gold"]),
    pawnX: (o) => pawnCrossed(M[o.mat || "grey"]),
    robot: () => robot(),
    plate: (o) => plate(o),
    text: (o) => text3d(o.txt, o.size ?? 1.2, (o.size ?? 1.2) * 0.28, o.own ? MATS[o.mat || "gold"]() : M[o.mat || "gold"]),
    coins: (o) => coinStack(o.n ?? 6, o.rad ?? 0.5),
    calendar: (o) => calendar(o.txt || ""),
    parcel: () => parcel(),
    badge: (o) => badge(o.rad ?? 0.45, o.kind || "x"),
    nosign: (o) => nosign(o.rad ?? 1.4),
    doc: (o) => doc(o),
    bubble: (o) => bubble(o),
    iceberg: () => iceberg(),
    belt: (o) => belt(o.len ?? 8),
    armbot: () => armBot(),
    counter: (o) => counter(o.txt || "CAIXA"),
    atm: () => atm(),
    door: () => door(),
    clock: (o) => clockPie(o),
    alarm: () => alarm(),
    folder: () => folder(),
    numeral: (o) => numeral(o.txt, o.size ?? 2.4, M[o.mat || "gold"]),
    bar: (o) => bar(o),
    hbar: (o) => hbar(o),
    grid: (o) => gridPanel(o),
    slot: (o) => slotPiece(o),
    sheet3: (o) => sheet3(o),
    star: (o) => star(o.rad ?? 0.3),
    box: (o) => rbox(o.w ?? 0.8, o.h ?? 0.8, o.d ?? 0.8, 0.08, o.own ? MATS[o.mat || "grey"]() : M[o.mat || "grey"]),
    sel: (o) => frame(o.w ?? 1.2, o.h ?? 0.8, o.t ?? 0.07, BLUE),
    beam: (o) => { const g = new THREE.Group(); g.add(new THREE.Mesh(new THREE.PlaneGeometry(o.w ?? 5, 0.07), basic(0x1892f0, 0.95))); g.add(new THREE.Mesh(new THREE.PlaneGeometry(o.w ?? 5, 0.6), basic(0x1892f0, 0.16))); return g; },
  };

  // ------------------------------------------------------------------ generic animation interpreter
  const E3 = (v) => ({ x: v[0], y: v[1], z: v[2] });
  function animate(obj, o, s) {
    const S0 = o.s ?? 1;
    obj.scale.setScalar(S0);
    if (o.p) obj.position.set(...o.p);
    if (Array.isArray(o.r)) obj.rotation.set(...o.r);
    if (o.t != null) {
      if (o.drop) {
        tl.fromTo(obj.position, { y: o.p[1] + o.drop }, { y: o.p[1], duration: o.dd ?? 0.4, ease: o.de ?? "bounce.out" }, o.t);
        tl.fromTo(obj.scale, { x: 0.001, y: 0.001, z: 0.001 }, { x: S0, y: S0, z: S0, duration: 0.08, ease: "power2.out" }, o.t);
      } else if (o.rise) {
        tl.fromTo(obj.position, { y: o.p[1] - o.rise }, { y: o.p[1], duration: o.dd ?? 0.5, ease: "back.out(1.3)" }, o.t);
      } else if (o.slide) {
        tl.fromTo(obj.position, { x: o.p[0] + o.slide }, { x: o.p[0], duration: o.dd ?? 0.45, ease: "power3.out" }, o.t);
        tl.fromTo(obj.scale, { x: 0.001, y: 0.001, z: 0.001 }, { x: S0, y: S0, z: S0, duration: 0.12, ease: "power2.out" }, o.t);
      } else {
        tl.fromTo(obj.scale, { x: 0.001, y: 0.001, z: 0.001 }, { x: S0, y: S0, z: S0, duration: o.dd ?? 0.4, ease: o.de ?? "back.out(1.9)" }, o.t);
      }
    }
    for (const m of o.moves || []) tl.to(obj.position, { ...E3(m.slice(2, 5)), duration: m[1], ease: m[5] || "power3.inOut" }, m[0]);
    for (const m of o.rots || []) tl.to(obj.rotation, { ...E3(m.slice(2, 5)), duration: m[1], ease: m[5] || "power3.inOut" }, m[0]);
    for (const m of o.scales || []) tl.to(obj.scale, { x: m[2], y: m[3] ?? m[2], z: m[4] ?? m[2], duration: m[1], ease: m[5] || "back.out(2)" }, m[0]);
    for (const t of o.pulses || []) tl.fromTo(obj.scale, { x: S0, y: S0, z: S0 }, { x: S0 * 1.16, y: S0 * 1.16, z: S0 * 1.16, duration: 0.11, yoyo: true, repeat: 1, ease: "power2.out", ...IR }, t);
    for (const t of o.shakes || []) tl.fromTo(obj.rotation, { z: obj.rotation.z }, { z: obj.rotation.z + 0.09, duration: 0.05, yoyo: true, repeat: 5, ease: "sine.inOut", ...IR }, t);
    for (const c of o.colors || []) {                            // [t, hex] on every mesh material of the object (cloned first)
      obj.traverse((m) => { if (m.isMesh && m.material && m.material.color && !m.material.map && !m.userData.cl) { m.material = m.material.clone(); m.userData.cl = 1; } });
      const col = new THREE.Color(c[1]);
      obj.traverse((m) => { if (m.isMesh && m.material && m.material.color && !m.material.map) tl.to(m.material.color, { r: col.r, g: col.g, b: col.b, duration: 0.2, ease: "power2.out" }, c[0]); });
    }
    if (o.out != null) tl.to(obj.scale, { x: 0.001, y: 0.001, z: 0.001, duration: o.od ?? 0.2, ease: "power2.in" }, o.out);
    // special behaviours
    const u = obj.userData || {};
    if (o.fill && u.sector) {                                     // clock sector: [[t, d, frac]]
      for (const f of o.fill) tl.to(u.frac, { v: f[2], duration: f[1], ease: "power2.inOut", onUpdate: () => {} }, f[0]);
    }
    if (o.grow) {                                                 // bar: [[t, d, frac]]  scale.y relative
      for (const f of o.grow) tl.fromTo(obj.scale, { y: f[3] ?? 0.001 }, { y: f[2], duration: f[1], ease: "power2.out", ...(f[4] ? IR : {}) }, f[0]);
    }
    if (o.growx) for (const f of o.growx) tl.fromTo(obj.scale, { x: f[3] ?? 0.001 }, { x: f[2], duration: f[1], ease: "power2.out" }, f[0]);
    if (o.dark && u.cells) u.cells.forEach((c, k) => { const t = o.dark[0] + ((k * 7) % u.cells.length) / u.cells.length * o.dark[1]; const col = new THREE.Color(0x1a2340); tl.to(c.material.color, { r: col.r, g: col.g, b: col.b, duration: 0.08 }, t); });
    if (o.doorOpen && u.leaf) for (const d of o.doorOpen) tl.to(u.leaf.rotation, { y: d[2], duration: d[1], ease: "power2.inOut" }, d[0]);
    if (o.knocks && u.leaf) for (const t of o.knocks) tl.fromTo(u.leaf.position, { z: -0.2 }, { z: -0.12, duration: 0.05, yoyo: true, repeat: 1, ease: "power2.out", ...IR }, t);
    if (o.armWork && u.j1) tl.fromTo(u.j1.rotation, { y: -0.6 }, { y: 0.6, duration: 0.55, yoyo: true, repeat: Math.max(1, Math.round((o.armWork[1] - o.armWork[0]) / 0.55)), ease: "sine.inOut", ...IR }, o.armWork[0]);
    if (o.eyesOn && u.eyeM) { const dim = new THREE.Color(0x24345f), lit = new THREE.Color(0x8fd8ff); tl.fromTo(u.eyeM.color, { r: dim.r, g: dim.g, b: dim.b }, { r: lit.r, g: lit.g, b: lit.b, duration: 0.16, ease: "power2.out" }, o.eyesOn); }
    if (o.wave && u.arms) for (const t of o.wave) tl.fromTo(u.arms[1].rotation, { x: 0 }, { x: -1.3, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out", ...IR }, t);
    return { obj, o, u };
  }

  // ------------------------------------------------------------------ scenes
  const SC = [];
  for (const spec of EP.scenes) {
    const g = new THREE.Group();
    g.visible = false;
    scene.add(g);
    const full = spec.mode !== "side";
    const aspect = full ? W / H : (W - PANEL_X) / H;
    const cam = new THREE.PerspectiveCamera(spec.fov ?? 30, aspect, 0.1, 160);
    const look = new THREE.Vector3(...(spec.look || [0, 2.2, 0]));
    cam.position.set(...(spec.cam || [0, 3, 14]));
    for (const c of spec.camMoves || []) {
      tl.to(cam.position, { ...E3(c[2]), duration: c[1], ease: c[4] || "power3.inOut" }, c[0]);
      if (c[3]) tl.to(look, { ...E3(c[3]), duration: c[1], ease: c[4] || "power3.inOut" }, c[0]);
    }
    if (spec.floor !== false) {
      const fl = new THREE.Mesh(new THREE.PlaneGeometry(90, 60), new THREE.ShadowMaterial({ opacity: spec.floorO ?? 0.2 }));
      fl.rotation.x = -Math.PI / 2;
      fl.position.y = spec.floorY ?? 0;
      fl.receiveShadow = true;
      g.add(fl);
    }
    if (spec.wall != null) {
      const wl = new THREE.Mesh(new THREE.PlaneGeometry(90, 60), new THREE.ShadowMaterial({ opacity: 0.12 }));
      wl.position.z = spec.wall;
      wl.receiveShadow = true;
      g.add(wl);
    }
    const live = [];
    for (const it of spec.items) {
      try {
        const make = FACT[it.k];
        if (!make) throw new Error("unknown item " + it.k);
        const obj = make(it);
        if (it.parent != null) live[it.parent].obj.add(obj); else g.add(obj);
        live.push(animate(obj, it, spec));
      } catch (err) { problems.push(err); live.push({ obj: new THREE.Group(), o: it, u: {} }); }
    }
    SC.push({ spec, g, cam, look, live, full });
  }

  function renderAt(t) {
    if (window.__faceAt) window.__faceAt(t);
    key.position.x = 6 + Math.sin(t * 0.8) * 0.9;
    renderer.setScissorTest(false);
    renderer.setViewport(0, 0, W, H);
    renderer.clear(true, true, true);
    for (const s of SC) {
      const on = t >= s.spec.t0 && t < s.spec.t1;
      s.g.visible = on;
      if (!on) continue;
      const u0 = t - s.spec.t0;
      for (const L of s.live) {                                   // continuous behaviours
        const o = L.o, u = L.u;
        if (o.float) L.obj.position.y = o.p[1] + Math.sin(u0 * 2.0 + (o.p[0] || 0)) * o.float;
        if (o.spin) L.obj.rotation.y = (Array.isArray(o.r) ? o.r[1] : 0) + Math.sin(u0 * 1.4 + (o.p ? o.p[0] : 0)) * o.spin;
        if (o.spinZ) L.obj.rotation.z = u0 * o.spinZ;
        if (u.sector) { const f = Math.max(0.0001, u.frac.v); u.sector.geometry.dispose(); u.sector.geometry = new THREE.CircleGeometry(1.08, 64, Math.PI / 2 - Math.PI * 2 * f, Math.PI * 2 * f); }
        if (u.stripes && o.run) u.stripes.forEach((st, i) => { st.position.x = -u.len / 2 + 0.3 + ((i * 0.6 + u0 * o.run) % (u.len - 0.6)); });
        if (o.ring && t >= o.ring[0] && t < o.ring[1]) L.obj.rotation.z = Math.sin((t - o.ring[0]) * 60) * 0.08;
      }
      s.cam.lookAt(s.look);
      const vx = s.full ? 0 : PANEL_X, vw = s.full ? W : W - PANEL_X;
      renderer.setViewport(vx, 0, vw, H);
      renderer.setScissor(vx, 0, vw, H);
      renderer.setScissorTest(true);
      renderer.render(scene, s.cam);
    }
  }
  window.addEventListener("hf-seek", (e) => {
    const t = e.detail && typeof e.detail.time === "number" ? e.detail.time : tl.time();
    if (Math.abs(tl.time() - t) > 1e-4) tl.time(t, false);
    renderAt(t);
  });
  tl.eventCallback("onUpdate", () => renderAt(tl.time()));
  renderAt(tl.time());
}
