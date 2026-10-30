#!/usr/bin/env bash
set -uo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
editor_app="${COCOS_CREATOR:-/Applications/Cocos/Creator/3.8.8/CocosCreator.app}"
"$editor_app/Contents/MacOS/CocosCreator" --project "$project_dir" --build "configPath=$project_dir/build-config.json"
build_rc=$?
if [[ "$build_rc" -ne 0 && "$build_rc" -ne 36 ]]; then
  exit "$build_rc"
fi
test -f "$project_dir/build/web-mobile/index.html"
