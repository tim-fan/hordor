#!/bin/bash
# Switch from the prod container to the dev server (manage.py runserver in
# tmux). Only one of the two should ever be bound to :8000 at a time.
set -euo pipefail

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
# Repo root = parent of the deploy/ dir this script lives in
REPO_ROOT="$(cd "$(dirname "$(readlink -f "$0")")/.." && pwd)"

echo "Stopping prod containers..."
systemctl --user stop hordor hordor-lan

echo "Starting dev server..."
tmux kill-session -t hordor_server 2>/dev/null || true
"$REPO_ROOT/hordor/start_server_in_tmux.sh"

echo "Dev server is live on :8000 (tmux session: hordor_server)."
