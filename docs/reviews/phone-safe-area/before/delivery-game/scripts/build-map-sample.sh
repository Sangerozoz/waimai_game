#!/usr/bin/env bash
set -uo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
editor_app="${COCOS_CREATOR:-/Applications/Cocos/Creator/3.8.8/CocosCreator.app}"
"$editor_app/Contents/MacOS/CocosCreator" --project "$project_dir" --build "configPath=$project_dir/build-map-sample.json"
build_rc=$?
if [[ "$build_rc" -ne 0 && "$build_rc" -ne 36 ]]; then exit "$build_rc"; fi
test -f "$project_dir/build/map-sample/index.html" || exit 1
mkdir -p "$project_dir/build/map-sample/acceptance"
cp "$project_dir/acceptance/index.html" "$project_dir/build/map-sample/acceptance/index.html"
mkdir -p "$project_dir/build/map-sample/acceptance-revision"
cp "$project_dir/acceptance-revision/index.html" "$project_dir/build/map-sample/acceptance-revision/index.html"
