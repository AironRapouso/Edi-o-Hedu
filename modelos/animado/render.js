// Render do vídeo animado: posiciona a timeline quadro a quadro, fotografa a página e envia ao ffmpeg.
// Grava em trechos (out/trechos/NNN.mp4): se for interrompido, rodar de novo continua de onde parou.
// Uso: node render.js [pasta do vídeo]   ->   out/video_mudo.mp4   (precisa do Playwright e do ffmpeg)
const { chromium } = require("playwright");
const http = require("http"), fs = require("fs"), path = require("path"), crypto = require("crypto"), { spawn, execFileSync } = require("child_process");
const raiz = path.resolve(process.argv[2] || "."), hf = path.join(raiz, "hf"), out = path.join(raiz, "out"), dir = path.join(out, "trechos");
const TRECHO = 150;                                                    // quadros por trecho (5 s)
const TIPO = { ".html": "text/html", ".js": "text/javascript", ".json": "application/json", ".woff2": "font/woff2", ".ttf": "font/ttf" };
(async () => {
  // os trechos só valem para esta versão exata das cenas e dos tempos
  const h = crypto.createHash("sha1");
  for (const f of ["index.html", "cenas.js", "kit.js"]) h.update(fs.readFileSync(path.join(hf, f)));
  const marca = h.digest("hex"), fm = path.join(dir, "versao.txt");
  if (!fs.existsSync(fm) || fs.readFileSync(fm, "utf8") !== marca) { fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir, { recursive: true }); fs.writeFileSync(fm, marca); }

  const srv = http.createServer((q, r) => {
    const f = path.join(hf, decodeURIComponent(q.url.split("?")[0]));
    if (!f.startsWith(hf) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { r.writeHead(404); return r.end(); }
    r.writeHead(200, { "content-type": TIPO[path.extname(f)] || "application/octet-stream" }); fs.createReadStream(f).pipe(r);
  }).listen(0);
  const b = await chromium.launch({ args: ["--use-gl=angle", "--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
  const p = await b.newPage({ viewport: { width: 1080, height: 1920 } });
  const erros = [];
  p.on("pageerror", (e) => erros.push(String(e)));
  await p.goto(`http://127.0.0.1:${srv.address().port}/index.html`);
  await p.evaluate(() => window.__hf.buildReady.cenas);
  const A = await p.evaluate(() => window.ANIM);
  const total = Math.round(A.total * A.fps), n = Math.ceil(total / TRECHO), ini = Date.now();
  let feitos = 0;
  for (let k = 0; k < n; k++) {
    const arq = path.join(dir, String(k).padStart(3, "0") + ".mp4");
    if (fs.existsSync(arq)) continue;
    const ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-framerate", String(A.fps), "-c:v", "mjpeg", "-i", "-",
      "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p", "-g", String(A.fps), arq + ".parcial.mp4"], { stdio: ["pipe", "inherit", "inherit"] });
    const fim = new Promise((ok, erro) => ff.on("close", (c) => (c === 0 ? ok() : erro(new Error("ffmpeg saiu com " + c)))));
    for (let i = k * TRECHO; i < Math.min(total, (k + 1) * TRECHO); i++) {
      await p.evaluate((t) => { window.tl.time(t, false); }, i / A.fps);
      const jpg = await p.screenshot({ type: "jpeg", quality: 95 });
      if (!ff.stdin.write(jpg)) await new Promise((r) => ff.stdin.once("drain", r));
      feitos++;
    }
    ff.stdin.end(); await fim;
    fs.renameSync(arq + ".parcial.mp4", arq);
    const s = (Date.now() - ini) / 1000;
    console.log(`trecho ${k + 1}/${n} | ${(s / feitos).toFixed(2)} s por quadro | faltam ~${Math.round((s / feitos) * (total - (k + 1) * TRECHO) / 60)} min`);
    if (erros.length) break;
  }
  await b.close(); srv.close();
  if (erros.length) { console.log("ERROS:\n" + [...new Set(erros)].join("\n")); process.exit(1); }
  const lista = path.join(dir, "lista.txt");
  fs.writeFileSync(lista, Array.from({ length: n }, (_, k) => `file '${String(k).padStart(3, "0")}.mp4'`).join("\n"));
  execFileSync("ffmpeg", ["-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lista, "-c", "copy", path.join(out, "video_mudo.mp4")]);
  console.log(`render: ${total} quadros -> ${path.join(out, "video_mudo.mp4")}`);
})();
