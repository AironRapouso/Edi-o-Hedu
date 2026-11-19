// Astronauta com o rosto do Dr. Hélio — substitui o robô nas cenas 3D (mesma interface: userData.head, arms, eyeM).
// Depende de: THREE, rbox, cyl, sph, sh, mat, basic, M (os mesmos ajudantes do scene3d.js).
export function makeAstronaut({ THREE, rbox, cyl, sph, sh, mat, basic, M: M0 }) {
  // cores da marca: Azul Institucional #031954 (traje), Azul Noturno #010B25 (detalhes), Dourado Luz #F4B04A (destaques)
  const NAVY = mat(0x031954, { r: 0.42, cc: 0.6 }), NIGHT = mat(0x010b25, { r: 0.4, cc: 0.7 });
  const M = { ...M0, white: NAVY, sky: M0.gold, blue: M0.gold, grey: NIGHT, navy: NIGHT };
  const SKIN = mat(0xd49c78, { r: 0.6, cc: 0.1 }), HAIR = mat(0x4b4e57, { r: 0.7, cc: 0.05 }), BEARD = mat(0xa7a9ad, { r: 0.8, cc: 0 });
  const RIM = mat(0x111318, { r: 0.35, cc: 0.8 }), DARK = mat(0x1b1d24, { r: 0.4 }), TEETH = mat(0xffffff, { r: 0.4 });
  const GLASS = new THREE.MeshPhysicalMaterial({ color: 0xcfe6ff, roughness: 0.05, metalness: 0, clearcoat: 1, transparent: true, opacity: 0.17, depthWrite: false });
  function head() {
    const h = new THREE.Group();
    const face = new THREE.Group();
    const skull = sph(0.78, SKIN); skull.scale.set(1, 1.08, 0.98);
    // cabelo grisalho escuro penteado para trás: calota + volume no topo
    // cabelo grisalho escuro penteado para trás: volumes sólidos (sem cascas abertas)
    // mesma frente e mesmo contorno de frente; só a profundidade encolheu: com z 1.0 em -0.3 a nuca do cabelo furava o casco (r até 1.34)
    const hair = sph(0.88, HAIR); hair.scale.set(1.0, 0.96, 0.75); hair.position.set(0, 0.36, -0.08);
    const tuft = sph(0.46, HAIR); tuft.scale.set(1.45, 0.55, 1.0); tuft.position.set(0, 0.78, 0.22); tuft.rotation.x = -0.3;
    [-1, 1].forEach((s) => { const side = sph(0.3, HAIR); side.scale.set(0.42, 1.0, 1.0); side.position.set(s * 0.74, 0.18, -0.02); face.add(side);
      const ear = sph(0.13, SKIN); ear.scale.set(0.5, 1, 0.8); ear.position.set(s * 0.79, -0.08, 0.05); face.add(ear); });
    // olhos, sobrancelhas, nariz
    [-0.27, 0.27].forEach((x) => { const e = sph(0.06, DARK); e.position.set(x, 0.1, 0.73); face.add(e);
      const b = rbox(0.24, 0.05, 0.05, 0.02, HAIR); b.position.set(x, 0.38, 0.7); b.rotation.z = x < 0 ? -0.1 : 0.1; face.add(b);
      const ring = sh(new THREE.Mesh(new THREE.TorusGeometry(0.2, 0.028, 12, 40), RIM)); ring.position.set(x, 0.1, 0.78); face.add(ring); });
    const bridge = cyl(0.022, 0.022, 0.16, RIM, 10); bridge.rotation.z = Math.PI / 2; bridge.position.set(0, 0.13, 0.8);
    [-1, 1].forEach((s) => { const t = cyl(0.02, 0.02, 0.5, RIM, 8); t.rotation.x = Math.PI / 2; t.position.set(s * 0.5, 0.12, 0.55); t.rotation.y = s * 0.25; face.add(t); });
    const nose = sph(0.1, SKIN); nose.scale.set(0.9, 1.1, 1.1); nose.position.set(0, -0.06, 0.8);
    // bigode e cavanhaque grisalhos, sorriso
    // bigode + cavanhaque numa peça só (contorno único com a abertura da boca)
    const bs = new THREE.Shape();
    bs.moveTo(0, 0.02); bs.bezierCurveTo(0.14, 0.07, 0.3, 0.05, 0.4, -0.07); bs.bezierCurveTo(0.36, -0.1, 0.33, -0.12, 0.3, -0.13);
    bs.bezierCurveTo(0.31, -0.3, 0.27, -0.5, 0.0, -0.56); bs.bezierCurveTo(-0.27, -0.5, -0.31, -0.3, -0.3, -0.13);
    bs.bezierCurveTo(-0.33, -0.12, -0.36, -0.1, -0.4, -0.07); bs.bezierCurveTo(-0.3, 0.05, -0.14, 0.07, 0, 0.02);
    const mouth = new THREE.Path(); mouth.absellipse(0, -0.2, 0.16, 0.075, 0, Math.PI * 2, true); bs.holes.push(mouth);
    const bg = new THREE.ExtrudeGeometry(bs, { depth: 0.07, bevelEnabled: true, bevelThickness: 0.035, bevelSize: 0.03, bevelSegments: 5, curveSegments: 28 });
    bg.translate(0, 0, -0.035);
    const goatee = new THREE.Group(); goatee.add(sh(new THREE.Mesh(bg, BEARD)));
    const smile = rbox(0.2, 0.05, 0.03, 0.02, TEETH); smile.position.set(0, -0.175, -0.012); goatee.add(smile);
    const lip = rbox(0.36, 0.2, 0.03, 0.08, mat(0x7a3b32, { r: 0.7, cc: 0 })); lip.position.set(0, -0.2, -0.04); goatee.add(lip);
    goatee.position.set(0, -0.2, 0.73); goatee.rotation.x = 0.5;
    face.add(skull, hair, tuft, bridge, nose, goatee);
    face.position.y = 0.02;
    // capacete: casco branco atrás, bolha de vidro, aro azul, fones laterais
    // casco e forro abertos num círculo plano em z = RING_Z, exatamente onde fica o aro (antes a abertura era um corte
    // vertical da esfera: a borda passava na frente do aro dos lados e aparecia como um filete escuro dentro do vidro)
    const RING_Z = 0.48;
    const openShell = (r) => new THREE.SphereGeometry(r, 56, 32, 0, Math.PI * 2, Math.acos(RING_Z / r), Math.PI - Math.acos(RING_Z / r)).rotateX(Math.PI / 2);
    const shell = sh(new THREE.Mesh(openShell(1.24), M.white));
    const lining = new THREE.Mesh(openShell(1.21), new THREE.MeshStandardMaterial({ color: 0x010b25, roughness: 0.9, side: THREE.BackSide }));
    const dome = new THREE.Mesh(new THREE.SphereGeometry(1.2, 56, 32), GLASS); dome.renderOrder = 5;
    const ringV = sh(new THREE.Mesh(new THREE.TorusGeometry(1.14, 0.075, 14, 64), M.sky)); ringV.position.z = RING_Z; ringV.scale.set(0.985, 1, 1);
    // fones do lado de fora do forro (em ±1.22 a face interna aparecia dentro do vidro, ao lado do rosto)
    [-1.3, 1.3].forEach((x) => { const cap = cyl(0.27, 0.27, 0.16, M.blue); cap.rotation.z = Math.PI / 2; cap.position.x = x; h.add(cap); });
    const eyeM = basic(0xffc85e);
    const lampH = new THREE.Mesh(new THREE.CircleGeometry(0.1, 24), eyeM); lampH.position.set(0, 1.12, 0.56); lampH.rotation.x = -0.45;
    h.add(face, lining, shell, dome, ringV, lampH);
    h.userData.eyeM = eyeM;
    return h;
  }
  const g = new THREE.Group();
  const hd = head(); hd.position.y = 3.3;
  const collar = sh(new THREE.Mesh(new THREE.TorusGeometry(0.62, 0.16, 14, 48), M.sky)); collar.rotation.x = Math.PI / 2; collar.position.y = 2.16;
  const body = rbox(2.0, 1.7, 1.35, 0.42, M.white); body.position.y = 1.28;
  const neck = cyl(0.34, 0.38, 0.62, SKIN, 32); neck.position.y = 2.36;
  const under = cyl(0.46, 0.56, 0.3, NIGHT, 32); under.position.y = 2.2;
  const pack = rbox(1.5, 1.5, 0.55, 0.2, M.grey); pack.position.set(0, 1.4, -0.85);
  const chest = rbox(1.1, 0.6, 0.08, 0.12, M.navy); chest.position.set(0, 1.42, 0.68);
  const lamp = new THREE.Mesh(new THREE.CircleGeometry(0.1, 24), basic(0xf4b04a)); lamp.position.set(0.32, 1.44, 0.725);
  const b1 = rbox(0.5, 0.09, 0.03, 0.03, M0.sky); b1.position.set(-0.2, 1.5, 0.725);
  const b2 = rbox(0.34, 0.09, 0.03, 0.03, M.gold); b2.position.set(-0.28, 1.33, 0.725);
  const belt = rbox(2.04, 0.2, 1.39, 0.08, M.blue); belt.position.y = 0.62;
  g.add(hd, neck, under, collar, body, pack, chest, lamp, b1, b2, belt);
  [-0.5, 0.5].forEach((x) => { const leg = cyl(0.33, 0.36, 0.42, M.white); leg.position.set(x, 0.36, 0); const boot = rbox(0.74, 0.26, 0.9, 0.12, M.navy); boot.position.set(x, 0.13, 0.08); g.add(leg, boot); });
  const arms = [-1, 1].map((sg) => {
    const pivot = new THREE.Group(); pivot.position.set(sg * 1.24, 1.9, 0.05);
    const arm = sh(new THREE.Mesh(new THREE.CapsuleGeometry(0.21, 0.7, 8, 20), M.white)); arm.position.y = -0.52;
    const cuff = cyl(0.23, 0.23, 0.1, M.sky, 24); cuff.position.y = -0.98;
    const glove = sph(0.24, M.navy); glove.position.y = -1.14;
    pivot.add(arm, cuff, glove); pivot.rotation.z = sg * 0.22; g.add(pivot); return pivot;
  });
  g.userData = { head: hd, arms, eyeM: hd.userData.eyeM };
  return g;
}
