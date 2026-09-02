#!/bin/sh
# Stamp the version and today's date into every page, then refresh the
# baked status rail values from the live endpoint. Nothing here is typed
# by hand.
#
# Usage: scripts/release.sh vX.Y.Z
set -e
cd "$(dirname "$0")/.."
[ -n "$1" ] || { echo "usage: scripts/release.sh vX.Y.Z" >&2; exit 1; }

pages=$(find . -name index.html \
  -not -path "./archive/*" -not -path "./raw/*" -not -path "./pitches/*" \
  -not -path "./qa/*" -not -path "./worker/*" | sort)
pages="$pages ./404.html"

python3 scripts/stamp.py "$1" $pages
python3 scripts/bake_status.py $pages || echo "bake_status: endpoint unavailable, baked values kept" >&2
