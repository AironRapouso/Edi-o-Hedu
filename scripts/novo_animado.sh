#!/usr/bin/env bash
# Cria a pasta de um vídeo animado (sem gravação) a partir do modelo.  Uso: bash scripts/novo_animado.sh ANIM_2
set -euo pipefail
NOME="${1:?uso: bash scripts/novo_animado.sh ANIM_N}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
DST="$REPO/episodios/$NOME"
[ -e "$DST" ] && { echo "já existe: $DST"; exit 0; }
mkdir -p "$DST/hf"
cp "$REPO"/modelos/animado/{voz.py,build.py,prever.js,render.sh,roteiro.json} "$DST/"
cp "$REPO"/modelos/animado/hf/{kit.js,cenas.js} "$DST/hf/"
echo "Pronto: $DST"
