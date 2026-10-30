# Task 2 independent review

SPEC: PASS  
QUALITY: PASS  
Actionable findings: none.

Reviewed the refreshed Task 1 ZIP → Task 2 U10 diff first, then Task 2 brief, approved design, final implementation report, verification logs and the named cross-boundary callers/validators. The final address enrichment delta is included. Review is limited to Task 2; Task 3 presentation work is not a prerequisite.

Reviewed artifact identities:

- `task-2.diff` SHA256 `aae60cb81722c833c32e0e961291aeb94ab0da576a39e53cd33acca7db6b8322`
- `task-2-end-snapshot.zip` SHA256 `ed4a2e55b9920f700bd40c9db2ead484bf45cbbeb9c369eb396073aad248402e`

## SPEC evidence

- `CityExtent.ts:12–18` clamps the camera centre after subtracting the viewport half width/height in road metres. `CityMap.ts:122–143` routes following `setRider`, locate, overview, focus and zoom through the same clamp; drag/pinch reach it at `CityMap.ts:162–168`. The compatibility extension includes historic outside rider/route geometry, without changing dispatch bounds (`CityMap.ts:139–143`, `CityExtent.ts:21–27`). Real caller initialization restores the rider pose and resets to the default 50 m scale (`MapSample.ts:80–83`).
- `PlaceCatalog.ts:7–29` derives the dense connected building component near the initial restaurant and applies the stated immediate approach allowance; `PlaceCatalog.ts:47` applies 10% padding. The reported final bounds are x[-4530,-570], y[-1410,1110]. `PlaceCatalog.ts:32–42` requires added locations to be reachable both ways on the bounded roads. `PlaceCatalog.ts:48–66` clones old POI metadata, preserves original order/name/node/kind, adds stable addresses and appends unique fictional locations. The raw graph arrays are retained. Final counts are 40 city merchants and 120 city customers, with 144 appended places.
- `OrderBook.ts:45`, `OrderBook.ts:194–214` use a separate router containing only nodes within `playBounds`. RoadRouter connects only consecutive surviving road endpoints, so it cannot introduce an outside shortcut. Preview uses the same bounded graph (`OrderBook.ts:101–108`); acceptance rejects overlength preferences (`OrderBook.ts:116–122`). Since the bounds are rectangular, the straight road segments between inside endpoints also remain inside.
- `OrderBook.ts:229–254` searches legal unique destinations across merchants before a repeat fallback, skips invalid/unreachable/overlength candidates and keeps total pickup plus delivery distance at most 10 km. Merchant usage penalties, food rotation and refresh avoidance implement the required diversity. The bounded repeat pass terminates for the one-merchant/one-customer fixture.
- `FoodCatalog.ts:5–27` supplies the exact sixteen row-major image indices and stable historic text mapping. `OrderBook.ts:247–251` derives quantity, weight and fragility from the chosen meal and keeps first-order normal/durable/no-door/1 kg/¥20 terms.
- `CountySnapshot.ts:35` accepts only the current identity or aliases supplied by prepared bundled map data. `PlaceCatalog.ts:65` derives that alias from the original graph and original POI identity, rather than save input. `OrderBook.ts:50–61` preserves player state, position and active delivery while deterministically replacing incompatible ordinary candidates without using the caller's RNG. Historic outside routes remain on the full graph; city dispatch resumes when the rider returns. Existing validation continues to check route geometry and historical receipt state against the unchanged graph.

## QUALITY evidence and validation limits

The implementation keeps graph preparation, camera mathematics and food metadata in pure modules. The city/full router cache keys are distinct, preventing a full-map route cached during migration from leaking into bounded ordinary dispatch. Restore bypasses RNG for replacement generation and current prepared-map saves avoid regeneration. The old active delivery is retained separately from candidate replacement, including routes, selected route, elapsed progress, damage and receipt.

Inspected the recorded final verification rather than rerunning full suites: `task2-final-all-tests.log` reports 27 legacy + 51 map/county + 18 save-store tests passing, and four map-data tests passing; `task2-final-typecheck.log` records typecheck with no diagnostics. The tests cover real CityMap movement entry points, bounded shortcuts, three diverse lobbies, tiny graph fallback, original indices/unique addresses, forged map identity rejection, real outside-save restoration, six distant legacy positions and unchanged active outside activity. No concrete unresolved doubt justified another test run.

Independently compared protected files byte-for-byte to `stage-one-revision-base.zip`: Main.scene, old domain/DeliverySession.ts, domain/GameConfig.ts, raw city.json, source.osm, city-roads.osm and every archived detail OSM file are unchanged.

No browser, Cocos build, save injection, source edit or Git mutation was performed for this review. Camera checks cover the recorded map heights 748/1030/1348 at 30–100 m; renderer appearance and actual-device acceptance remain later validation. An extent smaller than a viewport axis is explicitly centred by the helper and documented by the implementation report; this review does not claim arbitrary viewport dimensions can fit within a fixed world extent.
