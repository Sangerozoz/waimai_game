# Manual deferred-clock implementation plan

> Execute in the same checkout under the existing autonomous-development authorization. PM implements; reuse B for independent read-only review. Existing user instructions override fresh-thread, worktree, commit and repeated approval defaults.

**Goal:** Avoid serializing/restoring the full Dispatch history for manual, fully deferred, event-free clock updates without changing their results or weakening validation.

**Architecture:** Dispatch selects a private guarded clock method behind the existing tick interface. Economy/Fleet expose only complete callback-free `assertValid():void`. The original generic transaction remains unchanged for all ineligible updates. Spec: `docs/superpowers/specs/2026-11-07-manual-clock-design.md`.

**Files:** `V2EconomySession.ts`, `V2FleetSession.ts`, `V2DispatchSession.ts`; new `tests/product-regression-1106/manual-clock.test.cjs`; evidence only in `performance/manual-clock-1107/`. Runtime, Game, Route, Store, prices, maps and user storage are outside the write set.

- [x] Read latest packed profiling and capture773 inputs and three exact before sources.
- [x] Add the focused domain cases first; run `node delivery-game/tests/run-v2.cjs product-regression-1106/manual-clock.test.cjs` on unchanged production. Eligible clocks should fail only the redundant-serialization assertion; existing semantic/rejection cases should pass.
- [x] Add `assertValid():void` to Economy and Fleet by calling their existing complete validators. Add the private manual-clock method and an eligibility guard to Dispatch.tick; retain the entire old generic body.
- [x] Run the focused tests, default V2 regression and full typecheck. Include exception rollback, publicly changed port, duplicate and pending-event/advertisement fallback.
- [x] Compare exact before/after result bytes for four existing Game inputs and a direct Dispatch scenario matrix; preserve raw sample timing and all failures. Do not run benchmarks concurrently with heavy checks.
- [x] Freeze the precise diff/receipts and request B's independent read-only Spec/quality review. Resolve actual findings before deployment.
- [x] Build one independent Creator candidate; verify input integrity and unchanged resources. Run the same isolated packed-browser pickup/ready/travel windows, ledger and close gates, using the existing model input and only the known mapKey transport adaptation.
- [x] Update4182/4196 only after gates pass; check index and all14JS. Publish the measured result and current handoffs, preserving U01 and all other unverified acceptance limits.

Final closure: options getter follow-up RED20/5→GREEN25/25, default192/192, typecheck0; independent B Spec/quality PASS; final Creator36/Finished and actual isolated browser/ledger/slot gates passed. Both previews identify the final package (30 HTTP hashes). U01 remains open at about99–101ms per long-history transaction; no device-FPS or overall acceptance claim.
