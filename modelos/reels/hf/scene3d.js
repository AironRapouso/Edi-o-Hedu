// REELS 3 — 3D layer (three.js r181, vendored in assets/three).
// Everything here is a pure function of the GSAP timeline time: HyperFrames seeks the timeline and
// dispatches "hf-seek"; we render exactly that frame. No requestAnimationFrame, no wall clock, no random.
// One small world for the whole story: the gold pawn is VOCÊ, the robot is the FERRAMENTA, the sheet is the PLANILHA.
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { FontLoader } from "three/addons/loaders/FontLoader.js";
import { TextGeometry } from "three/addons/geometries/TextGeometry.js";

const ready = window.__scene3dReady || (() => {});
const problems = [];
try {
  await build();
} catch (err) {
  problems.push(err);
}
if (problems.length) {
  const d = document.createElement("div");
  d.id = "err3d";
  d.style.cssText = "position:absolute;left:0;top:0;z-index:99;width:1080px;background:#c00;color:#fff;font:20px monospace;white-space:pre-wrap;padding:12px";
  d.textContent = problems.map((e) => "scene3d: " + (e && e.stack ? e.stack : e)).join("\n\n");
  document.getElementById("root").appendChild(d);
  problems.forEach((e) => console.error("scene3d", e));
}
ready();

async function build() {
  const tl = window.tl;
  const D = window.REEL;
  const T = D.T;
  const S = (i) => T.S[i];
  const E = (i) => T.E[i];
  const W = 1080, H = 1920, SEAM = 712;
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
  renderer.toneMappingExposure = 1.0;
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
  Object.assign(key.shadow.camera, { left: -10, right: 10, top: 10, bottom: -10, near: 1, far: 45 });
  key.shadow.bias = -0.0005;
  key.shadow.normalBias = 0.03;
  const rim = new THREE.DirectionalLight(0xbfd8ff, 0.85);       // cool back light: an edge of light on every object
  rim.position.set(-8, 7, -7);
  scene.add(key, key.target, rim, new THREE.HemisphereLight(0xffffff, 0xdfe6f5, 0.55));

  const mat = (hex, o = {}) => new THREE.MeshPhysicalMaterial({ color: hex, roughness: o.r ?? 0.42, metalness: o.m ?? 0, clearcoat: o.cc ?? 0.5, clearcoatRoughness: 0.3 });
  const basic = (hex, o = 1) => new THREE.MeshBasicMaterial({ color: hex, transparent: o < 1, opacity: o, toneMapped: false });
  const C = { gold: 0xf4b04a, navy: 0x0b2266, ink: 0x05103a, blue: 0x0457e7, sky: 0x5ca2ee, white: 0xf8f6f1, red: 0xe5484d, grey: 0xc9c6bd };
  const M = {
    gold: mat(C.gold, { r: 0.28, m: 0.35, cc: 0.9 }),
    goldD: mat(0xdc9a36, { r: 0.3, m: 0.4, cc: 0.9 }),
    navy: mat(C.navy, { r: 0.4 }),
    ink: mat(C.ink, { r: 0.3, cc: 0.9 }),
    blue: mat(C.blue, { r: 0.35 }),
    sky: mat(C.sky, { r: 0.4 }),
    white: mat(C.white, { r: 0.55, cc: 0.25 }),
    kraft: mat(0xdcae72, { r: 0.75, cc: 0.05 }),
    kraftD: mat(0xb9864a, { r: 0.75, cc: 0.05 }),
    red: mat(C.red, { r: 0.4 }),
    cell: mat(0x9aa3b8, { r: 0.5, cc: 0.2 }),
    plate: mat(0x071447, { r: 0.7, cc: 0 }),
  };
  M.plate.envMapIntensity = 0.35;
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
    g.translate(-(b.min.x + b.max.x) / 2, -b.min.y, -(b.min.z + b.max.z) / 2);   // centred in x/z, standing on y = 0
    return sh(new THREE.Mesh(g, material));
  }
  function textPlane(w, h, draw, ppu = 240) {
    const c = document.createElement("canvas");
    c.width = Math.round(w * ppu);
    c.height = Math.round(h * ppu);
    draw(c.getContext("2d"), c.width, c.height);
    const tex = new THREE.CanvasTexture(c);
    tex.colorSpace = THREE.SRGBColorSpace;
    tex.anisotropy = 8;
    return new THREE.Mesh(new THREE.PlaneGeometry(w, h), new THREE.MeshBasicMaterial({ map: tex, transparent: true, toneMapped: false }));
  }
  const bebas = (x, px, ls = 0.03) => { x.font = `400 ${Math.round(px)}px "Bebas Neue"`; x.letterSpacing = `${Math.round(px * ls)}px`; };
  const label = (txt, color, fs = 0.62, ty = 0.56) => (x, w, h) => {
    x.fillStyle = color;
    bebas(x, h * fs, 0.05);
    x.textAlign = "center";
    x.textBaseline = "middle";
    x.fillText(txt, w / 2, h * ty);
  };
  function plate(w, h, d, bodyMat, txt, fg = "#F6F6F8", fs = 0.62) {
    const g = new THREE.Group();
    g.add(rbox(w, h, d, h * 0.28, bodyMat));
    const face = textPlane(w, h, label(txt, fg, fs));
    face.position.z = d / 2 + 0.006;
    g.add(face);
    return g;
  }
  function star(r) {
    const s = new THREE.Shape();
    for (let i = 0; i < 8; i++) {
      const a = (i * Math.PI) / 4, rad = i % 2 ? r * 0.2 : r;
      if (i) s.lineTo(Math.cos(a) * rad, Math.sin(a) * rad); else s.moveTo(Math.cos(a) * rad, Math.sin(a) * rad);
    }
    s.closePath();
    return new THREE.Mesh(new THREE.ExtrudeGeometry(s, { depth: r * 0.1, bevelEnabled: false }), new THREE.MeshBasicMaterial({ color: 0xffd98a, toneMapped: false }));
  }
  function frame(w, h, t, material, d = 0.06) {          // a rectangle outline made of four bars (children 0..3: top, bottom, left, right)
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
    const eyeM = new THREE.MeshBasicMaterial({ color: 0x8fd8ff, toneMapped: false });
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
  function robot() {                                      // the FERRAMENTA
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
    const bar = rbox(0.5, 0.09, 0.03, 0.03, M.sky);
    bar.position.set(-0.2, 1.48, 0.705);
    const bar2 = rbox(0.34, 0.09, 0.03, 0.03, M.sky);
    bar2.position.set(-0.28, 1.31, 0.705);
    g.add(rh, neck, body, chest, lamp, bar, bar2);
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
  function pawn(material) {                               // VOCÊ: a faceless gold game piece
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
  function coinStack(parent, x, z, n, r, when) {
    const out = [];
    for (let k = 0; k < n; k++) {
      const c = cyl(r, r, 0.17, k % 2 ? M.goldD : M.gold, 56);
      const y = 0.085 + k * 0.178;
      c.position.set(x + (((k * 37) % 7) - 3) * 0.012, y, z + (((k * 53) % 5) - 2) * 0.012);
      parent.add(c);
      const t = when(k);
      tl.fromTo(c.scale, { x: 0.001, y: 0.001, z: 0.001 }, { x: 1, y: 1, z: 1, duration: 0.1, ease: "power2.out" }, t);
      tl.fromTo(c.position, { y: y + 1.7 }, { y, duration: 0.24, ease: "bounce.out" }, t);
      out.push({ c, y, t });
    }
    return out;
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
  function parcel() {                                     // one of "as suas entregas"
    const g = new THREE.Group();
    g.add(rbox(0.96, 0.76, 0.8, 0.06, M.kraft), rbox(0.2, 0.775, 0.815, 0.02, M.kraftD));
    const ck = textPlane(0.44, 0.44, (x, w, h) => {
      x.fillStyle = "#0457E7";
      x.beginPath(); x.arc(w / 2, h / 2, w * 0.46, 0, 7); x.fill();
      x.strokeStyle = "#FFFFFF";
      x.lineWidth = w * 0.13;
      x.lineCap = "round";
      x.lineJoin = "round";
      x.beginPath(); x.moveTo(w * 0.27, h * 0.52); x.lineTo(w * 0.44, h * 0.68); x.lineTo(w * 0.74, h * 0.34); x.stroke();
    });
    ck.position.set(0.27, 0.02, 0.412);
    g.add(ck);
    return g;
  }
  function badgeX(r) {
    const g = new THREE.Group();
    const disc = cyl(r, r, 0.14, M.red, 56);
    disc.rotation.x = Math.PI / 2;
    g.add(disc);
    [-1, 1].forEach((sg) => { const b = rbox(r * 1.15, r * 0.24, 0.06, 0.03, M.white); b.rotation.z = (sg * Math.PI) / 4; b.position.z = 0.09; g.add(b); });
    return g;
  }
  function half() {                                       // "metade": a gold 1/2
    const g = new THREE.Group();
    const one = text3d("1", 1.25, 0.42, M.gold);
    one.position.set(-0.64, 1.38, 0);
    const two = text3d("2", 1.25, 0.42, M.gold);
    two.position.set(0.6, 0, 0);
    const bar = rbox(0.24, 2.75, 0.36, 0.1, M.gold);
    bar.position.set(0, 1.32, 0);
    bar.rotation.z = -0.6;
    g.add(one, two, bar);
    return g;
  }
  function devil() {                                      // "maldade"
    const g = new THREE.Group();
    g.add(sph(1.2, M.ink));
    [-1, 1].forEach((sg) => {
      const horn = sh(new THREE.Mesh(new THREE.ConeGeometry(0.3, 0.86, 28), M.red));
      horn.position.set(sg * 0.66, 1.12, 0);
      horn.rotation.z = -sg * 0.5;
      const eye = new THREE.Mesh(new THREE.CircleGeometry(0.21, 32), GLOW);
      eye.scale.set(1.5, 0.6, 1);
      eye.position.set(sg * 0.45, 0.2, 1.13);
      eye.rotation.z = sg * 0.42;
      g.add(horn, eye);
    });
    const grin = new THREE.Mesh(new THREE.TorusGeometry(0.42, 0.05, 8, 32, Math.PI), GLOW);
    grin.rotation.z = Math.PI;
    grin.position.set(0, -0.22, 1.12);
    g.add(grin);
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
  function heartGeo() {
    const p = new THREE.Shape();
    p.moveTo(0, 0.55);
    p.bezierCurveTo(0, 0.85, -0.35, 1.05, -0.6, 1.05);
    p.bezierCurveTo(-1.0, 1.05, -1.1, 0.6, -1.1, 0.45);
    p.bezierCurveTo(-1.1, -0.1, -0.5, -0.55, 0, -1.0);
    p.bezierCurveTo(0.5, -0.55, 1.1, -0.1, 1.1, 0.45);
    p.bezierCurveTo(1.1, 0.6, 1.0, 1.05, 0.6, 1.05);
    p.bezierCurveTo(0.35, 1.05, 0, 0.85, 0, 0.55);
    const geo = new THREE.ExtrudeGeometry(p, { depth: 0.5, bevelEnabled: true, bevelThickness: 0.16, bevelSize: 0.14, bevelSegments: 6, curveSegments: 28 });
    geo.translate(0, 0, -0.25);
    return geo;
  }
  function gift() {                                       // "o que você entrega"
    const g = new THREE.Group();
    g.add(rbox(1.5, 1.5, 1.5, 0.1, M.gold), rbox(0.34, 1.53, 1.53, 0.03, M.navy), rbox(1.53, 0.34, 1.53, 0.03, M.navy));
    [-1, 1].forEach((sg) => {
      const loop = sh(new THREE.Mesh(new THREE.TorusGeometry(0.27, 0.085, 14, 36), M.navy));
      loop.position.set(sg * 0.3, 0.98, 0);
      loop.rotation.z = sg * 0.5;
      loop.scale.set(1, 0.72, 1);
      g.add(loop);
    });
    const knot = sph(0.14, M.navy);
    knot.position.set(0, 0.82, 0);
    g.add(knot);
    return g;
  }
  function addFloor(g, y = 0, o = 0.2) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(70, 40), new THREE.ShadowMaterial({ opacity: o }));
    m.rotation.x = -Math.PI / 2;
    m.position.y = y;
    m.receiveShadow = true;
    g.add(m);
  }
  function addWall(g, z, o = 0.13) {
    const m = new THREE.Mesh(new THREE.PlaneGeometry(70, 50), new THREE.ShadowMaterial({ opacity: o }));
    m.position.z = z;
    m.receiveShadow = true;
    g.add(m);
  }

  // ------------------------------------------------------------------ flat drawings (canvas textures)
  const rr = (x, a, b, w, h, r) => { x.beginPath(); x.roundRect(a, b, w, h, r); };
  const sheetIcon = (x, cx, cy, sz) => {                   // a tiny spreadsheet glyph
    x.fillStyle = "#F6F6F8";
    rr(x, cx - sz / 2, cy - sz / 2, sz, sz, sz * 0.16); x.fill();
    x.strokeStyle = "#0B2266";
    x.lineWidth = sz * 0.07;
    x.beginPath();
    [0.36, 0.64].forEach((f) => { x.moveTo(cx - sz / 2, cy - sz / 2 + sz * f); x.lineTo(cx + sz / 2, cy - sz / 2 + sz * f); });
    x.moveTo(cx - sz / 2 + sz * 0.38, cy - sz / 2); x.lineTo(cx - sz / 2 + sz * 0.38, cy + sz / 2);
    x.stroke();
  };
  const drawRoom = (x, w, h) => {                          // what is behind the meeting-room door
    const gr = x.createLinearGradient(0, 0, 0, h);
    gr.addColorStop(0, "#FFF7DF"); gr.addColorStop(0.5, "#FBE3A4"); gr.addColorStop(1, "#F2BE5C");
    x.fillStyle = gr;
    x.fillRect(0, 0, w, h);
    x.fillStyle = "#0B2266";
    rr(x, w * 0.17, h * 0.085, w * 0.66, h * 0.115, w * 0.03); x.fill();
    [[0.25, 0.035, "#5CA2EE"], [0.38, 0.055, "#5CA2EE"], [0.51, 0.075, "#5CA2EE"], [0.64, 0.04, "#F4B04A"]].forEach(([c, bh, col]) => {
      x.fillStyle = col;
      x.fillRect(w * c, h * (0.185 - bh), w * 0.09, h * bh);
    });
    x.fillStyle = "#0B2266";
    [[0.22, 0.29], [0.5, 0.275], [0.78, 0.29]].forEach(([cx, cy]) => {
      x.beginPath(); x.arc(w * cx, h * cy, w * 0.085, 0, 7); x.fill();
      x.beginPath(); x.ellipse(w * cx, h * (cy + 0.09), w * 0.135, h * 0.045, 0, Math.PI, 0); x.fill();
      x.fillRect(w * (cx - 0.135), h * (cy + 0.089), w * 0.27, h * 0.06);
    });
    x.fillStyle = "#071447";
    x.fillRect(0, h * 0.39, w, h * 0.028);
  };
  const drawDots = (x, w, h) => {
    x.fillStyle = "#0B2266";
    [0.25, 0.5, 0.75].forEach((c) => { x.beginPath(); x.arc(w * c, h * 0.5, h * 0.14, 0, 7); x.fill(); });
  };
  const drawYou = (x, w, h) => {                           // they are talking about the gold pawn
    x.fillStyle = "#E79A2B";
    x.beginPath(); x.arc(w * 0.5, h * 0.3, h * 0.2, 0, 7); x.fill();
    x.beginPath(); x.moveTo(w * 0.5 - h * 0.34, h * 0.95); x.lineTo(w * 0.5 - h * 0.17, h * 0.52); x.lineTo(w * 0.5 + h * 0.17, h * 0.52); x.lineTo(w * 0.5 + h * 0.34, h * 0.95); x.closePath(); x.fill();
  };
  const drawSpill = (x, w, h) => {                         // warm light falling out of the open door
    const gr = x.createLinearGradient(0, 0, 0, h);
    gr.addColorStop(0, "rgba(249,205,120,.95)"); gr.addColorStop(1, "rgba(249,205,120,0)");
    x.fillStyle = gr;
    x.beginPath(); x.moveTo(w * 0.24, 0); x.lineTo(w * 0.76, 0); x.lineTo(w, h); x.lineTo(0, h); x.closePath(); x.fill();
  };
  const drawPanel = (x, w, h) => {                         // the room display beside the door: what the meeting is about
    x.fillStyle = "#071447";
    rr(x, 0, 0, w, h, h * 0.09); x.fill();
    x.textBaseline = "middle";
    x.textAlign = "left";
    x.fillStyle = "#9CC4F5";
    x.font = `700 ${Math.round(h * 0.1)}px "Mono"`;
    x.letterSpacing = `${Math.round(h * 0.022)}px`;
    x.fillText("EM REUNIÃO", w * 0.17, h * 0.17);
    x.strokeStyle = "rgba(156,196,245,.35)";
    x.lineWidth = h * 0.008;
    x.beginPath(); x.moveTo(w * 0.07, h * 0.3); x.lineTo(w * 0.93, h * 0.3); x.stroke();
    bebas(x, h * 0.31, 0.04);
    x.fillStyle = "#F6F6F8";
    x.fillText("VOCÊ", w * 0.07, h * 0.51);
    const vw = x.measureText("VOCÊ").width;
    x.fillStyle = "#F4B04A";
    x.fillText("X", w * 0.07 + vw + h * 0.08, h * 0.51);
    x.fillStyle = "#F6F6F8";
    x.fillText("FERRAMENTA", w * 0.07, h * 0.81);
  };
  const drawCost = (x, w, h) => {                          // the sheet of the meeting: two rows, VOCÊ and FERRAMENTA
    rr(x, 0, 0, w, h, h * 0.045); x.clip();
    x.fillStyle = "#FFFFFF";
    x.fillRect(0, 0, w, h);
    const hb = h * 0.205, rowH = (h - hb) / 2, cx = w * 0.462;
    x.fillStyle = "#0B2266";
    x.fillRect(0, 0, w, hb);
    sheetIcon(x, w * 0.06, hb * 0.5, hb * 0.5);
    x.fillStyle = "#F6F6F8";
    bebas(x, hb * 0.62, 0.05);
    x.textAlign = "left";
    x.textBaseline = "middle";
    x.fillText("CUSTO POR MÊS", w * 0.105, hb * 0.55);
    x.fillStyle = "#F4F6FA";
    x.fillRect(0, hb, cx, h - hb);
    x.strokeStyle = "#CDD4E2";
    x.lineWidth = h * 0.006;
    x.beginPath(); x.moveTo(0, hb + rowH); x.lineTo(w, hb + rowH); x.moveTo(cx, hb); x.lineTo(cx, h); x.stroke();
    x.fillStyle = "#0B2266";
    x.textAlign = "center";
    bebas(x, rowH * 0.66, 0.04);
    x.fillText("VOCÊ", cx / 2, hb + rowH * 0.55);
    bebas(x, rowH * 0.5, 0.03);
    x.fillText("FERRAMENTA", cx / 2, hb + rowH * 1.55);
    x.textAlign = "left";
    bebas(x, rowH * 0.5, 0.02);
    x.fillText("R$", cx + w * 0.035, hb + rowH * 0.55);
    x.fillText("R$", cx + w * 0.035, hb + rowH * 1.55);
    x.fillStyle = "#B4BCCD";
    bebas(x, rowH * 0.62, 0.02);
    x.fillText("?", cx + w * 0.16, hb + rowH * 1.55);
  };
  const GRID = { w: 5.0, h: 3.7, head: 0.55, letters: 0.3, nums: 0.38, cols: 4, rows: 4 };
  const drawGrid = (G, title) => (x, w, h) => {            // an empty spreadsheet (the cells get their bars in 3D)
    const ux = w / G.w, uy = h / G.h;
    rr(x, 0, 0, w, h, h * 0.03); x.clip();
    x.fillStyle = "#FFFFFF";
    x.fillRect(0, 0, w, h);
    x.fillStyle = "#0B2266";
    x.fillRect(0, 0, w, G.head * uy);
    sheetIcon(x, G.head * 0.55 * ux, G.head * 0.5 * uy, G.head * 0.52 * uy);
    x.fillStyle = "#F6F6F8";
    bebas(x, G.head * 0.64 * uy, 0.06);
    x.textAlign = "left";
    x.textBaseline = "middle";
    x.fillText(title, G.head * 1.05 * ux, G.head * 0.55 * uy);
    x.fillStyle = "#EEF1F6";
    x.fillRect(0, G.head * uy, w, G.letters * uy);
    x.fillRect(0, G.head * uy, G.nums * ux, h);
    const cw = (G.w - G.nums) / G.cols, rh = (G.h - G.head - G.letters) / G.rows;
    x.strokeStyle = "#CDD4E2";
    x.lineWidth = Math.max(2, h * 0.004);
    x.beginPath();
    for (let c = 0; c <= G.cols; c++) { x.moveTo((G.nums + c * cw) * ux, G.head * uy); x.lineTo((G.nums + c * cw) * ux, h); }
    for (let r = 0; r <= G.rows; r++) { x.moveTo(0, (G.head + G.letters + r * rh) * uy); x.lineTo(w, (G.head + G.letters + r * rh) * uy); }
    x.stroke();
    x.fillStyle = "#7C879F";
    x.textAlign = "center";
    x.font = `700 ${Math.round(G.letters * 0.62 * uy)}px "Inter"`;
    for (let c = 0; c < G.cols; c++) x.fillText("ABCDEF"[c], (G.nums + (c + 0.5) * cw) * ux, (G.head + G.letters * 0.54) * uy);
    for (let r = 0; r < G.rows; r++) x.fillText(String(r + 1), G.nums * 0.5 * ux, (G.head + G.letters + (r + 0.5) * rh) * uy);
  };
  const cellAt = (G, r, c) => {                            // centre of a cell in the sheet's own coordinates
    const cw = (G.w - G.nums) / G.cols, rh = (G.h - G.head - G.letters) / G.rows;
    return [-G.w / 2 + G.nums + (c + 0.5) * cw, G.h / 2 - G.head - G.letters - (r + 0.5) * rh, cw, rh];
  };
  const drawFormula = (x, w, h) => {
    x.fillStyle = "#0457E7";
    rr(x, h * 0.2, h * 0.2, h * 0.86, h * 0.6, h * 0.14); x.fill();
    x.fillStyle = "#FFFFFF";
    x.textAlign = "center";
    x.textBaseline = "middle";
    x.font = `700 ${Math.round(h * 0.36)}px "Mono"`;
    x.fillText("fx", h * 0.63, h * 0.52);
    x.fillStyle = "#0B2266";
    x.textAlign = "left";
    x.font = `700 ${Math.round(h * 0.47)}px "Mono"`;
    x.fillText("= SENTIMENTO", h * 1.3, h * 0.53);
  };

  // ------------------------------------------------------------------ timeline helpers
  const pop = (o, t, d = 0.42, ease = "back.out(1.9)", to = 1) => tl.fromTo(o.scale, { x: 0.001, y: 0.001, z: 0.001 }, { x: to, y: to, z: to, duration: d, ease }, t);
  const hide = (o, t, d = 0.18) => tl.to(o.scale, { x: 0.001, y: 0.001, z: 0.001, duration: d, ease: "power2.in" }, t);
  const colorTo = (material, hex, t, d = 0.22) => { const c = new THREE.Color(hex); tl.to(material.color, { r: c.r, g: c.g, b: c.b, duration: d, ease: "power2.out" }, t); };
  function camTo(s, t, d, pos, look, ease = "power3.inOut") {
    tl.to(s.cam.position, { x: pos[0], y: pos[1], z: pos[2], duration: d, ease }, t);
    tl.to(s.look, { x: look[0], y: look[1], z: look[2], duration: d, ease }, t);
  }
  function sparkle(g, pts, t0, gap = 0.1, r = 0.3) {
    pts.forEach(([x, y, z], k) => {
      const st = star(r);
      st.position.set(x, y, z);
      g.add(st);
      const t = t0 + k * gap;
      tl.fromTo(st.scale, { x: 0.001, y: 0.001, z: 0.001 }, { x: 1, y: 1, z: 1, duration: 0.18, ease: "back.out(3)" }, t);
      tl.to(st.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.3, ease: "power2.in" }, t + 0.32);
      tl.fromTo(st.rotation, { z: 0 }, { z: 1.2, duration: 0.62, ease: "none" }, t);
    });
  }

  // ------------------------------------------------------------------ scenes (one visible at a time)
  const SC = [];
  const FS1 = T.fs1, C3 = T.sc3, C4 = T.sc4, FS2 = T.fs2, C5 = T.sc5;
  function addScene(name, t0, t1, full, make) {
    const g = new THREE.Group();
    g.visible = false;
    scene.add(g);
    const s = { name, t0, t1, full, g, cam: new THREE.PerspectiveCamera(30, full ? W / H : W / SEAM, 0.1, 120), look: new THREE.Vector3(), update: null };
    SC.push(s);
    try { make(s, g); } catch (err) { problems.push(err); }
  }

  // ===== 1 · HOOK (split): "Sabe aquela reunião para a qual você não foi chamado?"
  // The meeting-room door slams on frame 0. The room display says what it is about (the cover text of the script:
  // VOCÊ X FERRAMENTA). They are inside, talking; the gold pawn (VOCÊ) is left outside.
  addScene("door", 0, FS1, false, (s, g) => {
    addFloor(g, 0);
    addWall(g, -0.62, 0.12);
    const DX = -1.9;
    [-1.29, 1.29].forEach((x) => { const j = rbox(0.26, 4.3, 0.5, 0.06, M.navy); j.position.set(DX + x, 2.15, -0.3); g.add(j); });
    const lintel = rbox(2.84, 0.26, 0.5, 0.06, M.navy);
    lintel.position.set(DX, 4.31, -0.3);
    g.add(lintel);
    const room = textPlane(2.32, 4.18, drawRoom, 200);
    room.position.set(DX, 2.09, -0.5);
    g.add(room);
    const spill = textPlane(2.9, 3.4, drawSpill, 60);
    spill.rotation.x = -Math.PI / 2;
    spill.position.set(DX + 0.2, 0.012, 1.75);
    g.add(spill);
    tl.fromTo(spill.material, { opacity: 0.8 }, { opacity: 0, duration: 0.26, ease: "power2.in" }, 0);

    // the room display on the wall: EM REUNIÃO · VOCÊ X FERRAMENTA
    const disp = new THREE.Group();
    disp.add(rbox(2.56, 1.72, 0.14, 0.14, M.ink));
    const dface = textPlane(2.4, 1.56, drawPanel);
    dface.position.z = 0.074;
    disp.add(dface);
    const dot = new THREE.Mesh(new THREE.CircleGeometry(0.075, 28), basic(0xff5a5f));
    dot.position.set(-0.96, 0.515, 0.08);
    disp.add(dot);
    disp.position.set(0.95, 3.0, -0.48);
    g.add(disp);
    tl.fromTo(disp.scale, { x: 0.7, y: 0.7, z: 0.7 }, { x: 1, y: 1, z: 1, duration: 0.42, ease: "back.out(2.4)" }, 0);

    // they are talking in there: two little bubbles behind the glass
    const bubbles = [[-0.42, 3.44, drawDots], [0.36, 3.2, drawYou]].map(([x, y, draw], k) => {
      const b = new THREE.Group();
      b.add(rbox(0.72, 0.46, 0.08, 0.16, M.white));
      const f = textPlane(0.6, 0.36, draw);
      f.position.z = 0.046;
      b.add(f);
      b.position.set(DX + x, y, -0.2);
      g.add(b);
      pop(b, 0.42 + k * 0.4, 0.26, "back.out(2.2)");
      hide(b, S(7) - 0.12 + k * 0.05, 0.12);
      return { b, y, k };
    });

    // the door: hinged on the left, swings shut towards the camera
    const door = new THREE.Group();
    door.position.set(DX - 1.15, 0, 0);
    g.add(door);
    const part = (m, x, y, z = 0) => { m.position.set(1.15 + x, y, z); door.add(m); return m; };
    part(rbox(2.3, 2.5, 0.16, 0.05, M.blue), 0, 1.25);
    part(rbox(0.34, 1.7, 0.16, 0.05, M.blue), -0.98, 3.33);
    part(rbox(0.34, 1.7, 0.16, 0.05, M.blue), 0.98, 3.33);
    part(rbox(2.3, 0.32, 0.16, 0.05, M.blue), 0, 4.02);
    part(new THREE.Mesh(new THREE.PlaneGeometry(1.64, 1.38), basic(0xcfe8ff, 0.2)), 0, 3.19, 0.0);
    const sign = part(plate(1.9, 0.62, 0.1, M.plate, "REUNIÃO", "#F6F6F8", 0.72), 0, 1.72, 0.13);
    part(sph(0.14, M.gold), 0.9, 1.02, 0.17);
    tl.fromTo(door.rotation, { y: -1.0 }, { y: 0, duration: 0.26, ease: "power2.in" }, 0);
    tl.fromTo(door.rotation, { y: 0 }, { y: -0.04, duration: 0.05, yoyo: true, repeat: 1, ease: "sine.inOut", ...IR }, 0.26);
    sparkle(g, [[DX + 1.5, 3.55, 0.5], [DX + 1.62, 2.3, 0.5], [DX + 1.5, 1.0, 0.5]], 0.25, 0.03, 0.24);   // the slam
    tl.fromTo(sign.scale, { x: 1, y: 1, z: 1 }, { x: 1.14, y: 1.14, z: 1.14, duration: 0.13, yoyo: true, repeat: 1, ease: "power2.out", ...IR }, S(2) + 0.02);

    // VOCÊ, outside
    const PX = 3.3;
    const you = pawn(M.gold);
    you.position.set(PX, 0, 0.35);
    g.add(you);
    pop(you, S(6) - 0.06, 0.4, "back.out(1.9)", 0.95);
    const ly = plate(1.6, 0.6, 0.14, M.plate, "VOCÊ", "#F6F6F8", 0.74);
    ly.position.set(PX, 0.33, 1.6);
    ly.rotation.x = -0.42;
    g.add(ly);
    pop(ly, S(6) + 0.06);
    const no = badgeX(0.46);                               // "não": no entry
    no.position.set(DX + 1.02, 4.0, 0.34);
    g.add(no);
    pop(no, S(7) - 0.03, 0.26, "back.out(2.6)");
    tl.fromTo(no.rotation, { z: -0.7 }, { z: 0, duration: 0.32, ease: "back.out(2)" }, S(7) - 0.03);
    tl.fromTo(door.rotation, { y: 0 }, { y: -0.025, duration: 0.04, yoyo: true, repeat: 3, ease: "sine.inOut", ...IR }, S(7));
    const qm = text3d("?", 0.95, 0.3, M.blue);             // "...chamado?"
    qm.position.set(PX + 1.0, 2.75, 0.4);
    qm.rotation.z = -0.2;
    g.add(qm);
    pop(qm, S(9) + 0.02, 0.34, "back.out(2.6)");
    tl.to(you.rotation, { z: -0.1, duration: 0.3, ease: "power2.out" }, S(9) + 0.02);

    s.cam.position.set(-0.6, 2.78, 9.7);
    s.look.set(-0.8, 2.62, 0);
    camTo(s, 0, S(6) - 0.22, [-0.4, 2.8, 10.1], [-0.72, 2.6, 0], "sine.out");
    camTo(s, S(6) - 0.22, 0.5, [0.8, 2.95, 13.0], [0.62, 2.45, 0]);
    camTo(s, S(9) + 0.2, FS1 - (S(9) + 0.2), [DX, 3.12, 7.6], [DX, 3.08, 0], "power2.in");   // dive into the meeting
    s.update = (t) => {
      const u = t - 0.26;
      g.position.x = u > 0 && u < 0.45 ? Math.sin(u * 95) * 0.05 * Math.exp(-u / 0.07) : 0;       // the slam shakes the wall
      bubbles.forEach((o) => { o.b.position.y = o.y + Math.sin(t * 5 + o.k * 2) * 0.02; });
      qm.rotation.y = Math.sin(t * 2.4) * 0.35;
      dot.scale.setScalar(Math.sin(t * 9) > 0 ? 1 : 0.55);
    };
  });

  // ===== 2 · FULL SCREEN: "Pode ter sido sobre o quanto você custa por mês,"
  addScene("cost", FS1, C3, true, (s, g) => {
    addFloor(g, 0);
    addWall(g, -0.6, 0.08);
    s.cam.position.set(0, 3.2, 20.6);
    s.look.set(0, 3.0, 0);
    camTo(s, FS1, C3 - FS1, [0, 3.2, 19.7], [0, 3.0, 0], "sine.out");

    const card = new THREE.Group();
    card.position.set(0, 6.05, 0);
    g.add(card);
    card.add(rbox(5.2, 2.5, 0.14, 0.12, M.white));
    const face = textPlane(5.16, 2.46, drawCost);
    face.position.z = 0.075;
    face.renderOrder = 1;
    card.add(face);
    tl.fromTo(card.position, { y: 9.3 }, { y: 6.05, duration: 0.34, ease: "back.out(1.3)" }, FS1 - 0.02);   // already entering on the first frame
    tl.fromTo(card.rotation, { x: 0.55 }, { x: -0.04, duration: 0.5, ease: "power3.out" }, FS1);
    // the row that matters: VOCÊ lights up, the cursor lands on its cost, the gold bar grows while the coins fall
    const hl = new THREE.Mesh(new THREE.PlaneGeometry(2.36, 0.96), new THREE.MeshBasicMaterial({ color: 0xf4b04a, transparent: true, opacity: 0, depthWrite: false, toneMapped: false }));
    hl.position.set(-1.39, 0.25, 0.082);
    hl.renderOrder = 2;
    card.add(hl);
    tl.to(hl.material, { opacity: 0.4, duration: 0.16, ease: "power2.out" }, S(16) - 0.03);
    const sel = frame(2.74, 0.94, 0.075, BLUE);
    sel.position.set(1.2, 0.25, 0.1);
    card.add(sel);
    pop(sel, S(15) - 0.04, 0.2, "back.out(2)");
    const barG = new THREE.Group();
    barG.position.set(0.8, 0.25, 0.1);
    const bar = rbox(1.6, 0.44, 0.1, 0.1, M.gold);
    bar.position.x = 0.8;
    barG.add(bar);
    card.add(barG);
    tl.fromTo(barG.scale, { x: 0.001 }, { x: 1, duration: 0.62, ease: "power2.out" }, S(17) + 0.02);

    // VOCÊ comes up on a pedestal, like something with a price
    const youG = new THREE.Group();
    const ped = cyl(1.12, 1.18, 0.28, M.navy, 64);
    ped.position.y = 0.14;
    const you = pawn(M.gold);
    you.position.y = 0.28;
    you.scale.setScalar(0.92);
    youG.add(ped, you);
    youG.position.set(-1.0, 0, 0.2);
    g.add(youG);
    tl.fromTo(youG.position, { y: -7 }, { y: 0, duration: 0.5, ease: "back.out(1.25)" }, FS1 + 0.2);       // over the face: after the paper cover
    tl.fromTo(you.position, { y: 0.28 }, { y: 0.8, duration: 0.13, yoyo: true, repeat: 1, ease: "power2.out", ...IR }, S(16) - 0.04);   // "você": that is you
    coinStack(g, 1.28, 0.45, 8, 0.56, (k) => S(17) + 0.06 + k * 0.085);
    const cal = calendar("MÊS");                           // "...por mês"
    cal.position.set(1.32, 3.02, 0.2);
    cal.rotation.x = 0.06;
    g.add(cal);
    pop(cal, S(18) - 0.04, 0.32, "back.out(2)", 0.5);
    tl.fromTo(cal.rotation, { x: 0.06 }, { x: 0.55, duration: 0.14, yoyo: true, repeat: 1, ease: "power2.inOut", ...IR }, S(19) + 0.04);
    s.update = (t) => {
      const u = t - FS1;
      card.rotation.z = Math.sin(u * 1.5) * 0.008;
      cal.rotation.z = Math.sin(u * 1.9) * 0.02;
      you.rotation.y = Math.sin(u * 1.2) * 0.25;
    };
  });

  // ===== 3 · split: "e quanto custa uma ferramenta / que faz as suas entregas / pela metade do preço."
  addScene("tool", C3, C4, false, (s, g) => {
    addFloor(g, 0);
    addWall(g, -1.6);
    const RX = 1.7;
    const bot = robot();
    bot.scale.setScalar(0.9);
    bot.position.set(RX, 0, 0);
    g.add(bot);
    const { head, arms, eyeM } = bot.userData;
    tl.fromTo(bot.position, { y: -6.5 }, { y: 0, duration: 0.5, ease: "back.out(0.55)" }, C3 - 0.14);      // already coming up at the cut: never an empty panel
    const dim = new THREE.Color(0x24345f), lit = new THREE.Color(0x8fd8ff);
    tl.fromTo(eyeM.color, { r: dim.r, g: dim.g, b: dim.b }, { r: lit.r, g: lit.g, b: lit.b, duration: 0.16, ease: "power2.out" }, C3 + 0.36);
    const tag = plate(1.5, 0.66, 0.12, M.plate, "R$ ?", "#F4B04A", 0.74);                      // its price, still a question
    tag.position.set(RX + 1.6, 2.55, 0.55);
    tag.rotation.z = -0.08;
    g.add(tag);
    pop(tag, S(22) + 0.04, 0.34, "back.out(2.4)");
    hide(tag, S(30) - 0.2, 0.14);
    const lt = plate(2.9, 0.62, 0.14, M.plate, "FERRAMENTA", "#F6F6F8", 0.72);
    lt.position.set(RX, 0.33, 1.4);
    lt.rotation.x = -0.42;
    g.add(lt);
    pop(lt, S(24) - 0.04);
    tl.to(head.rotation, { z: 0.14, duration: 0.25, ease: "back.out(2)" }, S(24));
    tl.to(head.rotation, { z: 0, duration: 0.2, ease: "power2.out" }, S(25) - 0.1);

    // "que faz as suas entregas": parcels fly out of it and pile up, each one checked
    const BX = [[4.8, 0.39], [5.8, 0.39], [5.3, 1.17], [5.3, 1.95]];
    const bt = [S(26) - 0.02, S(27), S(28) + 0.02, S(29) + 0.14];
    BX.forEach(([x, y], k) => {
      const b = parcel();
      g.add(b);
      const t = bt[k];
      tl.fromTo(b.scale, { x: 0.001, y: 0.001, z: 0.001 }, { x: 1, y: 1, z: 1, duration: 0.14, ease: "power2.out" }, t);
      tl.fromTo(b.position, { x: RX + 0.9, z: 0.8 }, { x, z: 0.25, duration: 0.34, ease: "none" }, t);
      tl.fromTo(b.position, { y: 1.5 }, { y: y + 1.5, duration: 0.17, ease: "power2.out" }, t);
      tl.to(b.position, { y, duration: 0.17, ease: "power2.in" }, t + 0.17);
      tl.fromTo(b.rotation, { z: -1.3 }, { z: (k % 2 ? 1 : -1) * 0.04, duration: 0.34, ease: "power1.out" }, t);
      tl.fromTo(b.scale, { y: 0.78 }, { y: 1, duration: 0.2, ease: "back.out(3)", ...IR }, t + 0.34);
      tl.fromTo(arms[1].rotation, { x: 0 }, { x: -1.25, duration: 0.11, yoyo: true, repeat: 1, ease: "power2.out", ...IR }, t - 0.03);
    });
    const le = plate(2.3, 0.62, 0.14, M.plate, "ENTREGAS", "#F6F6F8", 0.72);
    le.position.set(5.3, 0.33, 1.45);
    le.rotation.x = -0.42;
    g.add(le);
    pop(le, S(29) + 0.06);

    // "pela metade do preço": the same coins for both, side by side ... and half of the tool's fly away
    const you = pawn(M.gold);
    you.position.set(-3.2, 0, 0);
    g.add(you);
    pop(you, S(30) - 0.04, 0.36, "back.out(1.9)", 0.95);
    const ly = plate(1.6, 0.62, 0.14, M.plate, "VOCÊ", "#F6F6F8", 0.74);
    ly.position.set(-3.2, 0.33, 1.4);
    ly.rotation.x = -0.42;
    g.add(ly);
    pop(ly, S(30) + 0.08);
    const when = (k) => S(30) + 0.1 + k * 0.05;
    coinStack(g, -1.55, 0.55, 8, 0.5, when);
    const cb = coinStack(g, -0.25, 0.55, 8, 0.5, when);
    const tm = S(31);
    cb.slice(4).forEach((o, j) => {
      const t = tm + 0.05 + j * 0.03;
      tl.to(o.c.position, { x: o.c.position.x + (j - 1.5) * 0.5, y: o.y + 1.5 + j * 0.2, duration: 0.3, ease: "power2.out" }, t);
      tl.to(o.c.rotation, { z: (j % 2 ? 1 : -1) * 1.4, duration: 0.3, ease: "none" }, t);
      tl.to(o.c.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.16, ease: "power2.in" }, t + 0.14);
    });
    const hf = half();                                      // floats above the two stacks
    hf.position.set(-0.9, 2.0, 0.6);
    g.add(hf);
    pop(hf, tm - 0.08, 0.34, "back.out(2.4)", 0.68);
    tl.fromTo(hf.position, { y: 2.65 }, { y: 2.0, duration: 0.34, ease: "bounce.out" }, tm - 0.08);
    sparkle(g, [[-2.05, 3.25, 0.9], [0.25, 3.1, 0.9], [-0.9, 3.72, 0.7]], S(33) + 0.02, 0.11, 0.28);
    tl.to(head.rotation, { z: -0.16, duration: 0.3, ease: "back.out(2)" }, tm + 0.12);

    s.cam.position.set(2.1, 2.55, 10.3);
    s.look.set(1.8, 2.05, 0);
    camTo(s, C3, S(25) - 0.14 - C3, [1.85, 2.55, 9.9], [1.8, 2.05, 0], "sine.out");
    camTo(s, S(25) - 0.14, 0.45, [3.75, 2.5, 10.7], [3.55, 2.0, 0]);
    camTo(s, S(30) - 0.16, 0.5, [-0.3, 2.9, 11.5], [-0.45, 2.25, 0]);
    camTo(s, S(30) + 0.34, C4 - (S(30) + 0.34), [-0.55, 2.85, 11.1], [-0.45, 2.25, 0], "sine.out");
    s.update = (t) => {
      const u = t - C3;
      tag.rotation.z = -0.08 + Math.sin(u * 3.1) * 0.06;
      hf.rotation.y = Math.sin(u * 1.6) * 0.3;
      arms[0].rotation.x = Math.sin(u * 2.2) * 0.12;
    };
  });

  // ===== 4 · split: "Não é maldade,"
  addScene("evil", C4, FS2, false, (s, g) => {
    addFloor(g, 0);
    addWall(g, -1.5);
    s.cam.position.set(0.5, 2.5, 10.7);
    s.look.set(0, 2.0, 0);
    camTo(s, C4, FS2 - C4, [0.15, 2.5, 10.0], [0, 2.0, 0], "sine.out");
    const dv = devil();
    dv.position.set(0, 1.7, 0);
    g.add(dv);
    pop(dv, C4 - 0.08, 0.3, "back.out(2.2)");
    tl.fromTo(dv.rotation, { z: -0.35 }, { z: 0, duration: 0.4, ease: "back.out(2)" }, C4 - 0.08);
    const no = nosign(1.5);                                 // "NÃO é..."
    no.position.set(0, 1.7, 1.4);
    g.add(no);
    const tn = S(36) - 0.06;
    pop(no, tn, 0.24, "back.out(2.4)");
    tl.fromTo(no.rotation, { z: 0.5 }, { z: 0, duration: 0.3, ease: "back.out(2)" }, tn);
    tl.to(dv.scale, { x: 0.84, y: 0.84, z: 0.84, duration: 0.2, ease: "power2.out" }, tn + 0.03);
    tl.fromTo(dv.rotation, { z: 0 }, { z: 0.09, duration: 0.05, yoyo: true, repeat: 5, ease: "sine.inOut", ...IR }, tn + 0.03);
    s.update = (t) => { dv.position.y = 1.7 + Math.abs(Math.sin((t - C4) * 7)) * 0.1 * Math.max(0, 1 - (t - C4) / 0.5); };
  });

  // ===== 5 · FULL SCREEN: "é planilha, e planilha não tem sentimento."
  addScene("sheet", FS2, C5, true, (s, g) => {
    addFloor(g, 0);
    addWall(g, -1.0, 0.1);
    s.cam.position.set(0, 3.2, 20.6);
    s.look.set(0, 3.0, 0);
    camTo(s, FS2, C5 - FS2, [0, 3.2, 19.6], [0, 3.0, 0], "sine.inOut");
    const G = GRID;
    const SY = 1.98;
    const sheet = new THREE.Group();
    sheet.position.set(0, SY, 0);
    sheet.rotation.x = -0.1;
    g.add(sheet);
    sheet.add(rbox(G.w + 0.04, G.h + 0.04, 0.16, 0.12, M.white));
    const face = textPlane(G.w, G.h, drawGrid(G, "PLANILHA"));
    face.position.z = 0.085;
    sheet.add(face);
    // it drops from the top of the screen the moment he says it; it only crosses the seam once the paper has covered the face
    const t0 = FS2 - 0.02, tl0 = t0 + 0.34;
    tl.fromTo(sheet.position, { y: 8.9 }, { y: SY, duration: 0.34, ease: "power2.in" }, t0);
    tl.fromTo(sheet.scale, { x: 1.06, y: 0.9 }, { x: 1, y: 1, duration: 0.34, ease: "elastic.out(1.2, 0.4)", ...IR }, tl0);
    tl.fromTo(sheet.rotation, { z: -0.05 }, { z: 0, duration: 0.5, ease: "elastic.out(1.1, 0.4)" }, tl0);
    // the cells fill up one after the other: it just counts
    const EMPTY = [1, 2];
    let n = 0;
    for (let r = 0; r < G.rows; r++) {
      for (let c = 0; c < G.cols; c++) {
        if (r === EMPTY[0] && c === EMPTY[1]) continue;
        const [x, y, cw] = cellAt(G, r, c);
        const wd = cw * [0.62, 0.42, 0.7, 0.5, 0.56][(r * 3 + c * 2) % 5];
        const b = rbox(wd, 0.2, 0.07, 0.06, (r + c) % 4 === 1 ? M.sky : M.cell);
        b.position.set(x - cw * 0.4 + wd / 2, y, 0.12);
        sheet.add(b);
        pop(b, tl0 + 0.12 + n * 0.034, 0.2, "back.out(2)");
        n++;
      }
    }
    const [ex, ey, ecw, erh] = cellAt(G, EMPTY[0], EMPTY[1]);
    const sel = frame(ecw, erh, 0.075, BLUE);
    sel.position.set(ex, ey, 0.13);
    sheet.add(sel);
    pop(sel, S(39) - 0.03, 0.2, "back.out(2)");
    tl.fromTo(sel.scale, { x: 1, y: 1 }, { x: 1.12, y: 1.16, duration: 0.11, yoyo: true, repeat: 1, ease: "power2.out", ...IR }, S(40) + 0.2);

    // the formula bar: = SENTIMENTO ... the heart drops into the cell and comes out as a zero
    const FY = 5.3;
    const fx = new THREE.Group();
    fx.add(rbox(4.9, 0.86, 0.14, 0.22, M.white));
    const ft = textPlane(4.9, 0.86, drawFormula);
    ft.position.z = 0.076;
    fx.add(ft);
    fx.position.set(0, FY, 0);
    g.add(fx);
    pop(fx, S(39) - 0.06, 0.3, "back.out(1.9)");
    const res = plate(0.8, 0.6, 0.1, M.red, "0", "#FFFFFF", 0.8);
    res.position.set(1.92, FY, 0.14);
    g.add(res);

    const K = 0.56;
    const hm = mat(C.red, { r: 0.22, cc: 1.0 });
    const heart = sh(new THREE.Mesh(heartGeo(), hm));
    const hx = ex, hy = SY + ey + 0.05;
    heart.position.set(hx, 6.55, 0.95);
    g.add(heart);
    pop(heart, S(40) - 0.06, 0.3, "back.out(2.2)", K);
    [S(40) + 0.2, S(40) + 0.42].forEach((t) => tl.fromTo(heart.scale, { x: K, y: K, z: K }, { x: K * 1.16, y: K * 1.16, z: K * 1.16, duration: 0.07, yoyo: true, repeat: 1, ease: "power2.out", ...IR }, t));
    const tf = S(41) + 0.02, land = S(42) + 0.06;           // "não tem": it falls
    tl.to(heart.position, { y: hy, duration: land - tf, ease: "power2.in" }, tf);
    tl.fromTo(heart.scale, { x: K * 1.24, y: K * 0.7 }, { x: K, y: K, duration: 0.3, ease: "elastic.out(1.2, 0.4)", ...IR }, land);
    const ts = S(43) - 0.1;                                 // "sentimento": scanned, counted, zero
    const beam = new THREE.Group();
    beam.add(new THREE.Mesh(new THREE.PlaneGeometry(5.1, 0.07), basic(0x1892f0, 0.95)));
    beam.add(new THREE.Mesh(new THREE.PlaneGeometry(5.1, 0.6), basic(0x1892f0, 0.16)));
    beam.position.set(0, 3.7, 1.3);
    g.add(beam);
    tl.fromTo(beam.scale, { x: 0.001, y: 0.001, z: 1 }, { x: 1, y: 1, duration: 0.1, ease: "power2.out" }, ts);
    tl.fromTo(beam.position, { y: 3.7 }, { y: 0.5, duration: 0.3, ease: "sine.inOut" }, ts);
    tl.to(beam.scale, { x: 0.001, y: 0.001, duration: 0.1, ease: "power2.in" }, ts + 0.3);
    colorTo(hm, 0x9a9da8, ts + 0.1, 0.16);
    tl.to(heart.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.2, ease: "back.in(2)" }, ts + 0.2);
    tl.to(heart.position, { z: 0.3, duration: 0.2, ease: "power2.in" }, ts + 0.2);
    const zero = text3d("0", 0.5, 0.12, M.red);
    zero.position.set(ex, ey - 0.26, 0.2);
    sheet.add(zero);
    pop(zero, ts + 0.36, 0.26, "back.out(2.6)");
    pop(res, ts + 0.36, 0.26, "back.out(2.6)");
    tl.fromTo(sheet.rotation, { z: 0 }, { z: 0.02, duration: 0.05, yoyo: true, repeat: 3, ease: "sine.inOut", ...IR }, ts + 0.36);
    s.update = (t) => {
      const u = t - FS2;
      g.position.y = t > tl0 && t < tl0 + 0.4 ? Math.sin((t - tl0) * 80) * 0.07 * Math.exp(-(t - tl0) / 0.07) : 0;   // the sheet lands hard
      fx.rotation.z = Math.sin(u * 1.4) * 0.008;
      heart.rotation.y = Math.sin(u * 2.3) * 0.3;
      heart.rotation.z = t < tf ? Math.sin(u * 3.1) * 0.06 : 0;
    };
  });

  // ===== 6 · split: "Então me diz, o que você entrega que não cabe nessa conta?" (the CTA card is DOM, on the right)
  const MINI = { w: 2.86, h: 3.96, head: 0.66, letters: 0.26, nums: 0.3, cols: 3, rows: 5 };
  addScene("gift", C5, T.total + 1, false, (s, g) => {
    addFloor(g, 0);
    addWall(g, -1.4);
    s.cam.position.set(0.2, 2.9, 12.2);
    s.look.set(0.2, 2.45, 0);
    camTo(s, C5, T.total - C5, [0.2, 2.9, 11.7], [0.2, 2.45, 0], "sine.out");
    const G = MINI;
    const sheet = new THREE.Group();
    sheet.position.set(-2.32, 2.55, 0);
    g.add(sheet);
    sheet.add(rbox(G.w + 0.04, G.h + 0.04, 0.1, 0.12, M.white));
    const face = textPlane(G.w, G.h, drawGrid(G, "PLANILHA"));
    face.position.z = 0.052;
    sheet.add(face);
    tl.fromTo(sheet.rotation, { y: -1.9 }, { y: 0.26, duration: 0.6, ease: "back.out(1.3)" }, C5 - 0.12);
    pop(sheet, C5 - 0.12, 0.5, "back.out(1.4)");
    const CELL = [2, 1];
    let n = 0;
    for (let r = 0; r < G.rows; r++) {
      for (let c = 0; c < G.cols; c++) {
        if (r === CELL[0] && c === CELL[1]) continue;
        const [x, y, cw] = cellAt(G, r, c);
        const wd = cw * [0.6, 0.42, 0.68, 0.5, 0.55][(r * 2 + c * 3) % 5];
        const b = rbox(wd, 0.15, 0.06, 0.05, M.cell);
        b.position.set(x - cw * 0.38 + wd / 2, y, 0.085);
        sheet.add(b);
        pop(b, C5 + 0.2 + n * 0.03, 0.2, "back.out(2)");
        n++;
      }
    }
    const [cx, cy, cw, ch] = cellAt(G, CELL[0], CELL[1]);
    const sel = frame(cw, ch, 0.06, BLUE);
    sel.position.set(cx, cy, 0.1);
    sheet.add(sel);
    pop(sel, S(47) - 0.03, 0.2, "back.out(2)");
    // "o que você entrega": it shows up inside the cell ... "que não cabe": and it does not fit
    const gf = gift();
    gf.position.set(cx, cy, 0.42);
    gf.rotation.set(0.3, -0.5, 0);
    sheet.add(gf);
    const K0 = 0.26, K1 = 0.98;
    pop(gf, S(50) - 0.05, 0.32, "back.out(2.4)", K0);
    const tg = S(52) - 0.02;
    tl.to(gf.scale, { x: K1, y: K1, z: K1, duration: 0.5, ease: "back.out(1.8)" }, tg);
    tl.to(gf.position, { y: cy + 0.25, z: 1.05, duration: 0.5, ease: "power2.out" }, tg);
    const tb = tg + 0.12;                                   // the cell gives way
    [[0, 1.5, 0.5], [0, -1.5, -0.6], [-1.4, 0.2, 0.9], [1.4, -0.2, -0.8]].forEach(([dx, dy, rz], k) => {
      const p = sel.children[k];
      tl.to(p.position, { x: p.position.x + dx, y: p.position.y + dy, z: 0.5, duration: 0.45, ease: "power2.out" }, tb);
      tl.to(p.rotation, { z: rz, duration: 0.45, ease: "power1.out" }, tb);
      tl.to(p.scale, { x: 0.001, y: 0.001, z: 0.001, duration: 0.18, ease: "power2.in" }, tb + 0.3);
    });
    tl.fromTo(sheet.rotation, { z: 0 }, { z: 0.03, duration: 0.05, yoyo: true, repeat: 3, ease: "sine.inOut", ...IR }, tb);
    sparkle(sheet, [[cx - 1.05, cy + 1.25, 1.3], [cx + 1.0, cy + 1.0, 1.3], [cx - 0.8, cy - 0.85, 1.3], [cx + 1.05, cy - 0.6, 1.3]], S(54) + 0.1, 0.16, 0.3);
    sparkle(sheet, [[cx + 0.2, cy + 1.5, 1.3], [cx - 1.1, cy + 0.2, 1.3], [cx + 1.1, cy + 0.3, 1.3]], E(55) + 0.02, 0.12, 0.3);
    s.update = (t) => {
      const u = t - C5;
      sheet.rotation.z = (t < tb || t > tb + 0.4 ? 1 : 0) * Math.sin(u * 1.3) * 0.012;
      gf.rotation.y = -0.5 + Math.sin(u * 1.5) * 0.3 + Math.max(0, t - tg) * 0.5;
    };
  });

  // ------------------------------------------------------------------ render exactly the requested time
  const faceAt = window.__faceAt || (() => {});
  function renderAt(t) {
    faceAt(t);
    key.position.x = 6 + Math.sin(t * 0.8) * 0.9;           // the light breathes a little: highlights move on the gold
    renderer.setScissorTest(false);
    renderer.setViewport(0, 0, W, H);
    renderer.clear(true, true, true);
    for (const s of SC) {
      const on = t >= s.t0 && t < s.t1;
      s.g.visible = on;
      if (!on) continue;
      if (s.update) s.update(t);
      s.cam.lookAt(s.look);
      const vy = s.full ? 0 : H - SEAM, vh = s.full ? H : SEAM;
      renderer.setViewport(0, vy, W, vh);
      renderer.setScissor(0, vy, W, vh);
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
  renderAt(typeof window.__hfThreeTime === "number" ? window.__hfThreeTime : tl.time());
}
