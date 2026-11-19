#!/usr/bin/env bash
# Renderiza os três cortes 9:16 um depois do outro (nunca em paralelo) e normaliza cada um em -14 LUFS.
# Rode de dentro da pasta vert do episódio:  bash render_all.sh EP9
# Variáveis: HF (comando do HyperFrames), HF_CACHE (pasta de cache, padrão ~/hf-cache), CORTES (lista "c1 nome c2 nome ...")
set -u
EP="${1:?uso: bash render_all.sh EPnn}"
HF="${HF:-npx --yes hyperframes@0.8.158}"
HF_CACHE="${HF_CACHE:-$HOME/hf-cache}"
export TMPDIR="${TMPDIR:-$HF_CACHE/tmp}" HF_SEGMENTED_CAPTURE=true
mkdir -p "$TMPDIR"
cd "$(dirname "$0")"
python3 -X utf8 build_vert.py || exit 1
# nomes dos arquivos finais: edite junto com a tabela CUTS do build_vert.py
CORTES="${CORTES:-c1 chamamento c2 corte2 c3 corte3}"
set -- $CORTES
while [ $# -ge 2 ]; do
  c=$1; name=$2; shift 2
  mkdir -p ../../shorts; out="../../shorts/${EP}_short${c#c}_${name}_9x16.mp4"
  ( cd "$c" && $HF render . --fps 30 --quality looks --low-memory-mode --frames-cache-dir "$HF_CACHE/${EP}-vert-$c" -o "../${c}_raw.mp4" > render.log 2>&1 ) || { echo "FALHOU $c (veja $c/render.log)"; exit 1; }
  python3 -X utf8 loudnorm.py "${c}_raw.mp4" "$out" && echo "OK $out"
done
