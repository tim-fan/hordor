#!/bin/bash
# Switch from the dev server to the prod container: rebuilds the image from
# whatever is currently on disk (so prod always runs exactly what you were
# just developing against, no stale code), then swaps over. Only one of the
# two should ever be bound to :8000 at a time.
#
# Migrations are NOT run here on purpose -- schema changes should still be
# verified against an isolated DB copy first and applied manually.
set -euo pipefail

export XDG_RUNTIME_DIR="${XDG_RUNTIME_DIR:-/run/user/$(id -u)}"
REPO_ROOT="/home/tim/projects/20240505_hodor_small_object_store/hordor"

echo "Stopping dev server..."
tmux kill-session -t hordor_server 2>/dev/null || true

echo "Building image..."
podman build -t hordor:latest -f "$REPO_ROOT/Containerfile" "$REPO_ROOT"

echo "Starting prod container..."
systemctl --user restart hordor

echo "Prod is live on :8000."
