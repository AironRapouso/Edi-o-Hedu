#!/usr/bin/env bash
# Renderiza o vídeo animado e junta a narração.  Uso: bash render.sh [pasta do vídeo]   ->   out/final.mp4
set -euo pipefail
D="$(cd "${1:-.}" && pwd)"
HF="${HF:-npx --yes hyperframes@0.8.158}"
cd "$D/hf"
$HF render . --fps 30 --quality looks -o ../out/video_mudo.mp4 2>&1 | tee ../out/render.log
ffmpeg -v error -y -i ../out/video_mudo.mp4 -i ../out/narracao.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest ../out/final.mp4
ffprobe -v error -show_entries format=duration:stream=codec_type -of csv=p=0 ../out/final.mp4 | tr '\n' ' '; echo "-> $D/out/final.mp4"
