"""Monta um ou mais episódios de ponta a ponta: narração -> mixagem/master -> descrição.
Uso: python build.py <pasta do episódio> [...]   (a conferência da narradora é o verify_narr.py)"""
import pathlib, subprocess, sys, time

here = pathlib.Path(__file__).parent
for ep in sys.argv[1:]:
    t = time.time()
    for script in ('tts_edge.py', 'mix.py'):
        r = subprocess.run([sys.executable, '-X', 'utf8', str(here / script), ep], cwd=here,
                           capture_output=True, text=True, encoding='utf8')
        if r.returncode:
            print(f'FALHOU {ep} em {script}:\n{r.stderr[-1500:]}', flush=True)
            break
        print(r.stdout.strip().splitlines()[-1], flush=True)
    else:
        print(f'   ({time.time() - t:.0f}s)', flush=True)
