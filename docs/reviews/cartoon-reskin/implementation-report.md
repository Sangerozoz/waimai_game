# Cartoon UI implementation report

2026-10-29

## Changed files

- `delivery-game/assets/scripts/map-sample/CartoonArt.ts`: cached atlas loading, final measured icon/food/vehicle/chrome crops, per-host sliced chrome frames, failure retry, close guards, and frame release on node destruction.
- `delivery-game/assets/scripts/map-sample/SampleUI.ts`: beveled Graphics fallback, reusable chrome attach/resize helpers, native outlined labels, generated icon display and disabled grayscale.
- `delivery-game/assets/scripts/map-sample/MapSample.ts`: blue header and dock, generated avatar/coin/star/station art, yellow two-character claim button, blue/yellow actions, violet dialog heading, and header resize synchronization.
- `delivery-game/assets/scripts/map-sample/OrderPhone.ts`: blue-white shell and title, pale scroll cards, generated action chrome, and native readable text.
- `delivery-game/assets/scripts/map-sample/CityMap.ts`: pastel green land, cyan waterways, cream roads, and colored building roofs; geometry and camera rules unchanged.
- `delivery-game/assets/scripts/map-sample/FoodImages.ts`, `MapVehicle.ts`, `VehicleSideArt.ts`: existing presentation entrances now use the generated atlases for 16 dishes and D/D+ art; other original vehicle catalog assets remain intact.
- `delivery-game/tests/cartoon-art.test.cjs`, `map-hud.test.cjs`, `map-vehicle.test.cjs`, `modal-shade.test.cjs`: atlas crop/cache/lifecycle checks, current resource boundaries, and existing safe-area and interaction assertions. Removed the obsolete white-only header assertion.

The four source PNG atlases are under `delivery-game/assets/resources/map-sample/cartoon/`; their exact crop data is in `output/imagegen/cartoon-ui/manifest.json`.

## Verification

- `npm run typecheck` — passed, exit 0.
- `npm run test:map` — 150 passed, 0 failed.
- `npm test` — passed, exit 0: 27 core, 150 map, 18 county-store, and 4 Python map-data tests; 0 failures.
- No scripted gameplay, purchases, or save mutation was performed.

## Follow-up and limits

- Cocos native Game View was refreshed after the correction and inspected as described below. Web Mobile build verification remains with the root integration task.
- The generated avatar is a temporary presentation asset pending the separate official character workflow. Higher vehicle grades continue using their original catalog images.
- Chrome uses cached atlas textures with per-node sliced frames. Graphics remains visible if the atlas is unavailable, and destroyed views do not activate from late callbacks.

## Native screenshot correction

The first Cocos Game View capture (`cocos-home-initial.png`) showed pointed white ends on the dock and a white diamond across the central action. The cause was the first chrome sizing formula: it selected vertical source insets from the short target height, leaving exactly 12 destination pixels for the much taller source center. Cocos's sliced assembler correctly compressed the source center into that strip, making the curved white rim converge abruptly. The final helper keeps insets in scaled source-image pixels, uses a virtual sprite canvas at least as large as the source frame, and scales that canvas to the requested UI dimensions. Slicing remains active for larger components; compact components preserve their source material and visible center.

The independent review also found that generated control icons bypassed their vector fallback. `icon()` now draws the native icon first, then passes that node to `cartoonArt`; a failed atlas load leaves the locator and navigation controls visually identifiable. Disabled generated icons remain grayscale and inert.

Focused red tests reproduced both failures before the fix. After the fix: `node --test tests/cartoon-art.test.cjs` passed 8/8; `npm run typecheck` passed; full `npm test` passed with 27 core, 151 map, 18 county-store, and 4 Python map-data tests (200 total, 0 failures). Logs: `/tmp/cartoon-fix-full.log` and `/tmp/cartoon-fix-typecheck.log`. The pre-fix copies are in `fix-before/`, and `chrome-fallback-fix.patch` records the production correction. Root integration restarted native Game View and captured `delivery-game/temp/mcp-captures/cartoon-home-final.png`; visual inspection confirms the white spikes and diamond are gone while the two-character claim label, dock, locator, and header remain readable. Root integration is handling the final build.
