"""Narração do vídeo animado: uma fala por cena, na voz do Dr. Hélio.

Uso: python voz.py <pasta do vídeo> [--motor clone|provisoria] [--temp 1.4] [--vel 1.3] [--ref voz_ref.wav]

  clone       Chatterbox multilíngue (código aberto, MIT, roda na CPU, sem custo): copia a voz da amostra --ref.
  provisoria  o mesmo modelo com a voz padrão dele, para testar o vídeo enquanto não há amostra.

Cada fala é acelerada (--vel, sem mudar o tom), nivelada e conferida por transcrição local; a que sair diferente do
texto é gerada de novo. Saída: out/narracao.wav e out/words.json (tempo de cada palavra, usado na legenda e nas cenas).
"""
import argparse, difflib, hashlib, json, re, subprocess, unicodedata
from pathlib import Path

import numpy as np
import soundfile as sf

SR, PAUSA, FIM = 48000, 0.22, 0.7
TRIM = "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.03"


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    return re.sub(r"[^a-z0-9]", "", "".join(c for c in s if unicodedata.category(c) != "Mn"))


# o transcritor escreve números em algarismos ("48%"): eles ficam fora da nota, para não reprovar fala certa
NUMEROS = set("zero um uma dois duas tres quatro cinco seis sete oito nove dez onze doze treze quatorze catorze quinze dezesseis dezessete dezoito "
              "dezenove vinte trinta quarenta cinquenta sessenta setenta oitenta noventa cem cento mil e por".split())


def sem_numeros(tokens):
    return [x for x in tokens if x and x not in NUMEROS and not x.isdigit()]


def ff(*a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *a], check=True)


_tts = _asr = None


def gerar(texto, bruto, a, tentativa):
    global _tts
    import torch
    from chatterbox.mtl_tts import ChatterboxMultilingualTTS
    if _tts is None:
        carregar = torch.load                                              # os pesos foram salvos em GPU: abrir na CPU
        torch.load = lambda *x, **kw: carregar(*x, **{**kw, "map_location": torch.device("cpu")})
        _tts = ChatterboxMultilingualTTS.from_pretrained(device=torch.device("cpu"))
    torch.manual_seed(1000 + tentativa)
    ref = str(a.ref) if a.motor == "clone" else None        # sem amostra: voz padrão do modelo
    partes = [p for p in re.split(r"(?<=[.!?])\s+", texto) if p]          # frase a frase: o modelo erra menos
    ondas = [_tts.generate(p, language_id="pt", audio_prompt_path=ref, temperature=a.temp).squeeze(0).numpy() for p in partes]
    gap = np.zeros(int(_tts.sr * 0.16), dtype=np.float32)
    sf.write(bruto, np.concatenate([x for o in ondas for x in (o, gap)][:-1]), _tts.sr)


def ouvir(wav):
    global _asr
    if _asr is None:
        from faster_whisper import WhisperModel
        _asr = WhisperModel("small", device="cpu", compute_type="int8")
    segs, _ = _asr.transcribe(str(wav), language="pt", word_timestamps=True)
    return [(w.word, w.start, w.end) for s in segs for w in s.words]


def alinhar(texto, ouvidas, dur):
    """Tempo de cada palavra do roteiro: casa com o que foi ouvido e interpola o que não casou."""
    pal = texto.split()
    a, b = [norm(p) for p in pal], [norm(w) for w, _, _ in ouvidas]
    sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
    t = [None] * len(pal)
    for i, j, n in sm.get_matching_blocks():
        for k in range(n):
            t[i + k] = (ouvidas[j + k][1], ouvidas[j + k][2])
    conhecidos = [(-1, (0.0, 0.0))] + [(i, x) for i, x in enumerate(t) if x] + [(len(pal), (dur, dur))]
    for (i0, x0), (i1, x1) in zip(conhecidos, conhecidos[1:]):
        n = i1 - i0 - 1
        for k in range(n):
            s = x0[1] + (x1[0] - x0[1]) * k / n
            t[i0 + 1 + k] = (s, x0[1] + (x1[0] - x0[1]) * (k + 1) / n)
    nota = difflib.SequenceMatcher(None, sem_numeros(a), sem_numeros(b), autojunk=False).ratio()
    return nota, [{"w": p, "t0": round(x[0], 3), "t1": round(x[1], 3)} for p, x in zip(pal, t)]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("pasta"); p.add_argument("--motor", default="clone", choices=["clone", "provisoria"])
    p.add_argument("--temp", type=float, default=1.4); p.add_argument("--vel", type=float, default=1.3)
    p.add_argument("--ref", default=None); p.add_argument("--tentativas", type=int, default=4)
    a = p.parse_args()
    raiz = Path(a.pasta); out = raiz / "out" / "voz"; out.mkdir(parents=True, exist_ok=True)
    a.ref = Path(a.ref) if a.ref else raiz / "voz_ref.wav"
    if a.motor == "clone":
        assert a.ref.is_file(), f"falta a amostra de voz: {a.ref} (30 a 60 s, só a voz dele, sem música)"
    cenas = json.load(open(raiz / "roteiro.json", encoding="utf8"))["cenas"]
    trilha, saida, t = [], [], 0.0
    for c in cenas:
        chave = hashlib.sha1(f"{c['fala']}|{a.motor}|{a.temp}|{a.vel}".encode()).hexdigest()[:12]
        wav, meta = out / f"{c['id']}.wav", out / f"{c['id']}.json"
        m = json.load(open(meta, encoding="utf8")) if meta.exists() and wav.exists() else {}
        if m.get("chave") != chave:
            melhor = None
            for k in range(a.tentativas):
                bruto, cand = out / f"_{c['id']}_bruto.wav", out / f"_{c['id']}_{k}.wav"
                gerar(c["fala"], bruto, a, k)
                ff("-i", str(bruto), "-af", f"{TRIM},areverse,{TRIM},areverse,atempo={a.vel},loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", str(SR), "-ac", "1", str(cand))
                dur = sf.info(cand).duration
                nota, pal = alinhar(c["fala"], ouvir(cand), dur)
                print(f"  {c['id']} tentativa {k + 1}: confere {nota:.2f}, {dur:.1f} s", flush=True)
                if melhor is None or nota > melhor[0]:
                    melhor = (nota, pal, dur, cand)
                if nota >= 0.9:
                    break
            nota, pal, dur, cand = melhor
            cand.replace(wav)
            for f in out.glob(f"_{c['id']}_*"):
                f.unlink()
            m = {"chave": chave, "confere": round(nota, 3), "dur": round(dur, 3), "w": pal}
            json.dump(m, open(meta, "w", encoding="utf8"), ensure_ascii=False)
        x, _ = sf.read(wav, dtype="float32")
        trilha += [x, np.zeros(int(SR * PAUSA), dtype=np.float32)]
        saida.append({"id": c["id"], "t0": round(t, 3), "confere": m["confere"],
                      "w": [{"w": w["w"], "t0": round(t + w["t0"], 3), "t1": round(t + w["t1"], 3)} for w in m["w"]]})
        t += len(x) / SR + PAUSA
    total = round(t - PAUSA + FIM, 3)
    for c, n in zip(saida, saida[1:] + [{"t0": total}]):
        c["t1"] = n["t0"]
    trilha[-1] = np.zeros(int(SR * FIM), dtype=np.float32)
    sf.write(raiz / "out" / "narracao.wav", np.concatenate(trilha), SR)
    json.dump({"total": total, "motor": a.motor, "temp": a.temp, "vel": a.vel, "cenas": saida},
              open(raiz / "out" / "words.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    fracas = [c["id"] for c in saida if c["confere"] < 0.9]
    print(f"narração ok: {len(saida)} falas, {total:.1f} s" + (f" | conferir de ouvido: {', '.join(fracas)}" if fracas else ""))


main()
