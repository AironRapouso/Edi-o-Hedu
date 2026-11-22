// Prévia rápida: desenha um quadro no meio de cada cena (ou nos tempos dados) e monta uma folha de contato.
// Uso: node prever.js [pasta do vídeo] [t1 t2 ...]   ->   out/previa/folha.jpg   (precisa do Playwright)
const { chromium } = require("playwright");
const http = require("http"), fs = require("fs"), path = require("path"), { execFileSync } = require("child_process");
const raiz = path.resolve(process.argv[2] || "."), hf = path.join(raiz, "hf"), out = path.join(raiz, "out", "previa");
const TIPO = { ".html": "text/html", ".js": "text/javascript", ".json": "application/json", ".woff2": "font/woff2", ".ttf": "font/ttf" };
(async () => {
  fs.rmSync(out, { recursive: true, force: true }); fs.mkdirSync(out, { recursive: true });
  const srv = http.createServer((q, r) => {
    const f = path.join(hf, decodeURIComponent(q.url.split("?")[0]));
    if (!f.startsWith(hf) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end(); }
    r.writeHead(200, { "content-type": TIPO[path.extname(f)] || "application/octet-stream" }); fs.createReadStream(f).pipe(r);
  }).listen(0);
  const b = await chromium.launch({ args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  const erros = [];
  p.on("console", (m) => { if (m.type() === "error") erros.push(m.text()); });
  p.on("pageerror", (e) => erros.push(String(e)));
  await p.goto(`http://127.0.0.1:${srv.address().port}/index.html`);
  await p.evaluate(() => window.__hf.buildReady.cenas);
  const A = await p.evaluate(() => window.ANIM);
  const dados = process.argv.slice(3).map(Number).filter((x) => !isNaN(x));
  const tempos = dados.length ? dados : A.cenas.flatMap((c) => [c.t0 + (c.t1 - c.t0) * 0.3, c.t0 + (c.t1 - c.t0) * 0.85]);
  let i = 0;
  for (const t of tempos) {
    await p.evaluate((t) => { window.tl.time(t, false); }, Math.min(t, A.total - 0.01));
    await p.screenshot({ path: path.join(out, `q${String(i++).padStart(3, "0")}.jpg`), quality: 80 });
  }
  if (await p.$("#err3d")) erros.push(await p.$eval("#err3d", (e) => e.textContent));
  await b.close(); srv.close();
  const col = Math.min(8, tempos.length), lin = Math.ceil(tempos.length / col);
  execFileSync("ffmpeg", ["-v", "error", "-y", "-pattern_type", "glob", "-i", path.join(out, "q*.jpg"), "-vf", `scale=270:480,tile=${col}x${lin}:padding=4`, "-frames:v", "1", "-q:v", "3", path.join(out, "folha.jpg")]);
  console.log(`prévia: ${tempos.length} quadros (${tempos.map((t) => t.toFixed(1)).join(" ")}) -> ${path.join(out, "folha.jpg")}`);
  if (erros.length) { console.log("ERROS:\n" + [...new Set(erros)].join("\n")); process.exit(1); }
})();
