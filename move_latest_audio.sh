#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -ne 1 ]; then
  echo "Usage: ./move_latest_audio.sh path/inside/audio/ege/file.mp3"
  echo "Example: ./move_latest_audio.sh task3/variant01/q1.mp3"
  exit 1
fi

DEST_REL="$1"
DEST="$(pwd)/frontend/public/audio/ege/$DEST_REL"

SRC="$(ls -t "$HOME"/Downloads/*.{mp3,wav,m4a,mp4,ogg,aac} 2>/dev/null | head -n 1 || true)"

if [ -z "$SRC" ]; then
  echo "No audio file found in ~/Downloads"
  exit 1
fi

mkdir -p "$(dirname "$DEST")"
mv -f "$SRC" "$DEST"

echo "Moved:"
echo "  from: $SRC"
echo "  to:   $DEST"
