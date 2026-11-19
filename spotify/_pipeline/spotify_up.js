// Publica o episódio de índice I (lista _publicar.json) no assistente do Spotify for Creators já aberto.
const sleep = ms => new Promise(r => setTimeout(r, ms));
const has = t => document.body.innerText.includes(t);
const btn = t => [...document.querySelectorAll('button')].find(b => b.innerText.trim() === t);
const d = await fetch('http://127.0.0.1:8765/_publicar.json').then(r => r.json());
const e = d[I];
const name = e.mp3.split(/[\\/]/).pop();
const log = { n: e.n, title: e.title };

if (PHASE === 'fill') {
  let inp;
  for (let k = 0; k < 60 && !(inp = document.querySelector('input[type=file]')); k++) await sleep(250);
  const b = await fetch('http://127.0.0.1:8765/' + encodeURIComponent(name)).then(r => r.blob());
  const dt = new DataTransfer();
  dt.items.add(new File([b], name, { type: 'audio/mpeg' }));
  inp.files = dt.files;
  inp.dispatchEvent(new Event('change', { bubbles: true }));
  log.size = b.size;
  let t;
  for (let k = 0; k < 120 && !(t = document.querySelector('input[placeholder*="nome ao seu"]')); k++) await sleep(250);
  const set = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set;
  set.call(t, e.title);
  t.dispatchEvent(new Event('input', { bubbles: true }));
  const ed = document.querySelector('[contenteditable="true"]');
  for (let k = 0; k < 6 && ed.innerText.length < 100; k++) {
    ed.focus(); await sleep(400);
    const sel = getSelection(); sel.selectAllChildren(ed); sel.collapseToEnd(); await sleep(300);
    const c = new DataTransfer(); c.setData('text/plain', e.description);
    ed.dispatchEvent(new InputEvent('beforeinput', { inputType: 'insertFromPaste', dataTransfer: c, bubbles: true, cancelable: true }));
    await sleep(900);
  }
  log.titleOk = t.value === e.title;
  log.descLen = ed.innerText.length; log.expected = e.description.length;
  return log;
}

// PHASE === 'publish'
const t = document.querySelector('input[placeholder*="nome ao seu"]');
const ed = document.querySelector('[contenteditable="true"]');
if (!t || t.value !== e.title || !ed || ed.innerText.length < e.description.length * 0.9) return { ...log, err: 'FORM_NOT_FILLED' };
let k = 0;
while (!has('Prévia pronta') && k < 90) { await sleep(250); k++; }
if (!has('Prévia pronta')) return { ...log, state: 'NOT_READY' };
btn('Próximo').click(); await sleep(2200);
const lab = [...document.querySelectorAll('label')].find(l => l.innerText.trim() === 'Agora');
(lab.querySelector('input') || lab).click(); await sleep(600);
log.agora = [...document.querySelectorAll('input[type=radio]')].map(r => r.checked)[0];
if (!log.agora) return { ...log, err: 'AGORA_NOT_SET' };
btn('Publicar').click();
let j = 0;
while (!has('Episódio publicado') && j < 80) { await sleep(250); j++; }
log.published = has('Episódio publicado');
return log;
