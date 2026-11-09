# Owned JSON restoration implementation plan

**Goal:** Remove redundant whole-payload copies after `JSON.parse` in Economy, Fleet and Dispatch restoration while preserving every original validator and detached public projection.

**Evidence:** `docs/reviews/2026-11-05-game-development/performance/runtime-profile-1107/capture-04/` captures the current packed application in a fresh headless browser. At pickup, 23 runtime transactions consume 2788.6 of 3010.7 ms. Economy.restore, copied economy state and historical Dispatch validation dominate; slot commits consume 85.1 ms. Actual UI pickup/continue/delivery and ledger reconciliation remain valid. This is diagnostic browser timing, not physical-device FPS.

**Architecture:** The input is an immutable string. Each restore performs its own `JSON.parse`, which creates a private object graph. After full original validation, adopt that private graph instead of serializing/parsing it a second time. Public getters/snapshots must still detach their results. Separate restore calls must never share authority. No new interface, clock policy or schema.

**Scope:** Same checkout and fixed provider; no worktree/commit/push. Only `V2EconomySession.ts`, `V2FleetSession.ts`, `V2DispatchSession.ts` plus the new regression and evidence directory. Do not change maps, route code, economy parameters, historical evidence, validation bodies, Runtime/Store or user storage. PM implements; reuse B for independent read-only review.

### Task 1: Restore privately parsed objects without a second deep copy

- [x] Capture the three before sources and all 772 previously frozen inputs in `performance/owned-restore-1107/`.
- [x] Add `delivery-game/tests/product-regression-1106/owned-restore.test.cjs`. Observe real serialization calls without replacing their behavior: an Economy root, Fleet clock aggregate and Dispatch order-history array must not be re-encoded solely to detach an already privately parsed graph. Preserve scalar/cash/quote rejection and mutate detached returned data to prove ownership.
- [x] Run the new file on unchanged production with `node delivery-game/tests/run-v2.cjs product-regression-1106/owned-restore.test.cjs`; retain the actual resource-contract RED.
- [x] Make only these changes inside the existing restore functions:

```ts
// Economy: raw was JSON.parse(serialized), and the complete validator ran.
session.snapshot=raw;
// Fleet: raw was JSON.parse(serialized); validate() still runs afterwards.
f.value=raw.fleet;
// Dispatch: s was JSON.parse(serialized); validate() still runs afterwards.
result.orders=s.orders;result.batchIds=s.batchIds;result.frame=s.frame;
```

- [x] Verify distinct restore calls, public projections, replaceFrom, failed mutations, kg/slots and emergency compatibility; run default V2 regression and full typecheck. Retain all failures.
- [x] Compare complete before/after transaction bytes on existing long-history input, a real derived travelling state, empty state and the original soft-lock fixture. Freeze exact inputs, use conventional median, preserve raw samples and execution order.
- [x] Have B review frozen three-source diff, alias boundaries, validation preservation, RED/GREEN and benchmarks. Resolve concrete findings before deployment.
- [x] Build one independent final package; verify unchanged resources and original 4182/4196 HTTP identity. Repeat the same isolated packed-browser diagnostic on the final candidate and document its limits.
- [x] Publish the measured result and update current handoffs. Leave U01, true-device FPS, original raw cross-package recovery and 98% acceptance open unless evidence actually supports closing them.
