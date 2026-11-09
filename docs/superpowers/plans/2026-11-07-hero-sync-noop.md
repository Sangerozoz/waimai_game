# Hero completion sync no-op implementation plan

> **For agentic workers:** Execute in the existing checkout; PM implements the single task and reuses an independent reviewer. The user's same-checkout and session-reuse instructions override worktree, fresh-agent and commit defaults.

**Goal:** Avoid a full fleet/wallet transaction when all hero completion events have already replenished operating quota.

**Architecture:** `V2FleetSession` owns the consumed event cursor. Compare it with the existing scalar `V2EconomySession.heroCompletionEventCount`; on an exact match run the complete fleet combination validator before returning. When events remain, retain the entire current atomic synchronization path. No public interface or save schema changes.

**Tech Stack:** TypeScript, existing isolated V2 Node TAP runner, Creator 3.8.8.

## Global constraints

- Remain in `/Users/sanger/Documents/ChatGPT/taptap 2`, environment `env_e54zrbdgxt`; no worktree, commit or push.
- Provider/model routing and account settings remain untouched; reuse Codex/Sanger/max for any independent review.
- Only `V2FleetSession.ts` is a production write target. Tests and this task's evidence are separate writes.
- Preserve every original restore/validation, real hero refill, stage threshold, NPC settlement, clock, old contract, writer lock and save-before-publication rule.
- Do not modify maps, route data, prices, player saves, old fixtures or previous evidence.
- A bounded in-memory model benchmark is not browser FPS, physical-device performance or U01/98% acceptance.

### Task 1: Eliminate redundant already-consumed hero sync transactions

**Files:**
- Modify: `delivery-game/assets/scripts/domain/V2FleetSession.ts`, `syncHeroCompletions` only.
- Create: `delivery-game/tests/product-regression-1106/hero-sync-noop.test.cjs`.
- Create evidence: `docs/reviews/2026-11-05-game-development/performance/hero-sync-noop-1107/`.

**Interface:** Keep `syncHeroCompletions(): void` and all existing serialized representations.

- [x] Investigate the open U01 issue using existing evidence. The existing 150-minute model snapshot contains 771 hero / 884 NPC completions. Initial in-memory probing measured about 100 ms for one tick; sampling showed repeated cloning/restoration as the main cost.
- [x] Test one hypothesis without editing production: an exact-cursor no-op guard reduced a complete candidate transaction median from approximately 169 to 143 ms; 10 paired outputs were byte-identical. These exploratory results are preliminary and will be replaced by reproducible frozen-source measurements.
- [x] Capture source/input fingerprints and the exact before source; add test and benchmark artifacts.
- [x] Run `node delivery-game/tests/run-v2.cjs product-regression-1106/hero-sync-noop.test.cjs` against unchanged production. The cost-boundary assertions fail because repeated no-op sync still serializes the wallet; restore assertions pass.
- [x] Add the production guard, including the full combination validation required by independent review:

```ts
syncHeroCompletions():void {
 if(this.value.heroEventCursor===this.economy.heroCompletionEventCount){this.validate();return;}
 this.atomic(d=>d.syncDraft());
}
```

- [x] Re-run the narrow tests. All 11 pass, covering empty/consumed histories for kg/slots, restored pending events, malformed cursors, public wallet replacement in both schema directions and direct Economy slot promotion. Preserve original 2-pass/6-fail RED and review-followup 8-pass/3-fail RED.
- [x] Compare frozen-before and actual-after code on identical existing long-term and emergency evidence. All 40 complete serialized outputs match. Use the arithmetic mean of the two middle samples for an even-sized median; keep the earlier upper-median result archived.
- [x] Run the final default isolated V2 regression (156/156) and full typecheck (exit0). Keep original and review-followup failures with their exit codes.
- [x] Obtain independent read-only review of the final one-source delta, 11 tests, raw RED/GREEN and paired benchmark. Important/Minor findings closed; Spec PASS, quality PASS, 0 findings.
- [x] Build final candidate v2-hero-sync-validated-1107 (Creator36/Finished, 772 inputs unchanged), update 4182/4196, verify 30 HTTP identities and 524 unchanged resources. Preserve first undeployed candidate and terminal restart HTTP409/recovery.
- [x] Publish the report and update five current product entries. U01, original cross-package raw-save recovery, true-device FPS and overall 98% remain open.
