#!/usr/bin/env bash
# Installiert alles, was zum Vertonen einer Folge noetig ist.
# Aufruf aus dem Repository-Wurzelverzeichnis:  bash tools/setup.sh
set -euo pipefail

MODELS="${PODCAST_MODELS:-$HOME/.cache/spanisch-podcast-models}"
mkdir -p "$MODELS"

python3 -c "import sherpa_onnx, soundfile, numpy" 2>/dev/null || \
  pip install --quiet --break-system-packages "sherpa-onnx==1.13.8" soundfile numpy

command -v ffmpeg >/dev/null || { echo "FEHLER: ffmpeg fehlt"; exit 1; }

BASE=https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models
for v in vits-piper-es_MX-claude-high vits-piper-de_DE-thorsten-medium; do
  if [ ! -d "$MODELS/$v" ]; then
    echo "Lade Stimme $v ..."
    curl -sSL -o "$MODELS/$v.tar.bz2" "$BASE/$v.tar.bz2"
    tar xjf "$MODELS/$v.tar.bz2" -C "$MODELS"
    rm -f "$MODELS/$v.tar.bz2"
  fi
done
echo "Setup fertig. Stimmen in $MODELS"
