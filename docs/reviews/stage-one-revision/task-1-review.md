# Task 1 independent review

Reviewed the supplied ZIP-baseline → current `task-1.diff` first, then the task brief, approved design, implementation report, fixture provenance and the changed source/tests. This review covers Task 1 only. Task 2 city bounds/catalog/map-alias work and Task 3 UI/automatic receipt presentation are not acceptance requirements for this change.

## SPEC verdict: PASS

Critical: 0. Important: 0. Minor: 0.

- `delivery-game/assets/scripts/map-sample/DeliveryClock.ts:6–22`: the animation ratio is exactly display seconds / 180 with a 15-second cap; ETA is metres × 3.6 / km/h, without the removed overhead, traffic multiplier or minute rounding. Zero-distance progress is handled. `CountyConfig.ts:5–6` supplies D 12 km/h and D+ 13.2 km/h.
- `CountyConfig.ts:9–12`, `CountyRules.ts:24–45`, `OrderBook.ts:167–172`: the first level threshold is 50 XP and later increments are retained; settlement uses the departure level for income. D+ costs exactly 20000 cents, checks funds before deduction and rejects repeat upgrades. Tests cover 4/5-order thresholds, the next-order multiplier, 19999/20000 balances and repeat deductions.
- `OrderBook.ts:70–89`, `159–165`: new deliveries advance by cumulative metres and switch pickup stage by pickup metres. The conversion to router seconds preserves the router's pose contract across unequal road speeds. Legacy active deliveries retain the old road-time interpolation and frozen display/animation clocks.
- `CountySnapshot.ts:34–109`, `OrderBook.ts:44–61`, `142–151`: v1/v2 validation precedes migration; migrated active deliveries receive legacy rule version 1, while current deliveries record rule version 2. Current player level is recomputed independently of the frozen departure player and receipt. Legacy settlement uses historical level thresholds; current v3 validation checks the recomputed player against that historical result. Cash, rating, XP, vehicle, quota, route, selected damage, timing and receipt are preserved; done settlement returns the stored receipt without another award.
- `OrderBook.ts:49`, `131–139`, `MapSample.ts:187–201`: restored old paused deliveries run automatically, running deliveries remain running, the compatibility pause method is inert and the active pause button is gone. Existing background/foreground gating remains in `MapSample.ts:64–65`, `195–196`.
- The fixture tests cover ten genuine baseline v2 states, including pre/post-threshold legacy receipts and in-flight deliveries, and assert no RNG on migration/repeated v3 restoration. Current v3 running, routes, arrived and done paths also have restoration coverage. The v1 migration checks preserve progress/quota, retain a pending long route and return to the ordinary lobby after cancellation.

## QUALITY verdict: PASS

Critical: 0. Important: 0. Minor: 0.

No actionable introduced defect or documented-standard violation found. The county-only configuration keeps old-game tuning isolated. The single settlement implementation with an injected experience-level function keeps old/new financial arithmetic aligned while retaining the historical level policy. The versioned active-delivery rule is persisted and validated rather than inferred from current player state. The minimal UI call-site changes use metres/`timingForRoute` consistently.

No applicable repository coding-standard or AGENTS file was found in the task root or delivery-game scope. Reviewed changed code for correctness, naming, duplication, responsibility boundaries and unnecessary abstraction; no smell warranted an actionable finding.

## Evidence and limits

Did not rerun already-green full tests. Inspected the reported evidence for 40/40 map tests, 18/18 store tests, successful typecheck and the final focused 13/13 session run. No concrete unresolved doubt required another runtime check. No browser or Cocos build was performed.

Independently recomputed fixture SHA-256 `dbe7bc40ea12f856b6b839cde6d15181b9fcdf38b205cea615a61d0a5889a352` and baseline ZIP SHA-256 `ae37bed98ead41a823700aaaf3867456b765f146a6a62c3be1001f22783bfa6e`; both match the supplied provenance. Independently compared these current files to ZIP bytes; all are identical:

- `delivery-game/assets/scenes/Main.scene`: `4b243a4bfdd6f6cdaf5db358c0405dd9ea4b971351028bee1b3aee84eb368166`
- `delivery-game/assets/scripts/domain/DeliverySession.ts`: `a2ba218af00e1075cec9b9cf63528e09dcfbe6f56b8e19441dce0f9f6aac6f1c`
- `delivery-game/assets/scripts/domain/GameConfig.ts`: `1cb5be314ec1f8bb7373d55f3169b596b6fa493c26d49b9fa6da49f7bf59468e`

The only review artifact written is this report. No production/test code, browser state, user save or Git state was modified.
