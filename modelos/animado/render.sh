#!/usr/bin/env bash
# Renderiza o vídeo animado e junta a narração.  Uso: bash render.sh [pasta do vídeo]   ->   out/final.mp4
# Interrompido? Rode de novo: continua do trecho em que parou.  MOTOR=hf usa o HyperFrames (só vale a pena com placa de vídeo).
set -euo pipefail
D="$(cd "${1:-.}" && pwd)"
cd "$D"
if [ "${MOTOR:-proprio}" = hf ]; then
  (cd hf && ${HF:-npx --yes hyperframes@0.8.158} render . --fps 30 --quality looks -o ../out/video_mudo.mp4)
else
  NODE_PATH="${NODE_PATH:-$(npm root -g)}" node render.js .
fi
ffmpeg -v error -y -i out/video_mudo.mp4 -i out/narracao.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest -movflags +faststart out/final.mp4
ffprobe -v error -show_entries format=duration:stream=codec_type -of csv=p=0 out/final.mp4 | tr '\n' ' '; echo "-> $D/out/final.mp4"
