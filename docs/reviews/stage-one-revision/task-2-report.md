# Task 2 implementation report

Status: implementation complete; handed to root for the required independent Standards / Spec review. No Cocos build or browser acceptance performed in this task.

## Scope and interfaces

- Added pure `CityExtent.ts`, `PlaceCatalog.ts`, `FoodCatalog.ts`, with Cocos metadata files.
- Changed `MapTypes.ts`, `CityMap.ts`, `OrderBook.ts`, trusted alias validation in `CountySnapshot.ts`, and the minimal `prepareCity(asset.json)` connection in `MapSample.ts`.
- `Bounds` uses `minX/maxX/minY/maxY`. `clampCamera(bounds, offset, scale, width, height)` subtracts viewport half extents on both axes. Drag, pinch/wheel/button zoom, overview, locate, focusRoute, and following `setRider` all reach the same clamp. Outside historic route/rider geometry widens a compatibility camera; ordinary dispatch bounds remain fixed. An impossible viewport axis centres on the extent; existing full geometry and continuous MapGround remain underneath.
- `prepareCity(data):CityData` preserves the original graph arrays and POI order/name/node/kind, enriches old addresses, appends fictional places, and returns `playBounds`, `legacyMapIds`, `placeCatalogVersion:1`. A WeakMap reuses preparation of the same input; the version marks already prepared input, preventing double append. Independent raw JSON loads produce the same nodes, names, addresses and map identity. No RNG is used for catalog preparation.
- `FOOD_CATALOG` is a 16-entry row-major atlas map with `id/name/imageIndex/fragility/unitWeightKg`. `foodForOffer(text)` handles current meal names and old food strings. Legacy 家常饭盒/家常饭 → image0; 小炒套餐 → image2; 鲜汤面 → image4; unknown text has a stable image0 fallback. Task3 can consume this API directly.

## Actual density and place counts

Observed the original 3524 building polygons using 300m centroid cells with at least 10 buildings. The connected dense component nearest the first restaurant has 27 cells / 1013 buildings, x[-4200,-900], y[-900,600]. This selects the initial urban cluster, rather than the distant dense cluster at the southern edge or the entire source map.

Included immediate urban approach strips to make the core y[-1200,900], keeping x[-4200,-900]. Ten percent of core width/height is added on **each side**: final x[-4530,-570], y[-1410,1110], size3960×2520m. This supports map heights748/1030/1348 at all30–100m scales. It is a gameplay viewport choice grounded in the observed dense component; the raw road and building data are unchanged.

Original POIs:128 total, with16 inside this play range (5 restaurants /11 customers). Appended144:35 restaurants /109 customers. Prepared total272; city totals40 restaurants /120 customers. Original128 indices, names, node IDs and kinds stay stable. Every prepared place has a unique fictional address; added places have unique names and distinct original road nodes. Added nodes belong to the initial restaurant's strongly connected component in the graph restricted to the play bounds. Existing source nodes/roads remain available for old activity and outer recovery.

Raw identity `ef9d9c7`; prepared identity `7192a588`. Only the identity computed from bundled original data becomes a trusted legacy alias. Snapshot-provided alias strings have no authority, and forged map IDs fail validation.

## Dispatch and migration behavior

New ordinary routes use a separate router restricted to original nodes inside `playBounds`; source roads are not rewritten. This prevents a faster path from leaving and re-entering the city. Both pickup and delivery legs are checked, including every offered preference and combined distance<=10000m. Preview distances use that same bounded graph. Failed/unreachable candidates are skipped and the search continues.

Merchants rotate across the city with an in-batch usage penalty. Meals rotate through all16 types; quantities1–3, weight and fragility come from the selected meal. First order remains normal/durable/no-door,1 portion,1kg,base¥20. Destinations are searched uniquely across all legal merchants before a bounded repeat pass is permitted on small test graphs. Refreshes penalize the previous lobby destinations. One-merchant/one-customer maps still produce10 orders without looping.

For old alias saves, old ordinary candidates survive with their exact terms/IDs only when their pickup/customer remain inside the city and their legal trip remains<=10km; the old active pending offer is retained regardless of range, and its already selected route, elapsed time, damage, departure player and receipt stay frozen. Other candidates are replaced deterministically without invoking the caller's RNG. Player money/rating/XP/vehicle, current node, recent places, tutorial status and refresh usage remain intact. Current prepared-map saves reload without candidate regeneration or RNG calls. Existing genuine v2 fixtures continue to pass.

Old outside riders use the full original graph, preferring city merchants and customers. If no complete city-return trip is available within10km, constrained legacy outer dispatch remains available using the original place pool. No teleport, clearing, or forced overlength ordinary route is used; the compatibility camera keeps the old rider and route visible. Six distant original customer locations were tested for legal10-order dispatch, plus the real QA save.

Actual `docs/reviews/stage-one-final/pre-scenery-valid-save.json`: rider node4637276074 remains at its original point[1490.96,-3333.51]. All10 original candidates contain out-of-city endpoints, so none survive as ordinary candidates; they becomeCC-106–CC-115 deterministically. All10 replacements have city pickup/customer endpoints and total distance<=10km. Wallet/rating/XP/vehicle and refresh usage are preserved. A separate outside active-delivery identity migration test verifies unchanged full activity, pose and fixed damage, plus stable repeated reload.

## Diversity and CPU observations

One local Node run (not a mobile performance guarantee) measured catalog preparation33.8ms, initial construction/router setup plus10 dispatches63.5ms, and two10-order refreshes17.2ms /11.9ms. Real old QA save migration took248.7ms. Full raw numbers: `task-2-logs/task2-metrics.json`.

All three observed batches had10 distinct merchants,10 distinct meals and10 distinct destinations. Total road distances ranged1.214–7.202km initially,4.267–9.505km on refresh1,2.517–7.976km on refresh2. Automated three-batch coverage requires>=25 different destinations,>=20 merchants and all16 meals across the batches.

## TDD and verification evidence

Persistent complete logs are in `task-2-logs/` (not only temporary files):

1. `task2-red.log`: newly wired content checks fail because the new pure modules do not exist. Tests were added before implementation.
2. `task2-partial.log`: after pure content/camera modules, the real merchant diversity assertion fails (old dispatcher does not diversify the batch). Two camera fixture errors exposed missing test harness `selected`; corrected the harness without changing production to satisfy it.
3. `task2-camera-red.log`: corrected real CityMap tests replayed against the exact Task1 ZIP CityMap in an isolated temporary directory; boundary assertion fails immediately after following `setRider`. Working source was never reverted or replaced for this check.
4. `task2-green.log`, `task2-outer.log`, `task2-final-map.log`: progressive47/50/51-pass checks, including bounded-vs-outside shortcut, tiny-map fallback, six outer positions and frozen outside activity.
5. `task2-address-red.log`:50 pass/1 expected failure for city addresses including original POIs; enrich original address metadata, keeping original identity/index fields.
6. Final `npm test` in `delivery-game`:27 legacy game tests +51 map/county tests +18 store tests +4 map-data tests all pass; zero failures. Complete log `task2-final-all-tests.log`.
7. Final `npm run typecheck`:exit0, no diagnostics. Complete log `task2-final-typecheck.log`.

No commits, staging, reset, clean, worktree changes, save injection/clearing, acceptance edits, PNG changes, browser or Cocos build were performed. Existing incidental `__pycache__` files were left alone and excluded from the review snapshot/diff.

## Protected files and review artifacts

Compared Main.scene and city.json byte-for-byte to the original recovery ZIP, and old DeliverySession/GameConfig to Task1 ZIP:

- Main.scene SHA256 `4b243a4bfdd6f6cdaf5db358c0405dd9ea4b971351028bee1b3aee84eb368166`
- domain/DeliverySession.ts `a2ba218af00e1075cec9b9cf63528e09dcfbe6f56b8e19441dce0f9f6aac6f1c`
- domain/GameConfig.ts `1cb5be314ec1f8bb7373d55f3169b596b6fa493c26d49b9fa6da49f7bf59468e`
- city.json `536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20`

`task-2.diff`: full text diff with10 context lines against task-1-end-snapshot.zip for14 changed/new source/meta/test files. The enormous unchanged city.json is excluded. `task-2-changed-files.json` lists those paths. `task-2-end-snapshot.zip` contains the same source/tests/scripts/package/tsconfig scope as Task1 (excluding incidental bytecode), with repository-relative archive paths. It is the Task3 source baseline after root review; resources remain covered by the original recovery ZIP.

Remaining validation: independent read-only dual-axis review by root; later Cocos/browser acceptance, especially visual camera behavior on actual devices. No known implementation blocker at handoff.
