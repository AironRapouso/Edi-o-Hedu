"""Junta os episódios prontos em SPOTIFY/PRONTOS_PARA_POSTAR (mp3 + descrição) e gera o INDICE.md,
na ordem de publicação do canal.  Uso: python export.py"""
import json, pathlib, shutil, subprocess
from common import FF

ROOT = pathlib.Path(__file__).parent.parent
OUT = ROOT / 'PRONTOS_PARA_POSTAR'
OUT.mkdir(exist_ok=True)

# os 5 primeiros foram feitos antes do pipeline em lote (nomes antigos)
OLD = {
    'EP_T6e8': ('01_EP01_O_Manifesto', 'T6e8GQTLWMY', 'EPISÓDIO 1 - O MANIFESTO', 'Episódio 1 — O Manifesto'),
    'EP_QBkm': ('02_Reflexao_O_diagnostico_que_falta_nas_escolas', 'QBkmxIYnCtU',
                'REFLEXÃO: O DIAGNÓSTICO QUE FALTA NAS ESCOLAS', 'Reflexão — O diagnóstico que falta nas escolas'),
    'EP_xcRV': ('03_EP02_A_escola_do_seculo_XXI_com_a_logica_do_seculo_XIX', 'xcRVziS3Cm8',
                'A Escola do Século XXI Ainda Funciona com a Lógica do Século XIX | Nova Ordem Educacional #2',
                'Episódio 2 — A escola do século XXI ainda funciona com a lógica do século XIX'),
    'EP_CeMc': ('04_EP03_A_primeira_infancia_decide_o_futuro_do_pais', 'Ce-McjwYLK0',
                'A primeira infância decide o futuro do país #3', 'Episódio 3 — A primeira infância decide o futuro do país'),
    'EP_qvtu': ('05_EP04_So_2_das_20_metas_educacionais_foram_cumpridas', 'qvtupBHPEVA',
                'Só 2 das 20 metas educacionais do Brasil foram cumpridas em 10 anos #4',
                'Episódio 4 — Só 2 das 20 metas educacionais do Brasil foram cumpridas em 10 anos'),
}


OLD_DATES = {'EP_T6e8': '24/07/2026', 'EP_QBkm': '28/07/2026', 'EP_xcRV': '31/07/2026',
             'EP_CeMc': '02/08/2026', 'EP_qvtu': '07/08/2026'}


def dur(p):
    r = subprocess.run([FF.replace('ffmpeg.exe', 'ffprobe.exe'), '-v', 'error', '-show_entries', 'format=duration',
                        '-of', 'csv=p=0', str(p)], capture_output=True, text=True)
    t = float(r.stdout.strip())
    return f'{int(t // 60)}:{int(t % 60):02d}'


rows, missing = [], []
for ep in sorted(p for p in ROOT.glob('EP_*') if p.is_dir()):
    if ep.name in OLD:
        name, yid, yt_title, title = OLD[ep.name]
        mp3 = next((ep / 'out').glob('*.mp3'))
        desc = (ep / 'out/descricao_spotify.txt').read_text(encoding='utf8').rstrip()
        if 'youtu.be' not in desc:
            desc = desc.replace('\nEducação é estratégia.', f'\nAssista em vídeo: https://youtu.be/{yid}\n\nEducação é estratégia.')
        date = OLD_DATES[ep.name]
    else:
        pj = ep / 'edit/plan.json'
        info = (ep / 'src/info.txt').read_text(encoding='utf8').strip().split(' | ') if (ep / 'src/info.txt').exists() else None
        if not pj.exists() or not info:
            missing.append(ep.name); continue
        plan = json.load(open(pj, encoding='utf8'))
        name, yid, title = plan['name'], plan['youtube_id'], plan['title']
        yt_title, date = info[3], f'{info[1][6:8]}/{info[1][4:6]}/{info[1][:4]}'
        mp3 = ep / 'out' / f'{name}.mp3'
        if not mp3.exists():
            missing.append(ep.name); continue
        desc = (ep / 'out' / f'{name}.txt').read_text(encoding='utf8').rstrip()
    dst = OUT / f'{name}.mp3'
    if not dst.exists() or dst.stat().st_mtime < mp3.stat().st_mtime:
        shutil.copy2(mp3, dst)
    (OUT / f'{name}.txt').write_text(desc + '\n', encoding='utf8')
    rows.append((name, date, yt_title, yid, title, dur(dst)))

rows.sort()
md = ['# A Nova Ordem Educacional — episódios prontos para o Spotify', '',
      'Cada episódio tem um `.mp3` (áudio final, −14 LUFS) e um `.txt` com o título, a descrição e os capítulos.',
      'A ordem é a mesma da publicação no YouTube. O WAV de cada um está na pasta `EP_xxxx/out`.', '',
      '| Nº | YouTube | Vídeo original | Duração | Título no Spotify | Arquivo |', '|---|---|---|---|---|---|']
for name, date, yt_title, yid, title, d in rows:
    yt = yt_title.replace('|', '·')
    md.append(f"| {name[:2]} | {date} | [{yt}](https://youtu.be/{yid}) | {d} | {title} | `{name}.mp3` |")
(OUT / 'INDICE.md').write_text('\n'.join(md) + '\n', encoding='utf8')
print(len(rows), 'episódios exportados para', OUT)
print('faltando:', ', '.join(missing) or 'nenhum')
