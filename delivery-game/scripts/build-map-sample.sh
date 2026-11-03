#!/usr/bin/env bash
set -uo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
editor_app="${COCOS_CREATOR:-/Applications/Cocos/Creator/3.8.8/CocosCreator.app}"
"$editor_app/Contents/MacOS/CocosCreator" --project "$project_dir" --build "configPath=$project_dir/build-map-sample.json"
build_rc=$?
if [[ "$build_rc" -ne 0 && "$build_rc" -ne 36 ]]; then exit "$build_rc"; fi
set -e
test -f "$project_dir/build/map-sample/index.html" || exit 1
mkdir -p "$project_dir/build/map-sample/acceptance"
cp "$project_dir/acceptance/index.html" "$project_dir/build/map-sample/acceptance/index.html"
mkdir -p "$project_dir/build/map-sample/acceptance-revision"
cp "$project_dir/acceptance-revision/index.html" "$project_dir/build/map-sample/acceptance-revision/index.html"

# Independent ground-coordinate sample; its data is not a game save or route graph.
mkdir -p "$project_dir/build/map-sample/county-sample"
cp "$project_dir/county-sample/index.html" "$project_dir/county-sample/sample.js" "$project_dir/county-sample/rider-directions.js" "$project_dir/county-sample/scene-index.js" "$project_dir/county-sample/street-facades.js" "$project_dir/county-sample/index-v1.html" "$project_dir/county-sample/sample-v1.js" "$project_dir/county-sample/scene-index-v1.js" "$project_dir/county-sample/outer-landscape.js" "$project_dir/build/map-sample/county-sample/"
cp "$project_dir/../docs/art/2026-11-03-county-sample-production/sample-scene-layout.json" "$project_dir/build/map-sample/county-sample/sample-scene-layout.json"
cp "$project_dir/../docs/art/2026-11-02-county-production-layout/sample-route-reference.json" "$project_dir/build/map-sample/county-sample/sample-route-reference.json"
mkdir -p "$project_dir/build/map-sample/county-sample/materials"
cp "$project_dir/county-sample/materials/"*.png "$project_dir/build/map-sample/county-sample/materials/"
mkdir -p "$project_dir/build/map-sample/county-sample/rider-directions"
cp "$project_dir/county-sample/rider-directions/manifest.json" "$project_dir/build/map-sample/county-sample/rider-directions/"
cp "$project_dir/county-sample/rider-directions/"rider-d-*.png "$project_dir/build/map-sample/county-sample/rider-directions/"
# Optional expanded county scene, when delivered; default sample remains unchanged.
if [[ -f "$project_dir/county-sample/county-scene-layout.json" ]]; then
  cp "$project_dir/county-sample/county-scene-layout.json" "$project_dir/build/map-sample/county-sample/county-scene-layout.json"
fi
if [[ -f "$project_dir/county-sample/outer-landscape.json" ]]; then
  cp "$project_dir/county-sample/outer-landscape.json" "$project_dir/build/map-sample/county-sample/outer-landscape.json"
fi
if [[ -f "$project_dir/county-sample/sample-scene-layout-v2.json" ]]; then
  cp "$project_dir/county-sample/sample-scene-layout-v2.json" "$project_dir/build/map-sample/county-sample/sample-scene-layout-v2.json"
fi
