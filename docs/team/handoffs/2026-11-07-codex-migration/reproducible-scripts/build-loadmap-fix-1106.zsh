#!/bin/zsh
set -u
log='/Users/sanger/Documents/ChatGPT/taptap 2/docs/reviews/2026-11-06-product-testing/build-loadmap-fix-complete.log'
env -u ELECTRON_RUN_AS_NODE /Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/MacOS/CocosCreator --project '/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game' --build 'configPath=/Users/sanger/.hermes/cache/scratch/v2-loadmap-fix-1106.json' > "$log" 2>&1
rc=$?
printf '\nCREATOR_EXIT=%s\n' "$rc" >> "$log"
printf 'Creator loadmap fix exit: %s\n' "$rc"
exit "$rc"
