#!/bin/sh
# Prepare the Stedd demo call for the site (Brief 8, item 3).
# Trims leading and trailing silence, normalizes to -16 LUFS, and writes
# assets/audio/stedd-demo.mp3 (80 kbps) and stedd-demo.ogg (Opus, 48 kbps).
# Usage: sh scripts/prep_demo_call.sh <recording.wav|.mp3|.m4a>
set -e
in="$1"; out="assets/audio/stedd-demo"
[ -f "$in" ] || { echo "usage: sh scripts/prep_demo_call.sh <recording>"; exit 1; }
filters="silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.3,areverse,silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.6,areverse,loudnorm=I=-16:TP=-1.5:LRA=11"
ffmpeg -hide_banner -loglevel error -y -i "$in" -af "$filters" -ar 44100 -ac 1 -c:a libmp3lame -b:a 80k "$out.mp3"
ffmpeg -hide_banner -loglevel error -y -i "$in" -af "$filters" -ar 48000 -ac 1 -c:a libopus -b:a 48k "$out.ogg"
for f in "$out.mp3" "$out.ogg"; do
  size=$(stat -f %z "$f"); dur=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f")
  printf '%s  %s bytes  %.1fs\n' "$f" "$size" "$dur"
  [ "$size" -lt 1048576 ] || echo "  over 1MB, lower the bitrate or trim"
done
