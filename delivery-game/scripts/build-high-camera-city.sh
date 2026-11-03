#!/usr/bin/env bash
# Compile only by default. --deploy requires the complete native data package.
set -uo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
isolated="$project_dir/high-camera-city-project"
editor_app="${COCOS_CREATOR:-/Applications/Cocos/Creator/3.8.8/CocosCreator.app}"
if [[ "${1:-}" == --deploy ]]; then
  [[ -f "$isolated/runtime-data/asset-manifest.json" && -f "$isolated/runtime-data/scene-layout.json" && -f "$isolated/runtime-data/integration-record.json" ]] || { echo 'Native data package is incomplete; refusing deployment'; exit 1; }
fi
"$editor_app/Contents/MacOS/CocosCreator" --project "$isolated" --build "configPath=$isolated/build-high-camera-city.json"
build_rc=$?
echo "Cocos process exit: $build_rc"
if [[ "$build_rc" -ne 0 && "$build_rc" -ne 36 ]]; then exit "$build_rc"; fi
set -e
[[ -f "$isolated/build/high-camera-city/index.html" ]] || exit 1
if [[ "${1:-}" == --deploy ]]; then
  destination="$project_dir/build/map-sample/high-camera-city"
  if [[ -d "$destination" ]]; then
    backup="$isolated/deployment-backups/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup"
    cp -R "$destination/." "$backup/"
  fi
  mkdir -p "$destination/assets"
  cp -R "$isolated/build/high-camera-city/." "$destination/"
  cp -R "$isolated/runtime-data/." "$destination/assets/"
fi
