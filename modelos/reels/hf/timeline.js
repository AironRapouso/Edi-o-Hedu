// REELS 3 — DOM side of the timeline (face framing, full-screen cover, pill captions word by word, CTA card).
// The 3D scenes add their own tweens to this same timeline from scene3d.js (a module, so it runs later):
// the build-ready promise below keeps HyperFrames from capturing before they exist.
window.__timelines = window.__timelines || {};
window.__hf = window.__hf || {};
window.__hf.buildReady = window.__hf.buildReady || {};
window.__hf.buildReady.scene3d = new Promise((resolve) => { window.__scene3dReady = resolve; });

const D = window.REEL;
const tl = gsap.timeline({ paused: true });
window.tl = tl;
const S = (i) => D.T.S[i];
const E = (i) => D.T.E[i];

// ---- face panel: the framing is a pure function of the frame number (build.py computed one transform per frame
// from the tracked eye line: same spot after every jump cut, hard punch-ins, 60 % of his slow drift taken out)
const zoomEl = document.getElementById("zoom");
function faceAt(t) {
  const i = Math.min(D.face.length - 1, Math.max(0, Math.floor(t * 30 + 0.01)));
  const f = D.face[i];
  zoomEl.style.transform = "translate(" + f[0] + "px, " + f[1] + "px) scale(" + f[2] + ")";
}
window.__faceAt = faceAt;
window.addEventListener("hf-seek", (e) => faceAt(e.detail && typeof e.detail.time === "number" ? e.detail.time : tl.time()));
tl.eventCallback("onUpdate", () => faceAt(tl.time()));   // scene3d.js replaces this callback with one that also calls faceAt
faceAt(0);

// ---- full-screen cover (paper wipes down over the face, twice)
tl.set("#cover", { scaleY: 0 }, 0);
tl.fromTo("#cover", { scaleY: 0 }, { scaleY: 1, duration: 0.26, ease: "power3.inOut" }, D.T.fs1 - 0.06);
tl.to("#cover", { scaleY: 0, duration: 0.26, ease: "power3.inOut" }, D.T.sc3 - 0.02);
tl.to("#cover", { scaleY: 1, duration: 0.26, ease: "power3.inOut" }, D.T.fs2 - 0.06);
tl.to("#cover", { scaleY: 0, duration: 0.26, ease: "power3.inOut" }, D.T.sc5 - 0.02);

// ---- captions: the pill pops in with the whole chunk dimmed, each word lights up (and pops) when he says it
D.caps.forEach((c) => {
  tl.fromTo("#" + c.id + " .pill", { opacity: 0.55, scale: 0.88, y: 7 }, { opacity: 1, scale: 1, y: 0, duration: 0.13, ease: "back.out(2.2)" }, c.s);   // never a frame without the pill
  c.w.forEach((w, k) => {
    tl.set("#" + w.id, { opacity: 1 }, w.t);
    if (k) tl.fromTo("#" + w.id, { scale: 1.1, y: -5 }, { scale: 1, y: 0, duration: 0.15, ease: "power2.out", immediateRender: false }, w.t);
  });
});

// ---- CTA card
const T5 = D.T.sc5;
tl.fromTo("#cta", { opacity: 0, x: 70, scale: 0.94 }, { opacity: 1, x: 0, scale: 1, duration: 0.34, ease: "back.out(1.5)" }, T5 - 0.1);   // already sliding in at the cut
tl.fromTo("#cta .ask", { opacity: 0, x: -18 }, { opacity: 1, x: 0, duration: 0.22, ease: "power3.out" }, T5 + 0.08);
tl.fromTo("#cta .qq", { opacity: 0, y: 16 }, { opacity: 1, y: 0, duration: 0.26, ease: "power3.out" }, S(47) - 0.03);
tl.fromTo("#field", { opacity: 0, y: 18 }, { opacity: 1, y: 0, duration: 0.24, ease: "power3.out" }, S(50) + 0.1);
tl.set("#cur", { opacity: 0 }, 0);
tl.set("#ph", { opacity: 0 }, D.typed[0]);
tl.set("#cur", { opacity: 1 }, D.typed[0]);
tl.to("#field", { borderColor: "#0457E7", duration: 0.15 }, D.typed[0]);
D.typed.forEach((t, k) => tl.set("#ty" + k, { display: "inline" }, t));
tl.to("#field", { borderColor: "#F4B04A", backgroundColor: "#FFF6E3", duration: 0.2 }, E(55) + 0.02);
tl.fromTo("#send", { scale: 1 }, { scale: 1.28, duration: 0.11, yoyo: true, repeat: 3, ease: "power2.out" }, E(55) + 0.02);
tl.fromTo("#fol", { scale: 1 }, { scale: 1.14, duration: 0.12, yoyo: true, repeat: 1, ease: "power2.out" }, E(55) + 0.2);
tl.to("#fola", { opacity: 0, duration: 0.1 }, E(55) + 0.3);

window.__timelines.main = tl;
