#!/usr/bin/env bash
set -uo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
isolated="$project_dir/street-corner-3d-project"
editor_app="${COCOS_CREATOR:-/Applications/Cocos/Creator/3.8.8/CocosCreator.app}"
"$editor_app/Contents/MacOS/CocosCreator" --project "$isolated" --build "configPath=$isolated/build-street-corner.json"
build_rc=$?
if [[ "$build_rc" -ne 0 && "$build_rc" -ne 36 ]]; then exit "$build_rc"; fi
set -e
[[ -f "$isolated/build/street-corner-3d/index.html" ]] || exit 1
asset="$project_dir/../docs/art/2026-11-03-street-corner-3d/scene-design.json"
[[ -f "$asset" ]] || { printf '%s\n' 'Street corner scene asset has not arrived; build retained in isolated project.' >&2; exit 2; }
mkdir -p "$project_dir/build/map-sample/street-corner-3d"
cp -R "$isolated/build/street-corner-3d/." "$project_dir/build/map-sample/street-corner-3d/"
cp "$asset" "$project_dir/build/map-sample/street-corner-3d/scene-design.json"
