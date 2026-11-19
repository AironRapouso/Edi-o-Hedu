"""Mostra as palavras com tempo num intervalo.  Uso: python w.py <pasta do episódio> t0 t1 [t0 t1 ...]"""
import json, pathlib, sys

EP = pathlib.Path(sys.argv[1])
words = json.load(open(EP / 'edit/transcripts/source.json', encoding='utf8'))['words']
a = list(map(float, sys.argv[2:]))
for t0, t1 in zip(a[::2], a[1::2]):
    print(f'-- {t0}-{t1}:', ' '.join(f"{w['text']}[{w['start']:.2f}]" for w in words if t0 <= w['start'] <= t1))
