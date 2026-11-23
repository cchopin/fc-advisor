#!/bin/bash
# Pull-based deployment: fetch origin/main and redeploy when it moved.
# Runs from fc-advisor-autodeploy.timer. No inbound connection needed.
set -euo pipefail

REPO_DIR="${REPO_DIR:-/home/tely/fc-advisor}"
REMOTE_URL="${REMOTE_URL:-https://github.com/${GITHUB_REPO:-cchopin/fc-advisor}.git}"
GITHUB_REPO="${GITHUB_REPO:-cchopin/fc-advisor}"
BRANCH="${BRANCH:-main}"
HEALTH_URL="${HEALTH_URL:-http://127.0.0.1:5050/}"

cd "$REPO_DIR"

# Public repo: fetch over HTTPS so no SSH key or agent is needed.
git fetch --quiet "$REMOTE_URL" "$BRANCH"
local_sha=$(git rev-parse HEAD)
remote_sha=$(git rev-parse FETCH_HEAD)

if [ "$local_sha" = "$remote_sha" ]; then
    exit 0
fi

if ! git diff --quiet || ! git diff --cached --quiet; then
    echo "ERROR: uncommitted changes in $REPO_DIR, refusing to deploy $remote_sha" >&2
    exit 1
fi

if ! git merge-base --is-ancestor "$local_sha" "$remote_sha"; then
    echo "ERROR: local HEAD $local_sha is not an ancestor of $remote_sha (history diverged), refusing to deploy" >&2
    exit 1
fi

# Only deploy commits whose GitHub Actions checks all succeeded.
ci_state=$(curl -fsS -H 'Accept: application/vnd.github+json' \
    "https://api.github.com/repos/${GITHUB_REPO}/commits/${remote_sha}/check-runs" \
    | python3 -I -c '
import json, sys
runs = json.load(sys.stdin).get("check_runs", [])
if not runs or any(r["status"] != "completed" for r in runs):
    print("pending")
elif all(r["conclusion"] in ("success", "skipped", "neutral") for r in runs):
    print("success")
else:
    print("failure")
') || ci_state=unknown

case "$ci_state" in
    success) ;;
    pending|unknown) exit 0 ;;  # retry on next timer tick
    *)
        echo "CI failed for ${remote_sha:0:7}, not deploying" >&2
        exit 1 ;;
esac

echo "Deploying ${local_sha:0:7} -> ${remote_sha:0:7}"
git merge --quiet --ff-only FETCH_HEAD
git update-ref "refs/remotes/origin/$BRANCH" "$remote_sha"

docker compose up -d --build --remove-orphans

for _ in $(seq 1 15); do
    if curl -fsS -o /dev/null "$HEALTH_URL"; then
        echo "Deploy OK: $(git log -1 --format='%h %s')"
        docker image prune -f >/dev/null
        exit 0
    fi
    sleep 2
done

echo "ERROR: $HEALTH_URL not healthy after deploying ${remote_sha:0:7}" >&2
exit 1
