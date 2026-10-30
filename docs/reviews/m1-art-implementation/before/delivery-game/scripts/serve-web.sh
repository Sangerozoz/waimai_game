#!/usr/bin/env bash
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
build_dir="${1:-$project_dir/build/web-mobile}"
cd "$build_dir"
exec python3 -m http.server "${PORT:-8080}" --bind 127.0.0.1
