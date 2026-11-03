#!/usr/bin/env bash
set -uo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
isolated="$project_dir/modular-city-project"
editor_app="${COCOS_CREATOR:-/Applications/Cocos/Creator/3.8.8/CocosCreator.app}"
"$editor_app/Contents/MacOS/CocosCreator" --project "$isolated" --build "configPath=$isolated/build-modular-city.json"
build_rc=$?
if [[ "$build_rc" -ne 0 && "$build_rc" -ne 36 ]]; then exit "$build_rc"; fi
set -e
[[ -f "$isolated/build/modular-city/index.html" ]] || exit 1
mkdir -p "$project_dir/build/map-sample/modular-city"
cp -R "$isolated/build/modular-city/." "$project_dir/build/map-sample/modular-city/"
