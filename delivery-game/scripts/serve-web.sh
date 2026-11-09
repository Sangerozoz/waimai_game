#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
build_dir="${1:-$project_dir/build/web-mobile}"
server_args=("$build_dir" --port "${PORT:-8080}" --bind 127.0.0.1)
if [[ -n "${PREVIEW_FALLBACK_BUILD:-}" ]]; then
  server_args+=(--fallback-directory "$PREVIEW_FALLBACK_BUILD")
fi
exec python3 "$project_dir/scripts/serve-web.py" "${server_args[@]}"
