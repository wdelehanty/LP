#!/bin/sh
# Prepare a screen-recording loop for a photo frame (Brief 8, item 4).
# Crops the QuickTime capture to the frame's aspect, trims to 12 to 15 seconds,
# and encodes h264 mp4 and vp9 webm at 1400 wide, silent, under 1.5MB each.
# Also writes a poster still from the first frame when the frame has none.
# Usage: sh scripts/prep_loop.sh <recording.mov> <slug> [aspect w:h] [start s] [duration s]
#   sh scripts/prep_loop.sh ~/Desktop/morning-round.mov morning-round-gmail 3:2 2 14
set -e
in="$1"; slug="$2"; aspect="${3:-3:2}"; start="${4:-0}"; dur="${5:-14}"
[ -f "$in" ] && [ -n "$slug" ] || { echo "usage: sh scripts/prep_loop.sh <recording> <slug> [w:h] [start] [duration]"; exit 1; }
aw="${aspect%%:*}"; ah="${aspect##*:}"
vf="crop=min(iw\,ih*$aw/$ah):min(ih\,iw*$ah/$aw),scale=1400:-2,fps=24"
mkdir -p assets/loops
ffmpeg -hide_banner -loglevel error -y -ss "$start" -t "$dur" -i "$in" -vf "$vf" -an -c:v libx264 -crf 28 -preset slow -pix_fmt yuv420p -movflags +faststart "assets/loops/$slug.mp4"
ffmpeg -hide_banner -loglevel error -y -ss "$start" -t "$dur" -i "$in" -vf "$vf" -an -c:v libvpx-vp9 -crf 38 -b:v 0 -row-mt 1 -deadline good "assets/loops/$slug.webm"
[ -f "assets/img/$slug.jpg" ] || ffmpeg -hide_banner -loglevel error -y -ss "$start" -i "$in" -vf "crop=min(iw\,ih*$aw/$ah):min(ih\,iw*$ah/$aw),scale=1400:-2" -frames:v 1 -q:v 4 "assets/img/$slug.jpg"
for f in "assets/loops/$slug.mp4" "assets/loops/$slug.webm"; do
  size=$(stat -f %z "$f"); printf '%s  %s bytes\n' "$f" "$size"
  [ "$size" -lt 1572864 ] || echo "  over 1.5MB: raise crf or shorten"
done
