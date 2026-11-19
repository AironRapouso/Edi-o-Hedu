"""Fila de montagem: monta e confere todo episódio cujo plan.json é mais novo que o mp3.
Uso: python runner.py   (para quando existir o arquivo STOP nesta pasta; resultados em queue.log)"""
import json, pathlib, subprocess, sys, time

here = pathlib.Path(__file__).parent
root = here.parent
log = here / 'queue.log'


def run(script, ep):
    r = subprocess.run([sys.executable, '-X', 'utf8', str(here / script), str(ep)], cwd=here,
                       capture_output=True, text=True, encoding='utf8', errors='replace')
    return r.returncode, (r.stdout if r.returncode == 0 else r.stdout + r.stderr[-1500:])


def pending():
    out = []
    for pj in sorted(root.glob('EP_*/edit/plan.json')):
        ep = pj.parent.parent
        if not (ep / 'edit/segments.json').exists():
            continue
        try:
            name = json.load(open(pj, encoding='utf8'))['name']
        except Exception:
            continue
        mp3 = ep / 'out' / f'{name}.mp3'
        if not mp3.exists() or mp3.stat().st_mtime < pj.stat().st_mtime:
            out.append(ep)
    return out


failed = {}   # episódio -> mtime do plano que falhou (só tenta de novo quando o plano mudar)
while not (here / 'STOP').exists():
    todo = [e for e in pending() if failed.get(e) != (e / 'edit/plan.json').stat().st_mtime]
    if not todo:
        time.sleep(15)
        continue
    ep = todo[0]
    t = time.time()
    code, out = run('build.py', ep)
    text = ['', f'##### {ep.name} {time.strftime("%H:%M")}', out.strip()]
    if 'FALHOU' in out or code:
        failed[ep] = (ep / 'edit/plan.json').stat().st_mtime
        text.append('>>> FALHOU; corrija o plan.json')
    else:
        for sc in ('verify_narr.py', 'verify_edges.py'):
            text.append(run(sc, ep)[1].strip())
    text.append(f'({time.time() - t:.0f}s)')
    with open(log, 'a', encoding='utf8') as f:
        f.write(chr(10).join(text) + chr(10))
