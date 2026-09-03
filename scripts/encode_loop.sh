#!/bin/sh
# Encode a frame sequence from render_loop.js into the two loop formats (Brief 8, item 4).
# Usage: sh scripts/encode_loop.sh <frames-dir> <slug> [fps]
set -e
dir="$1"; slug="$2"; fps="${3:-24}"
mkdir -p assets/loops
ffmpeg -hide_banner -loglevel error -y -framerate "$fps" -i "$dir/f%04d.png" -vf "scale=1400:-2" -an -c:v libx264 -crf 26 -preset slow -pix_fmt yuv420p -movflags +faststart "assets/loops/$slug.mp4"
ffmpeg -hide_banner -loglevel error -y -framerate "$fps" -i "$dir/f%04d.png" -vf "scale=1400:-2" -an -c:v libvpx-vp9 -crf 36 -b:v 0 -row-mt 1 -deadline good "assets/loops/$slug.webm"
for f in "assets/loops/$slug.mp4" "assets/loops/$slug.webm"; do
  size=$(stat -f %z "$f"); dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  printf '%s  %s bytes  %.1fs\n' "$f" "$size" "$dur"
  [ "$size" -lt 1572864 ] || echo "  over 1.5MB: raise crf or shorten"
done
