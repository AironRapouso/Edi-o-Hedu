"""Gera as falas da narradora (edge-tts, voz Francisca pt-BR).  Uso: python tts_edge.py <pasta do episódio> [chave ...]
Sem chaves, gera só o que falta ou cujo texto mudou."""
import asyncio, json, os, pathlib, sys
import edge_tts
from common import VOICE, RATE, block_lines

EP = pathlib.Path(sys.argv[1])
plan = json.load(open(EP / 'edit/plan.json', encoding='utf8'))
lines = block_lines(plan)
out = EP / 'edit/tts'
out.mkdir(exist_ok=True)
stamp = out / 'lines.json'
old = json.load(open(stamp, encoding='utf8')) if stamp.exists() else {}
only = set(sys.argv[2:])


async def main():
    for key, text in lines.items():
        f = out / f'{key}.mp3'
        if f.exists() and old.get(key) == text and key not in only:
            continue
        for attempt in range(4):
            try:
                await edge_tts.Communicate(text, VOICE, rate=RATE, proxy=os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')).save(str(f))
                break
            except Exception as e:   # serviço gratuito: às vezes derruba a conexão
                if attempt == 3:
                    raise
                await asyncio.sleep(3)
    for f in out.glob('*.mp3'):
        if f.stem not in lines:
            f.unlink(); (out / f'{f.stem}.wav').unlink(missing_ok=True)
    json.dump(lines, open(stamp, 'w', encoding='utf8'), ensure_ascii=False, indent=1)

asyncio.run(main())
print(EP.name, 'narração ok:', len(lines), 'falas,', sum(map(len, lines.values())), 'caracteres')
