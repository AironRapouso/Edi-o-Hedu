#!/usr/bin/env bash
# Cria a pasta de trabalho de um Reel avulso (modelo: modelos/reels, o visual de painel 3D + rosto).
#
#   bash scripts/novo_reel.sh REELS_4 /caminho/do/take_vertical.mp4
set -euo pipefail
NOME="${1:?uso: bash scripts/novo_reel.sh REELS_N /caminho/do/take.mp4}"
SRC="${2:-}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
DST="$REPO/episodios/$NOME/edit"
[ -e "$DST" ] && { echo "já existe: $DST"; exit 1; }
mkdir -p "$DST"/{raw,transcripts,hf/assets,audio,capa/hf}
cp "$REPO"/modelos/reels/*.py "$DST/"
cp "$REPO"/modelos/reels/hf/* "$DST/hf/"
cp "$REPO"/modelos/reels/audio/*.py "$DST/audio/"
cp "$REPO/modelos/reels/capa/make_cover.py" "$DST/capa/"
cp "$REPO/modelos/reels/capa/hf/index.html" "$DST/capa/hf/"
cp -r "$REPO/assets/fonts" "$REPO/assets/three" "$DST/hf/assets/"
cp "$REPO/assets/gsap.min.js" "$REPO/assets/astronauta.js" "$DST/hf/assets/"
MONO="${MONO_FONT:-}"
if [ -z "$MONO" ] && command -v fc-match >/dev/null; then MONO="$(fc-match -f '%{file}' 'DejaVu Sans Mono:bold')"; fi
[ -n "$MONO" ] && [ -f "$MONO" ] && cp "$MONO" "$DST/hf/assets/fonts/consolab.ttf"
[ -n "$SRC" ] && cp "$SRC" "$DST/raw/source.mp4"
echo "Pronto: $DST"
