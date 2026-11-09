#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
build_dir="${1:-$project_dir/build/web-mobile}"
exec python3 "$project_dir/scripts/serve-web.py" "$build_dir" --port "${PORT:-8080}" --bind 127.0.0.1
