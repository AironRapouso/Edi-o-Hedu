// Cenas do vídeo "A bomba já caiu na sua sala" (Método da Aprendizagem Verificável).
// Um mundo só, visto em corte: campo em cima, bunker embaixo. O professor (astronauta) constrói 5 camadas.
// Modelo para os próximos vídeos: troque este arquivo e o roteiro.json; o kit.js não muda.
import { criarKit } from "./kit.js";

const fim = window.__cenasProntas || (() => {});
try {
  await montar();
} catch (err) {
  const d = document.createElement("div");
  d.id = "err3d";
  d.style.cssText = "position:absolute;left:0;top:0;z-index:99;width:1080px;background:#c00;color:#fff;font:20px monospace;white-space:pre-wrap;padding:12px";
  d.textContent = "cenas: " + (err && err.stack ? err.stack : err);
  document.getElementById("root").appendChild(d);
  console.error("cenas", err);
}
fim();

async function montar() {
  const k = await criarKit();
  const { THREE, tl, A, scene, olho, M, basic, fosco, sh, rbox, cyl, sph, bloco, cena, quando, dom, mostra, quadro } = k;
  const T = Object.fromEntries(A.cenas.map((c) => [c.id, c]));
  const CAM = ["c1", "c2", "c3", "c4", "c5"];
  const some = (o) => { o.visible = false; return o; };
  const vis = new Map();                                      // visibilidade com hora marcada (aplicada a cada quadro)
  const marca = (o, t, v) => { if (!vis.has(o)) vis.set(o, { ini: o.visible, ev: [] }); vis.get(o).ev.push([t, v]); };
  const liga = (o, t) => marca(o, t, true);
  const desliga = (o, t) => marca(o, t, false);

  // ------------------------------------------------------------------ o terreno em corte
  const GRAMA = fosco(0x6cc24a), TERRA = fosco(0x9a6a3c), TERRA2 = fosco(0x74502f), CONC = fosco(0xc9ccd1), PAREDE = fosco(0xe6e9ee);
  const X = 3.2, PX0 = 1.3, PX1 = 2.9;                       // meia largura da sala; o poço da escada vai de PX0 a PX1
  bloco(-60, 60, -14, -0.25, -80, -3, TERRA2);                // fundo do corte
  bloco(-60, 60, -0.25, 0, -80, -3, GRAMA);
  bloco(-60, -X, -14, -0.25, -3, 0, TERRA); bloco(-60, -X, -0.25, 0, -3, 0, GRAMA);
  bloco(X, 60, -14, -0.25, -3, 0, TERRA); bloco(X, 60, -0.25, 0, -3, 0, GRAMA);
  bloco(-X, X, -14, -5.2, -3, 0, TERRA);
  bloco(-X, PX0, -1, -0.25, -3, 0, TERRA); bloco(-X, PX0, -0.25, 0, -3, 0, GRAMA);
  bloco(PX1, X, -1, -0.25, -3, 0, TERRA); bloco(PX1, X, -0.25, 0, -3, 0, GRAMA);
  const tampao = bloco(-X, X, -5.2, -1, -3, 0, TERRA, true);  // a terra que ocupa a sala antes da obra
  const tampaoPoco = bloco(PX0, PX1, -1, -0.25, -3, 0, TERRA, true);
  const tampaoGrama = bloco(PX0, PX1, -0.25, 0, -3, 0, GRAMA);
  [tampao, tampaoPoco].forEach((b) => { b.scale.y = 0.0001; b.visible = false; });
  tampaoGrama.visible = false;

  const arvores = [[-3.3, -7], [3.6, -9], [0.4, -14], [-6, -18], [6.5, -20]].map(([x, z], i) => {
    const g = new THREE.Group();
    const tronco = cyl(0.16, 0.22, 1.3, fosco(0x7a4f2b), 8); tronco.position.y = 0.65;
    const copa = sh(new THREE.Mesh(new THREE.IcosahedronGeometry(1.05 + (i % 2) * 0.25, 0), fosco(i % 2 ? 0x3f9b46 : 0x4fae4a))); copa.position.y = 1.95;
    g.add(tronco, copa); g.position.set(x, 0, z); scene.add(g);
    return g;
  });

  // ------------------------------------------------------------------ a bomba no horizonte
  const bomba = new THREE.Group();
  bomba.add(new THREE.Mesh(new THREE.SphereGeometry(2.6, 32, 20), basic(0xfff6d2)), new THREE.Mesh(new THREE.SphereGeometry(4.6, 32, 20), basic(0xffc35a, 0.4)));
  bomba.position.set(-3.4, 3.4, -55);
  const onda = new THREE.Mesh(new THREE.BoxGeometry(160, 16, 2.5), basic(0xff9a3c, 0.6));
  onda.position.set(0, 8, -55);
  scene.add(bomba, some(onda));

  // ------------------------------------------------------------------ as 5 camadas do bunker (prontas no início; a obra rebobina)
  const laje = bloco(-X + 0.05, X - 0.05, -5.2, -4.9, -2.95, 0.05, CONC);                                   // 1 fundação
  const paredes = [bloco(-X + 0.05, -X + 0.3, -4.9, -1, -2.95, 0.05, CONC, true), bloco(X - 0.3, X - 0.05, -4.9, -1, -2.95, 0.05, CONC, true),
    bloco(-X + 0.3, X - 0.3, -4.9, -1, -2.95, -2.75, PAREDE, true)];                                          // 2 paredes
  const tetos = [bloco(-X + 0.05, PX0, -1.22, -1, -2.95, 0.05, CONC), bloco(PX1, X - 0.05, -1.22, -1, -2.95, 0.05, CONC)];
  const luz = new THREE.PointLight(0xffe2b0, 26, 14); luz.position.set(-0.4, -1.9, -0.8); scene.add(luz);
  const PXC = (PX0 + PX1) / 2;
  const escada = new THREE.Group();                                                                          // 3 porta: escada e escotilha com 3 travas
  [-0.36, 0.36].forEach((dx) => { const r = cyl(0.045, 0.045, 5.2, M.steel, 10); r.position.set(dx, -2.3, 0); escada.add(r); });
  for (let i = 0; i < 12; i++) { const d = cyl(0.035, 0.035, 0.72, M.steel, 8); d.rotation.z = Math.PI / 2; d.position.y = -4.6 + i * 0.42; escada.add(d); }
  escada.position.set(PXC, 0, -2.3); scene.add(escada);
  const escotilha = new THREE.Group();                        // pivô na borda direita: gira para abrir
  const tampa = rbox(1.7, 0.2, 1.9, 0.08, M.steel); tampa.position.set(-0.85, 0.1, 0);
  escotilha.add(tampa);
  const travas = [-0.6, 0, 0.6].map((dz) => { const t = cyl(0.14, 0.14, 0.14, M.gold, 20); t.position.set(-0.85, 0.27, dz); escotilha.add(t); return t; });
  escotilha.position.set(PX1 + 0.05, 0, -1.5); escotilha.rotation.z = -1.35; scene.add(escotilha);
  const mesas = [-2.0, -0.2, 1.3].map((x, i) => {                                                            // 4 interior: três grupos
    const g = new THREE.Group();
    const pe = cyl(0.1, 0.16, 0.55, M.steel, 12); pe.position.y = 0.28;
    const tampo = rbox(1.0, 0.1, 0.8, 0.04, M.navy); tampo.position.y = 0.6;
    g.add(pe, tampo); g.position.set(x, -4.9, -1.9); scene.add(g);
    const al = k.peao([M.sky, M.gold, M.green][i]); al.scale.setScalar(0.85); al.position.set(x + 0.05, -4.9, -1.0);
    return { g, al };
  });
  const medidor = new THREE.Group();                                                                         // 5 teste de pressão
  const aro = cyl(0.86, 0.86, 0.12, M.navy, 40); aro.rotation.x = Math.PI / 2;
  const disco = cyl(0.74, 0.74, 0.14, M.white, 40); disco.rotation.x = Math.PI / 2;
  const agulha = new THREE.Group(); const ag = rbox(0.09, 0.62, 0.05, 0.02, M.red); ag.position.set(0, 0.26, 0.1); agulha.add(ag); agulha.rotation.z = -0.9;
  medidor.add(aro, disco, agulha, (() => { const c = cyl(0.09, 0.09, 0.2, M.navy, 16); c.rotation.x = Math.PI / 2; return c; })());
  medidor.position.set(-1.9, -2.25, -2.68); scene.add(medidor);

  // ------------------------------------------------------------------ personagens
  const prof = k.astronauta(0.5);
  const [bracoE, bracoD] = prof.userData.arms;
  const fora = k.peao(M.red); fora.position.set(-2.3, 0, -1.4); some(fora);                                  // aluno que usou a IA sozinho
  const papel = rbox(0.5, 0.66, 0.04, 0.02, M.white); papel.position.set(0.34, 0.72, 0.3); papel.rotation.z = -0.15; fora.add(papel);
  const cinza = fosco(0x6b6b6b);

  // ------------------------------------------------------------------ tela (HUD)
  k.estilo(`
    .hud{position:absolute;left:0;top:0;transform-origin:50% 50%}
    #relogio{left:340px;top:70px;width:400px;height:150px;border-radius:26px;background:#150406;border:8px solid #e5484d;color:#ff5a5f;font:400 130px/134px "Bebas Neue";text-align:center;letter-spacing:6px;box-shadow:0 0 50px rgba(229,72,77,.6)}
    #veu,#veu2{left:0;top:0;width:1080px;height:1920px;background:rgba(3,10,38,.3)} #veu2{background:rgba(3,10,38,.8)}
    #clarao{left:0;top:0;width:1080px;height:1920px;background:#fff}
    #pausa{left:390px;top:780px;width:300px;height:300px;border-radius:50%;background:rgba(255,255,255,.94);box-shadow:0 16px 60px rgba(0,0,0,.45)}
    #pausa i{position:absolute;top:80px;width:46px;height:140px;border-radius:12px;background:#0b2266} #pausa i:first-child{left:88px} #pausa i:last-child{left:166px}
    .faixa{left:60px;width:960px;text-align:center;color:#fff;font:400 118px/118px "Bebas Neue";letter-spacing:2px;text-shadow:0 6px 0 #05103a,0 10px 30px rgba(0,0,0,.5)}
    .et{left:390px;width:670px;height:100px;border-radius:26px;background:#fff;box-shadow:0 12px 34px rgba(0,0,0,.35);font:700 38px/100px "Inter";color:#05103a;text-align:left;white-space:nowrap}
    .et b{display:inline-block;height:100px;padding:0 22px;margin-right:18px;border-radius:26px 0 0 26px;color:#fff;font:400 64px/106px "Bebas Neue";letter-spacing:2px;vertical-align:top}
    .mas b{background:#e5484d} .entao b{background:#1fa35c}
    #cartao{left:110px;top:330px;width:860px;padding:44px 0 50px;border-radius:44px;background:#fff;text-align:center;color:#05103a;box-shadow:0 24px 70px rgba(0,0,0,.5)}
    #cartao .n{font:400 150px/150px "Bebas Neue";color:#f4b04a;text-shadow:0 4px 0 #05103a} #cartao .l{font:700 46px/60px "Inter"}
    .num{left:110px;width:860px;height:250px;border-radius:44px;background:#fff;box-shadow:0 24px 70px rgba(0,0,0,.5);color:#05103a;font:700 48px/250px "Inter";white-space:nowrap}
    .num b{display:inline-block;width:400px;margin-right:24px;text-align:center;font:400 200px/262px "Bebas Neue";vertical-align:top}
    .lt{left:100px;width:880px;text-align:center;color:#f4b04a;font:400 120px/120px "Bebas Neue";letter-spacing:3px}
    .li{left:100px;width:880px;height:150px;border-radius:32px;background:#fff;color:#05103a;font:700 54px/150px "Inter";white-space:nowrap;box-shadow:0 14px 40px rgba(0,0,0,.4)}
    .li b{display:inline-block;width:120px;text-align:center;font:400 96px/158px "Bebas Neue";color:#0457e7;vertical-align:top}
    .li u{position:absolute;right:28px;top:31px;width:88px;height:88px;border-radius:50%;background:#1fa35c;color:#fff;font:700 62px/88px "Inter";text-align:center;text-decoration:none}
    #prova{left:0;top:150px;width:1080px;text-align:center;color:#f4b04a;font:400 330px/300px "Bebas Neue";letter-spacing:14px;text-shadow:0 10px 0 #05103a,0 20px 50px rgba(0,0,0,.5)}
    #cta{left:90px;top:1290px;width:900px;padding:34px 0;border-radius:40px;background:#0b2266;color:#fff;text-align:center;font:700 58px/74px "Inter";box-shadow:0 16px 44px rgba(0,0,0,.45)}
    .rot{height:96px;padding:0 34px;border-radius:26px;color:#fff;font:400 66px/102px "Bebas Neue";letter-spacing:2px;white-space:nowrap;box-shadow:0 10px 30px rgba(0,0,0,.4)}
  `);
  const relogio = dom('<div id="relogio" class="hud">00:09</div>');
  const veu = dom('<div id="veu" class="hud"></div>'), veu2 = dom('<div id="veu2" class="hud"></div>');
  const pausa = dom('<div id="pausa" class="hud"><i></i><i></i></div>');
  const clarao = dom('<div id="clarao" class="hud"></div>');

  // ================================================================== 1. gancho: a bomba, o relógio, a corrida
  const g = T.gancho, p = T.pausa, d = T.dado, o = T.obra, te = T.teste, li = T.lista, ct = T.cta;
  const CORTE = { x: 0, y: -1.6, z: 14.5, lx: 0, ly: -2.4, lz: 0 };
  Object.assign(olho, { x: 0.4, y: 1.3, z: 14.5, lx: 0.6, ly: -0.3, lz: 0 });
  tl.to(olho, { z: 15.5, y: 1.0, duration: p.t1 - g.t0, ease: "none" }, g.t0);
  mostra(relogio, g.t0 + 0.05, d.t0);
  const tDesce = g.t0 + (g.t1 - g.t0) * 0.62;
  prof.position.set(-3.7, 0, -1.3); prof.rotation.y = 1.1;
  tl.to(prof.position, { x: PXC, duration: tDesce - g.t0, ease: "none" }, g.t0);
  tl.to(prof.rotation, { y: Math.PI, duration: 0.25 }, tDesce - 0.2);
  tl.to(prof.position, { y: -1.9, z: -1.75, duration: g.t1 - tDesce, ease: "none" }, tDesce);
  tl.to(bomba.scale, { x: 1.5, y: 1.5, z: 1.5, duration: p.t0 - g.t0, ease: "power1.in" }, g.t0);

  // ================================================================== 2. pausa
  mostra(pausa, p.t0, p.t1);
  tl.to(veu, { autoAlpha: 1, duration: 0.15 }, p.t0);
  const faixaIA = dom('<div class="hud faixa" style="top:330px">A BOMBA É A IA</div>');
  mostra(faixaIA, quando("pausa", "bomba"), p.t1);

  // ================================================================== 3. dado
  tl.to(veu2, { autoAlpha: 1, duration: 0.2 }, d.t0 - 0.1);
  tl.set(veu, { autoAlpha: 0 }, d.t0 + 0.2);
  const cartao = dom('<div id="cartao" class="hud"><div class="l">TRABALHO PERFEITO EM</div><div class="n">30 SEGUNDOS</div></div>');
  const n48 = dom('<div class="hud num" style="top:800px"><b style="color:#1fa35c">+48%</b>no exercício</div>');
  const n17 = dom('<div class="hud num" style="top:1090px"><b style="color:#e5484d">−17%</b>na prova sem IA</div>');
  mostra(cartao, quando("dado", "trabalho") - 0.1, d.t1);
  mostra(n48, quando("dado", "quarenta") - 0.1, d.t1);
  mostra(n17, quando("dado", "dezessete") - 0.1, d.t1);

  // ================================================================== 4. obra: rebobina, cava
  const pecas = [laje, ...paredes, ...tetos, escada, escotilha, medidor, ...mesas.flatMap((m) => [m.g, m.al])];
  const r0 = o.t0;
  pecas.forEach((x) => desliga(x, r0));
  tl.set(luz, { intensity: 0 }, r0);
  [tampao, tampaoPoco, tampaoGrama].forEach((x) => liga(x, r0));
  tl.set([tampao.scale, tampaoPoco.scale], { y: 1 }, r0);
  tl.set(prof.position, { x: -2.2, y: 0, z: -1.4 }, r0);
  tl.set(prof.rotation, { y: 0.35 }, r0);
  tl.set(bomba.scale, { x: 1, y: 1, z: 1 }, r0);
  tl.set(olho, CORTE, r0);
  tl.to(veu2, { autoAlpha: 0, duration: 0.3 }, r0);
  const tCava = quando("obra", "constrói");
  desliga(tampaoGrama, tCava);
  tl.to(tampaoPoco.scale, { y: 0.0001, duration: 0.35, ease: "power2.in" }, tCava);
  tl.to(tampao.scale, { y: 0.0001, duration: Math.max(0.6, o.t1 - tCava - 0.45), ease: "power1.inOut" }, tCava + 0.3);
  const acena = (t) => { tl.to(bracoD.rotation, { z: 2.5, duration: 0.2, ease: "back.out(2)" }, t); tl.to(bracoD.rotation, { z: 0.22, duration: 0.3 }, t + 0.7); };
  acena(tCava);
  const faixa5 = dom('<div class="hud faixa" style="top:250px">5 CAMADAS</div>');
  mostra(faixa5, quando("obra", "cinco") - 0.05, o.t1);

  // ================================================================== 5 a 9. as camadas, cada uma com MAS e ENTÃO
  const TXT = {
    c1: ["1 · PROPÓSITO", "OBJETIVO VAGO", "FAZER SOZINHO"], c2: ["2 · EM CASA", "IA RESPONDE TUDO", "IA VIRA TUTORA"],
    c3: ["3 · ENTRADA", "METADE NÃO PASSA", "SABE QUEM AJUDAR"], c4: ["4 · PRÁTICA", "CADA GRUPO TRAVA", "INTERVÉM NA HORA"],
    c5: ["5 · PROVA", "ALUNO GAGUEJA", "VOLTA UMA CAMADA"],
  };
  CAM.forEach((id) => {
    const c = T[id], [titulo, mas, entao] = TXT[id];
    mostra(dom(`<div class="hud faixa" style="top:120px">${titulo}</div>`), c.t0, c.t1);
    mostra(dom(`<div class="hud et mas" style="top:290px"><b>MAS…</b>${mas}</div>`), quando(id, "Mas") - 0.05, c.t1, { de: 0.5 });
    mostra(dom(`<div class="hud et entao" style="top:406px"><b>ENTÃO…</b>${entao}</div>`), quando(id, "Então") - 0.05, c.t1, { de: 0.5 });
    acena(c.t0 + 0.1);
  });
  const cai = (obj, t, y) => { liga(obj, t); tl.fromTo(obj.position, { y: y + 7 }, { y, duration: 0.5, ease: "bounce.out", immediateRender: false }, t); };
  cai(laje, T.c1.t0 + 0.25, laje.position.y);
  paredes.forEach((w, i) => { liga(w, T.c2.t0 + 0.2 + i * 0.18); tl.fromTo(w.scale, { y: 0.0001 }, { y: 1, duration: 0.45, ease: "back.out(1.6)", immediateRender: false }, T.c2.t0 + 0.2 + i * 0.18); });
  tetos.forEach((w) => cai(w, T.c2.t0 + 0.85, w.position.y));
  tl.to(luz, { intensity: 26, duration: 0.3 }, T.c2.t0 + 1.2);
  liga(escada, T.c3.t0 + 0.2);
  tl.fromTo(escada.position, { y: 6 }, { y: 0, duration: 0.45, ease: "power2.out", immediateRender: false }, T.c3.t0 + 0.2);
  liga(escotilha, T.c3.t0 + 0.6);
  tl.set(escotilha.rotation, { z: 0 }, T.c3.t0 + 0.6);
  tl.fromTo(escotilha.position, { y: 6 }, { y: 0, duration: 0.5, ease: "bounce.out", immediateRender: false }, T.c3.t0 + 0.6);
  travas.forEach((t, i) => tl.fromTo(t.scale, { x: 0.01, y: 0.01, z: 0.01 }, { x: 1, y: 1, z: 1, duration: 0.25, ease: "back.out(3)", immediateRender: false }, quando("c3", "três", 1) + i * 0.22));
  const c4 = T.c4;
  tl.to(olho, { y: -2.6, z: 11.5, ly: -3.1, duration: 0.6, ease: "power2.inOut" }, c4.t0);
  tl.set(prof.position, { x: -2.0, y: -4.9, z: -0.6 }, c4.t0 + 0.05);
  tl.set(prof.rotation, { y: 0.3 }, c4.t0 + 0.05);
  mesas.forEach((m, i) => [m.g, m.al].forEach((x, j) => {
    const t = c4.t0 + 0.3 + i * 0.2 + j * 0.12;
    liga(x, t);
    tl.fromTo(x.scale, { x: 0.01, y: 0.01, z: 0.01 }, { x: j ? 0.85 : 1, y: j ? 0.85 : 1, z: j ? 0.85 : 1, duration: 0.3, ease: "back.out(2.4)", immediateRender: false }, t);
  }));
  tl.to(prof.position, { x: 1.9, duration: c4.t1 - quando("c4", "Então"), ease: "power1.inOut" }, quando("c4", "Então"));
  const c5 = T.c5;
  tl.to(olho, { ...CORTE, duration: 0.5, ease: "power2.inOut" }, c5.t0);
  liga(medidor, c5.t0 + 0.2);
  tl.fromTo(medidor.scale, { x: 0.01, y: 0.01, z: 0.01 }, { x: 1, y: 1, z: 1, duration: 0.35, ease: "back.out(2.4)", immediateRender: false }, c5.t0 + 0.2);
  tl.to(agulha.rotation, { z: 0.9, duration: 0.8, ease: "elastic.out(1,0.5)" }, quando("c5", "pressão"));
  tl.to(agulha.rotation, { z: 0.1, duration: 0.3 }, quando("c5", "gagueja"));
  tl.to(agulha.rotation, { z: -0.9, duration: 0.5, ease: "power2.in" }, quando("c5", "volta"));

  // ================================================================== 10. teste: o relógio volta, a bomba cai
  const boom = quando("teste", "cai") + 0.25;
  tl.to(olho, { y: -0.8, z: 16, ly: -1.6, duration: 0.5, ease: "power2.inOut" }, te.t0);
  tl.set(prof.position, { x: 1.2, y: -4.9, z: -0.7 }, te.t0);
  tl.set(prof.rotation, { y: -0.3 }, te.t0);
  tl.set(agulha.rotation, { z: -0.9 }, te.t0);
  mostra(relogio, te.t0 + 0.05, boom + 0.2);
  liga(fora, te.t0 + 0.1);
  tl.fromTo(fora.scale, { x: 0.01, y: 0.01, z: 0.01 }, { x: 1, y: 1, z: 1, duration: 0.3, ease: "back.out(2.4)", immediateRender: false }, te.t0 + 0.1);
  tl.to(escotilha.rotation, { z: 0, duration: 0.2 }, te.t0);
  tl.to(bomba.scale, { x: 9, y: 9, z: 9, duration: 0.3, ease: "power2.in" }, boom - 0.2);
  tl.fromTo(clarao, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.1 }, boom - 0.05);
  tl.to(clarao, { autoAlpha: 0, duration: 0.7, ease: "power1.out" }, boom + 0.12);
  liga(onda, boom);
  tl.to(onda.position, { z: 14, duration: 0.95, ease: "power1.in" }, boom);
  desliga(onda, boom + 0.95);
  tl.to(scene.background, { r: 0.80, g: 0.52, b: 0.30, duration: 0.4 }, boom);
  tl.to(bomba.scale, { x: 2.2, y: 2.2, z: 2.2, duration: 1.2 }, boom + 0.3);
  arvores.forEach((a, i) => { const t = boom + 0.55 - i * 0.05; tl.to(a.rotation, { x: 1.35, duration: 0.3, ease: "power2.in" }, t); tl.to(a.scale, { y: 0.5, duration: 0.3 }, t); });
  const tw = boom + 0.72;                                      // a onda chega ao aluno de fora
  tl.to(papel.scale, { x: 0.15, y: 0.15, z: 0.15, duration: 0.5 }, tw + 0.1);
  tl.to(papel.position, { y: 0.1, x: 0.6, duration: 0.5, ease: "power1.in" }, tw + 0.1);
  tl.to(fora.rotation, { z: -0.35, duration: 0.25, ease: "power2.out" }, tw);
  tl.to(agulha.rotation, { z: 0.9, duration: 0.6, ease: "elastic.out(1,0.5)" }, tw);
  const aluno = mesas[1].al;                                   // o aluno de dentro vem explicar
  tl.to(aluno.position, { x: 0.1, z: -0.5, duration: 0.4 }, quando("teste", "Quem", 1));
  tl.to(bracoD.rotation, { z: 2.4, duration: 0.25, ease: "back.out(2)" }, quando("teste", "explica"));
  tl.to(aluno.position, { y: -4.55, duration: 0.16, yoyo: true, repeat: 3, ease: "power1.out" }, quando("teste", "explica"));
  const rF = dom('<div class="hud rot" style="left:70px;top:420px;background:#e5484d">IA SOZINHO: CINZAS</div>');
  const rD = dom('<div class="hud rot" style="left:250px;top:1420px;background:#1fa35c">COM PROFESSOR: EXPLICA</div>');
  mostra(rF, quando("teste", "cinzas") - 0.3, te.t1);
  mostra(rD, quando("teste", "explica") - 0.3, te.t1);

  // ================================================================== 11. lista: o que o método deixa
  tl.to(veu2, { autoAlpha: 1, duration: 0.25 }, li.t0);
  mostra(dom('<div class="hud lt" style="top:250px">O MÉTODO DEIXA</div>'), li.t0 + 0.05, li.t1);
  ["Objetivo escrito", "Estudo em casa", "Entrada sem IA", "Prática em sala", "Explicação sem IA"].forEach((s, i) => {
    const t = li.t0 + 0.3 + i * Math.min(0.42, (li.t1 - li.t0 - 1.2) / 5);
    const e = dom(`<div class="hud li" style="top:${430 + i * 185}px"><b>${i + 1}</b>${s}<u>✓</u></div>`);
    mostra(e, t, li.t1, { de: 0.85 });
    tl.fromTo(e.querySelector("u"), { scale: 0 }, { scale: 1, duration: 0.22, ease: "back.out(3)" }, t + 0.22);
  });

  // ================================================================== 12. chamada final
  tl.set(olho, { x: 0, y: 1.5, z: 9.5, lx: 0, ly: 1.25, lz: 0 }, ct.t0);
  tl.set(prof.position, { x: 0, y: 0, z: -1.2 }, ct.t0);
  tl.set(prof.rotation, { y: 0 }, ct.t0);
  desliga(fora, ct.t0);
  tl.set(scene.background, { r: scene.background.r, g: scene.background.g, b: scene.background.b }, ct.t0);   // novo dia: céu azul, árvores de pé
  arvores.forEach((a) => { tl.set(a.rotation, { x: 0 }, ct.t0); tl.set(a.scale, { y: 1 }, ct.t0); });
  tl.to(veu2, { autoAlpha: 0, duration: 0.2 }, ct.t0);
  tl.to(bracoD.rotation, { z: 2.6, duration: 0.25, ease: "back.out(2)" }, ct.t0 + 0.1);
  tl.to(bracoE.rotation, { z: -2.6, duration: 0.25, ease: "back.out(2)" }, ct.t0 + 0.1);
  mostra(dom('<div id="prova" class="hud">PROVA</div>'), ct.t0 + 0.05, null);
  mostra(dom('<div id="cta" class="hud">Salve e teste<br>na próxima aula</div>'), ct.t0 + 0.3, null);

  // ------------------------------------------------------------------ movimentos procedurais (função do tempo)
  const n2 = (n) => String(Math.max(0, n)).padStart(2, "0");
  for (const st of vis.values()) st.ev.sort((a, b) => a[0] - b[0]);
  quadro.push((t) => {
    for (const [ob, st] of vis) { let v = st.ini; for (const [te0, ve] of st.ev) if (t >= te0) v = ve; ob.visible = v; }
    papel.material = t >= tw ? cinza : M.white;
    const corre = t < tDesce ? 1 : 0;                          // passo de corrida no gancho
    prof.children[0].position.y = corre * Math.abs(Math.sin(t * 11)) * 0.16 + (t >= T.c4.t0 && t < T.c5.t0 ? Math.abs(Math.sin(t * 6)) * 0.05 : 0);
    if (t < p.t0) { bracoE.rotation.x = corre * Math.sin(t * 11) * 0.9; bracoD.rotation.x = -corre * Math.sin(t * 11) * 0.9; }
    else { bracoE.rotation.x = 0; bracoD.rotation.x = 0; }
    let s = 9;
    if (t < g.t1) s = 9 - Math.floor(((t - g.t0) / (g.t1 - g.t0)) * 2.99);
    else if (t < te.t0) s = 7;
    else s = 7 - Math.floor(((t - te.t0) / (boom - te.t0)) * 7.99);
    relogio.textContent = "00:" + n2(s);
    const u = t - boom;                                        // tremor da explosão
    const f = u > 0 && u < 1.3 ? (1 - u / 1.3) * 0.22 : 0;
    olho.dx = Math.sin(u * 47) * f; olho.dy = Math.cos(u * 61) * f;
    bomba.children[1].scale.setScalar(1 + Math.sin(t * 5) * 0.06);
  });
  k.pronto();
}
