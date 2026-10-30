# Task 1 — county clock, economy and compatible saves

Implementation complete; independent standards/spec review is pending root dispatch. No commit/stage/reset/clean/worktree operation, browser use or Cocos build was performed.

## Changes

- Added county-only `CountyConfig.ts`: D 12 km/h, D+ 13.2 km/h, upgrade 20000 cents, +12% income, 8 kg. First level threshold 50 XP; every later increment is preserved by shifting the old curve 50 XP earlier. Original `GameConfig.ts` remains byte-identical to the baseline ZIP.
- Clock takes actual road metres and average km/h: 6000 m / 12 km/h = 1800 display seconds = 10 animation seconds; 2700 seconds and above cap at 15 animation seconds. Display clock remains unrounded; existing formatting rounds minutes upward.
- New movement follows cumulative metres across different road speeds; pickup stage switches at the metres ratio. `progress.routeElapsedSeconds` remains a compatible road-interpolation parameter. Added `timingForRoute(route)` so old active route cards show frozen legacy ETA.
- New snapshots are v3. Each active delivery records `ruleVersion:1` (frozen old clock/settlement) or `2` (new county rules). v1/v2 first pass strict old validation, then migrate; current player level recomputes, while departure player and frozen receipts remain unchanged. A later v3 load validates legacy receipts against old settlement and compares current player with recomputed level. Running and old paused deliveries load into running automatically without RNG. Repeated settlement returns the same receipt and never credits again.
- Manual pause API is inert for compatibility; removed the UI pause action and replaced it with follow rider. Minimal UI wiring imports county vehicles, uses `timingForRoute`, and displays ¥200. Broader UI work remains Task 3. Existing view background-freeze behavior remains intact.

## Baseline fixtures and evidence

Before editing production clock/economy, extracted TypeScript sources directly from `.merge-backups/2026-10-28/stage-one-revision-base.zip`, compiled its unmodified OrderBook with Cocos-bundled TypeScript into `/private/tmp/county-task1-baseline/js`, then called the old runtime to serialize real v2 states. The initial six states existed before production edits. Added four more states using the same untouched baseline runtime to cover changed level thresholds.

Fixture: `delivery-game/tests/fixtures/county-v2-baseline.json` (145614 bytes). SHA-256: `dbe7bc40ea12f856b6b839cde6d15181b9fcdf38b205cea615a61d0a5889a352`.

States: idle, routes, running, paused, arrived, done, fifthDone, fiftyRunning, fiftyDone, oldLevelTwo. The first six include a D+ bought for the old ¥320 and one used free refresh; XP50 in-flight/receipts retain legacy Lv1 while current level becomes Lv2; XP200 idle becomes Lv3. All old cash/rating/XP/vehicle/quota/position/selected paths/damage/receipt data survive. Migration and second v3 restoration consume no RNG. State summaries and baseline ZIP SHA are in `task-1-fixture-provenance.json`; the large fixture is intentionally omitted from the text diff.

## TDD and checks

Working directory for npm commands: `delivery-game/`.

1. `npm run test:map` before changes: 34/34 pass (baseline verification). First attempted test write used an incorrect duplicated `delivery-game/` prefix and wrote nothing; corrected before implementation.
2. Added behavior checks first, then `npm run test:map > /private/tmp/task1-red.log 2>&1`: 37 tests, 30 pass, **7 expected failures**: fifth-order Lv2, ¥200 upgrade, v3/auto-resume migration, distance-based pose, ten-second compression, metres/kph ETA, distance progress.
3. Implemented rules/migration and updated previous test expectations for intentionally changed rules (15-second cap, auto-resume, ¥200, v3). Initial green: 37/37.
4. Extended legacy fixtures and corruption/threshold coverage; final full `npm run test:map > /private/tmp/task1-green-third.log 2>&1`: **40/40 pass**, 0 failures. (The enclosing exploratory shell returned 1 only because subsequent `rg 'not ok'` found no failing lines; npm/test itself succeeded.)
5. `npm run test:county-store`: **18/18 pass**, exit 0.
6. `npm run typecheck`: **exit 0**, no diagnostics.
7. After adding one current-level assertion to the fixture loop, ran only the focused county-session suite via a fresh strict TypeScript compilation and `node --test tests/county-session.test.cjs` with `MAP_ROUTER_MODULE` pointing at that temporary output: **13/13 pass**, exit 0. No production changes followed the full verification; avoided rerunning unchanged full suites.

No Cocos build/browser acceptance performed; root handles those after the dependent tasks.

## Self review and handoff

Checked v1/v2 original validation before migration, legacy departure-level income, frozen receipt levels, v3 current-level validation, unchanged RNG choices, D+ old purchase spending, delivery stages with unequal road speeds, idempotent settle, and no active pause action. No known Task 1 blockers.

Protected source comparison against baseline ZIP succeeded byte-for-byte:

- Main.scene SHA-256 `4b243a4bfdd6f6cdaf5db358c0405dd9ea4b971351028bee1b3aee84eb368166`
- domain/DeliverySession.ts SHA-256 `a2ba218af00e1075cec9b9cf63528e09dcfbe6f56b8e19441dce0f9f6aac6f1c`
- domain/GameConfig.ts SHA-256 `1cb5be314ec1f8bb7373d55f3169b596b6fa493c26d49b9fa6da49f7bf59468e`

Review delta: `task-1.diff`, full baseline-ZIP → current unified text diff with 10 lines context for all 11 changed/new source/meta/test files. Fixture path/hash/state summaries are supplied separately.

Task 2 baseline: `task-1-end-snapshot.zip`, contains all current `delivery-game/assets/scripts/`, `tests/`, `scripts/`, package.json and tsconfig.json, with repository-relative archive paths. It supplements the original baseline ZIP (map/resource files are deliberately excluded).

Task 2 must introduce explicit legacy map ID compatibility when appending POIs (current map hash still includes ordered POIs and strict equality). Old node/POI identities must be retained; old active delivery `ruleVersion` must survive any catalog/range migration. Task 3 should keep `timingForRoute` and CountyConfig usage during UI redesign.
