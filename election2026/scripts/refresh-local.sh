#!/bin/bash
# DISABLED: the GitHub Action refreshes results; running both made the two fight over data.json.
# Remove these two lines (and `launchctl load` the plist) to turn the Mac job back on.
echo "refresh-local.sh is disabled; the GitHub Action handles refreshes."; exit 0
# Local stand-in for the GitHub schedule: refresh election2026 results from NBC/AP
# and push them. Run by launchd every 20 minutes (app.sadh.election2026.plist).
# Only election2026/data.json, data.js and the dot map (election2026/dots/) are ever
# committed; anything else you have uncommitted in the repo is left alone.
# The dot map rebuilds on the first run each hour and needs: pip3 install numpy scipy shapely pyshp
set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO" || exit 1
echo "== $(date '+%F %T %Z') =="

# Start from the latest remote data so we never fight an earlier push.
git fetch -q origin && git merge -q --ff-only "origin/$(git rev-parse --abbrev-ref HEAD)" 2>/dev/null \
  || echo "note: could not fast-forward (local commits or changes); continuing on current HEAD"

python3 election2026/scripts/update.py || { echo "update.py failed; nothing pushed"; exit 1; }

if [ "$(date +%M)" -lt 20 ]; then
  if python3 -c "import numpy, scipy, shapely, shapefile" 2>/dev/null; then
    python3 election2026/scripts/build_dots.py || echo "dot map rebuild failed; keeping the last good one"
  else
    echo "dot map: skipped (pip3 install numpy scipy shapely pyshp to enable)"
  fi
fi

if git diff --quiet -- election2026/data.json election2026/data.js election2026/dots; then
  echo "Results unchanged."; exit 0
fi
git add election2026/dots
git commit -q -m "election2026: results refresh $(date -u +'%F %H:%M') UTC" -- election2026/data.json election2026/data.js election2026/dots || exit 1
for i in 1 2 3; do
  if git push -q; then echo "pushed."; exit 0; fi
  echo "push rejected; rebasing (attempt $i)"
  git pull -q --rebase --autostash || true
done
echo "push still failing after 3 attempts"; exit 1
