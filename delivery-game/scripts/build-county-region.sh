#!/usr/bin/env bash
# Necessary delivery build only. No tests or browser operations.
set -euo pipefail
project_dir="$(cd "$(dirname "$0")/.." && pwd)"
isolated="$project_dir/county-region-project"
editor_app="${COCOS_CREATOR:-/Applications/Cocos/Creator/3.8.8/CocosCreator.app}"
[[ -f "$isolated/runtime-data/region-atlas.json" && -f "$isolated/runtime-data/integration-record.json" ]] || { echo 'Atlas native package required'; exit 1; }
mkdir -p "$isolated/build-evidence"
log="$isolated/build-evidence/build-$(date +%Y%m%d-%H%M%S).log"
set +e
"$editor_app/Contents/MacOS/CocosCreator" --project "$isolated" --build "configPath=$isolated/build-county-region.json" > "$log" 2>&1
build_rc=$?
set -e
printf 'Cocos process exit: %s; log: %s\n' "$build_rc" "$log"
[[ "$build_rc" -eq 0 || "$build_rc" -eq 36 ]] || exit "$build_rc"
rg -q 'Finished' "$log" || { echo 'No Finished evidence; refusing deployment'; exit 1; }
[[ -f "$isolated/build/county-region/index.html" ]] || exit 1
if [[ "${1:-}" == --deploy ]]; then
  destination="$project_dir/build/map-sample/county-region"
  if [[ -d "$destination" ]]; then
    backup="$isolated/deployment-backups/$(date +%Y%m%d-%H%M%S)"
    mkdir -p "$backup"
    cp -R "$destination/." "$backup/"
  fi
  mkdir -p "$destination/assets"
  cp -R "$isolated/build/county-region/." "$destination/"
  cp -R "$isolated/runtime-data/." "$destination/assets/"
fi
