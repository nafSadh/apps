#!/bin/bash
# Local stand-in for the GitHub schedule: refresh election2026 results from NBC/AP
# and push them. Run by launchd every 20 minutes (app.sadh.election2026.plist).
# Only election2026/data.json and data.js are ever committed; anything else you
# have uncommitted in the repo is left alone.
set -u
export PATH="/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:$PATH"
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$REPO" || exit 1
echo "== $(date '+%F %T %Z') =="

# Start from the latest remote data so we never fight an earlier push.
git fetch -q origin && git merge -q --ff-only "origin/$(git rev-parse --abbrev-ref HEAD)" 2>/dev/null \
  || echo "note: could not fast-forward (local commits or changes); continuing on current HEAD"

python3 election2026/scripts/update.py || { echo "update.py failed; nothing pushed"; exit 1; }

if git diff --quiet -- election2026/data.json election2026/data.js; then
  echo "Results unchanged."; exit 0
fi
git commit -q -m "election2026: results refresh $(date -u +'%F %H:%M') UTC" -- election2026/data.json election2026/data.js || exit 1
for i in 1 2 3; do
  if git push -q; then echo "pushed."; exit 0; fi
  echo "push rejected; rebasing (attempt $i)"
  git pull -q --rebase --autostash || true
done
echo "push still failing after 3 attempts"; exit 1
