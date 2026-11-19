#!/usr/bin/env bash
# Renderiza o vídeo longo de um episódio (composição em episodios/EPnn/edit/hf) e gera o arquivo final com o áudio tratado.
#
#   bash scripts/render_longo.sh EP9            # render completo
#   RESUME=1 bash scripts/render_longo.sh EP9   # retoma um render interrompido (só se a composição NÃO mudou)
#
# Variáveis: HF (comando do HyperFrames), HF_CACHE (cache de quadros, padrão ~/hf-cache; use um disco com espaço).
set -euo pipefail
EP="${1:?uso: bash scripts/render_longo.sh EPnn}"
REPO="$(cd "$(dirname "$0")/.." && pwd)"
E="$REPO/episodios/$EP/edit"
HF="${HF:-npx --yes hyperframes@0.8.158}"
HF_CACHE="${HF_CACHE:-$HOME/hf-cache}"
export TMPDIR="${TMPDIR:-$HF_CACHE/tmp}" HF_SEGMENTED_CAPTURE=true
mkdir -p "$TMPDIR"

cd "$E/hf"
python3 -X utf8 build.py
EXTRA=""; [ "${RESUME:-0}" = "1" ] && EXTRA="--resume"
$HF render . --fps 30 --quality looks --low-memory-mode --frames-cache-dir "$HF_CACHE/$EP-longo" $EXTRA -o ../final_raw.mp4 2>&1 | tee render.log
if grep -q "HDR auto-promotion" render.log; then echo "ATENÇÃO: há imagem HDR na composição; converta para bt709 e renderize de novo."; exit 1; fi

cd "$E"
python3 -X utf8 audio/sound.py            # voz tratada + efeitos + vinheta, -14 LUFS -> ../EPnn_final.mp4
python3 -X utf8 qa.py "../${EP}_final.mp4" audio_raw.wav
python3 -X utf8 make_srt.py "$E/../${EP}_legendas.srt"
echo "Pronto: episodios/$EP/${EP}_final.mp4 (olhe as folhas de contato em edit/verify/qa)"
