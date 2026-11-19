#!/usr/bin/env bash
# Cria a pasta de trabalho de um episódio novo a partir do modelo do vídeo longo (modelos/longo).
#
#   bash scripts/novo_episodio.sh EP9 /caminho/da/gravacao.mp4
#
# Resultado: episodios/EP9/ com raw/source.mp4, edit/ (scripts já renomeados para EP9), hf/assets
# (fontes, three.js, gsap, vinheta), thumbnail/ e shorts/capas/src/ prontos para editar.
set -euo pipefail
EP="${1:?uso: bash scripts/novo_episodio.sh EPnn /caminho/da/gravacao.mp4}"
SRC="${2:-}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
DST="$REPO/episodios/$EP"
[ -e "$DST" ] && { echo "já existe: $DST"; exit 1; }

mkdir -p "$DST"/{raw,edit/transcripts,edit/hf/assets,edit/audio,edit/vert,thumbnail,shorts/capas/src/fonts,spotify,upload}

# scripts do vídeo longo e dos shorts
cp "$REPO"/modelos/longo/*.py "$DST/edit/"
cp "$REPO"/modelos/longo/audio/*.py "$DST/edit/audio/"
cp "$REPO"/modelos/longo/hf/* "$DST/edit/hf/"
cp "$REPO"/modelos/longo/vert/* "$DST/edit/vert/"

# recursos da composição
cp -r "$REPO/assets/fonts" "$REPO/assets/three" "$DST/edit/hf/assets/"
cp "$REPO/assets/gsap.min.js" "$REPO/assets/vinheta.mp4" "$DST/edit/hf/assets/"

# fonte monoespaçada das legendas (o modelo usa "consolab.ttf"; a Consolas é da Microsoft e não vem no repositório)
MONO="${MONO_FONT:-}"
if [ -z "$MONO" ] && command -v fc-match >/dev/null; then MONO="$(fc-match -f '%{file}' 'DejaVu Sans Mono:bold')"; fi
if [ -n "$MONO" ] && [ -f "$MONO" ]; then cp "$MONO" "$DST/edit/hf/assets/fonts/consolab.ttf"
else echo "AVISO: sem fonte mono; instale fonts-dejavu-core ou passe MONO_FONT=/caminho/fonte.ttf"; fi

# thumbnail e capas (modelo azul do vídeo longo)
cp "$REPO/modelos/thumbnail/longo_azul/thumb.html" "$DST/thumbnail/"
cp "$REPO/assets/compass.png" "$REPO/assets/fonts/Inter-700-latin.woff2" "$REPO/assets/fonts/bebas-neue-latin-400-normal.woff2" "$DST/thumbnail/"
cp "$REPO"/modelos/thumbnail/capas_shorts/*.html "$REPO/assets/compass.png" "$DST/shorts/capas/src/"
cp "$REPO/assets/fonts/Inter-700-latin.woff2" "$REPO/assets/fonts/bebas-neue-latin-400-normal.woff2" "$DST/shorts/capas/src/fonts/"

# nomes de arquivo do modelo (EP7) -> episódio novo
grep -rlZ "EP7" "$DST/edit" --include=*.py --include=*.sh | xargs -0 -r sed -i "s/EP7/$EP/g"

if [ -n "$SRC" ]; then cp "$SRC" "$DST/raw/source.mp4"; fi
echo "Pronto: $DST"
echo "Próximo passo: cd $DST/edit && python3 -X utf8 whisper_transcribe.py ../raw/source.mp4 transcripts/$EP.json"
