// Vídeo animado (tela cheia, sem gravação) — kit comum a todos os vídeos: renderizador, luz, materiais, construtores,
// personagem (astronauta Dr. Hélio), legendas e relógio. As cenas de cada vídeo ficam em cenas.js.
// Tudo é função pura do tempo da timeline GSAP: o HyperFrames posiciona a timeline e dispara "hf-seek";
// desenhamos exatamente aquele quadro. Sem requestAnimationFrame, sem relógio de parede, sem acaso.
import * as THREE from "three";
import { RoundedBoxGeometry } from "three/addons/geometries/RoundedBoxGeometry.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

const norm = (s) => s.toLowerCase().normalize("NFD").replace(/[^a-z0-9]/g, "");

export async function criarKit() {
  const tl = window.tl, A = window.ANIM, W = A.W, H = A.H;
  await Promise.all(['400 120px "Bebas Neue"', '700 60px "Inter"'].map((f) => document.fonts.load(f)));
  const { makeAstronaut } = await import("./assets/astronauta.js");

  // qualidade do 3D (o render é por software, sem placa de vídeo): escala do quadro 3D, suavização e sombra
  const Q = Object.assign({ escala: 1, aa: true, sombra: 2048, suave: true, verniz: true }, A.q, window.QUAL);
  const renderer = new THREE.WebGLRenderer({ canvas: document.getElementById("gl"), antialias: Q.aa, preserveDrawingBuffer: true });
  renderer.setPixelRatio(1);
  renderer.setSize(Math.round(W * Q.escala), Math.round(H * Q.escala), false);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.NeutralToneMapping;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = Q.suave ? THREE.PCFSoftShadowMap : THREE.PCFShadowMap;

  const scene = new THREE.Scene();
  scene.background = new THREE.Color(0x8fd0ff);
  scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture;
  scene.environmentIntensity = 0.55;
  const sol = new THREE.DirectionalLight(0xfff2d8, 2.3);
  sol.position.set(7, 15, 12);
  sol.target.position.set(0, -2, 0);
  sol.castShadow = true;
  sol.shadow.mapSize.set(Q.sombra, Q.sombra);
  Object.assign(sol.shadow.camera, { left: -14, right: 14, top: 14, bottom: -14, near: 1, far: 60 });
  sol.shadow.bias = -0.0005;
  sol.shadow.normalBias = 0.03;
  scene.add(sol, sol.target, new THREE.HemisphereLight(0xffffff, 0x9bbf7a, 0.75));

  const cam = new THREE.PerspectiveCamera(50, W / H, 0.1, 300);
  const olho = { x: 0, y: 1.5, z: 16, lx: 0, ly: 0, lz: 0, dx: 0, dy: 0 };   // posição, alvo e tremor da câmera

  // ---- materiais e construtores (os mesmos nomes do scene3d.js dos Reels; o astronauta depende deles)
  const mat = (hex, o = {}) => Q.verniz
    ? new THREE.MeshPhysicalMaterial({ color: hex, roughness: o.r ?? 0.42, metalness: o.m ?? 0, clearcoat: o.cc ?? 0.5, clearcoatRoughness: 0.3 })
    : new THREE.MeshStandardMaterial({ color: hex, roughness: (o.r ?? 0.42) * 0.8, metalness: o.m ?? 0 });
  const basic = (hex, o = 1) => new THREE.MeshBasicMaterial({ color: hex, transparent: o < 1, opacity: o, toneMapped: false });
  const fosco = (hex) => new THREE.MeshStandardMaterial({ color: hex, roughness: 0.95, flatShading: true });   // visual de maquete
  const M = {
    gold: mat(0xf4b04a, { r: 0.28, m: 0.35, cc: 0.9 }), navy: mat(0x0b2266, { r: 0.4 }), ink: mat(0x05103a, { r: 0.3, cc: 0.9 }),
    blue: mat(0x0457e7, { r: 0.35 }), sky: mat(0x5ca2ee, { r: 0.4 }), white: mat(0xf8f6f1, { r: 0.55, cc: 0.25 }),
    red: mat(0xe5484d, { r: 0.4 }), green: mat(0x2fb46a, { r: 0.4 }), grey: mat(0xc9c6bd, { r: 0.6 }), steel: mat(0x5d6b7a, { r: 0.35, m: 0.6 }),
  };
  const sh = (m) => { m.castShadow = true; m.receiveShadow = true; return m; };
  const rbox = (w, h, d, r, material) => sh(new THREE.Mesh(new RoundedBoxGeometry(w, h, d, 5, Math.min(r, w / 2 - 0.001, h / 2 - 0.001, d / 2 - 0.001)), material));
  const cyl = (rt, rb, h, material, seg = 48) => sh(new THREE.Mesh(new THREE.CylinderGeometry(rt, rb, h, seg), material));
  const sph = (r, material) => sh(new THREE.Mesh(new THREE.SphereGeometry(r, 48, 28), material));
  // bloco entre dois cantos; base = true põe o pivô no chão do bloco (para crescer de baixo para cima com scale.y)
  function bloco(x0, x1, y0, y1, z0, z1, material, base = false) {
    const g = new THREE.BoxGeometry(x1 - x0, y1 - y0, z1 - z0);
    if (base) g.translate(0, (y1 - y0) / 2, 0);
    const b = sh(new THREE.Mesh(g, material));
    b.position.set((x0 + x1) / 2, base ? y0 : (y0 + y1) / 2, (z0 + z1) / 2);
    scene.add(b);
    return b;
  }
  function astronauta(escala = 0.5) {            // o professor: astronauta com o rosto do Dr. Hélio; origem nos pés
    const a = makeAstronaut({ THREE, rbox, cyl, sph, sh, mat, basic, M });
    a.scale.setScalar(escala);
    const g = new THREE.Group();
    g.add(a);
    g.userData = a.userData;                      // { head, arms: [esq, dir], eyeM }
    scene.add(g);
    return g;
  }
  function peao(material) {                       // aluno: peça de jogo sem rosto; origem nos pés, 1,2 de altura
    const g = new THREE.Group();
    const pe = cyl(0.36, 0.4, 0.12, material); pe.position.y = 0.06;
    const corpo = cyl(0.16, 0.33, 0.66, material); corpo.position.y = 0.45;
    const cab = sph(0.27, material); cab.position.y = 0.98;
    g.add(pe, corpo, cab);
    scene.add(g);
    return g;
  }

  // ---- tempo: cada cena e cada palavra da narração têm hora marcada (out/words.json)
  const cena = (id) => A.cenas.find((c) => c.id === id);
  function quando(id, palavra, n = 0) {           // início da n-ésima ocorrência da palavra na fala da cena
    const c = cena(id), ws = c.w.filter((w) => norm(w.w) === norm(palavra));
    return (ws[n] || ws[ws.length - 1] || { t0: c.t0 }).t0;
  }

  // ---- camada de tela (HUD): elementos HTML por cima do 3D, sempre controlados pela timeline
  const hud = document.getElementById("hud");
  const estilo = (css) => { const s = document.createElement("style"); s.textContent = css; document.head.appendChild(s); };
  function dom(html) {
    const d = document.createElement("div");
    d.innerHTML = html.trim();
    const e = d.firstChild;
    hud.appendChild(e);
    gsap.set(e, { autoAlpha: 0 });
    return e;
  }
  function mostra(e, t0, t1, o = {}) {            // entra com um estalo em t0 e sai em t1 (sem t1, fica)
    tl.fromTo(e, { autoAlpha: 0, scale: o.de ?? 0.7, y: o.y ?? 24 }, { autoAlpha: 1, scale: 1, y: 0, duration: 0.24, ease: "back.out(2.2)", immediateRender: false }, t0);
    if (t1 != null) tl.to(e, { autoAlpha: 0, duration: 0.14, ease: "power1.in" }, t1 - 0.14);
  }

  // ---- legendas: a pílula entra com o trecho apagado e cada palavra acende quando é dita
  A.caps.forEach((c) => {
    const e = document.getElementById(c.id);
    tl.set(e, { autoAlpha: 1 }, c.s);
    tl.fromTo(e.firstChild, { scale: 0.9, y: 8 }, { scale: 1, y: 0, duration: 0.12, ease: "back.out(2.2)", immediateRender: false }, c.s);
    tl.set(e, { autoAlpha: 0 }, c.e);
    c.w.forEach((w) => tl.set("#" + w.id, { opacity: 1, color: "#F4B04A" }, w.t));
  });

  // ---- desenhar exatamente o tempo pedido
  const quadro = [];                              // funções (t) chamadas antes de cada quadro: movimentos procedurais
  function renderAt(t) {
    for (const f of quadro) f(t);
    cam.position.set(olho.x + olho.dx, olho.y + olho.dy, olho.z);
    cam.lookAt(olho.lx + olho.dx, olho.ly + olho.dy, olho.lz);
    renderer.render(scene, cam);
  }
  function pronto() {
    tl.set({}, {}, A.total);                      // a timeline dura o vídeo inteiro
    window.addEventListener("hf-seek", (e) => {
      const t = e.detail && typeof e.detail.time === "number" ? e.detail.time : tl.time();
      if (Math.abs(tl.time() - t) > 1e-4) tl.time(t, false);
      renderAt(t);
    });
    tl.eventCallback("onUpdate", () => renderAt(tl.time()));
    renderAt(typeof window.__hfThreeTime === "number" ? window.__hfThreeTime : tl.time());
  }

  return { THREE, tl, A, W, H, scene, sol, olho, M, mat, basic, fosco, sh, rbox, cyl, sph, bloco, astronauta, peao, cena, quando, estilo, dom, mostra, quadro, pronto };
}
