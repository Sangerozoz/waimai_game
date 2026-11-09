# Manual deferred-clock transaction design

This is an internal performance change under the user's standing product-development authorization and repeated instruction to continue autonomously. It introduces no player decision or new feature; no repeat design approval, worktree, commit, model/account change or user testing is required.

## Evidence and alternatives

The current isolated long-history application spends about109ms per Runtime transaction. Each frame calls Dispatch.tick and a later Fleet advance; Dispatch.tick currently serializes/restores the full history even when only its frame changes. See `performance/owned-restore-1107/browser/window-1.json`: 52 Dispatch transactions and 104 Dispatch restores in 26 Runtime updates.

1. **Selected:** a strictly guarded path for manual ticks with both existing defer flags set, no pending ad and no unseen hero completion. Run all wallet, fleet, rewards and dispatch validation, then atomically replace only the frame/rebase fields. This removes the redundant serialized draft for that one event type.
2. Further local clone deletion has diminishing returns and leaves the repeated transaction structure in place.
3. A general draft capability or cached historical-validation system would touch many command/error paths. That broader redesign is outside this bounded task.

## Module and interface

Dispatch remains the module owning clock, control and cross-module consistency. Its existing tick interface is unchanged. Economy and Fleet each gain a callback-free `assertValid(): void` internal collaboration method; neither exposes authority or accepts an `eligible` parameter. Economy runs its complete existing validator. Fleet runs the complete wallet validator and its complete existing combination validator. Public projections remain detached.

The internal seam is validation of current private authority without first serializing a replacement draft. No adapters or new storage surfaces are introduced.

## Eligibility and effects

The path is eligible only for `deferAuto === true`, `deferFleet === true`, manual control, no pending advertisement, an exact equality between fleet hero-event cursor and wallet completion-event count, and an arrival port with its own ordinary function-valued data property. Accessor/inherited ports stay on the generic transaction, so external getters are not introduced into an in-place update. Auto control, pending/expiring ads, missing defer flags and unseen completion events retain the original transaction path verbatim.

Before changing state, preserve all restoration guards: valid arrival port, known Dispatch version, boolean clock-rebase flag, complete Economy validity, complete Fleet/wallet validity, wallet identity or complete serialized equality when the two references differ, complete RewardSession.restore validation, and complete Dispatch validation. An identical shared wallet reference proves equality without encoding it again.

Validate sequence, absolute time, flags, duplicate fingerprint and safe millisecond range exactly as the old tick does. A duplicate returns without replacing frame/rebase. A new frame retains the old high-water rule `max(now, oldNow)`, saves foreground/paused/fingerprint and clears clock rebase. It returns `{autoRunSeconds:0, control:'manual'}`.

Run original completion synchronization (guaranteed no new events by the guard) and complete Dispatch validation before publication. On any exception after replacing frame/rebase, restore both previous fields. No cash, ledger, rewards, fleet time, quota, batch, signed quote or route may change on this path. No calendar callback may run merely to tick the deferred clock.

## Verification and limits

Observe the real Dispatch.serialize method with a forwarding wrapper to prove eligible ticks do not construct a serialized whole-history draft. Use literal expected frames for rollback/foreground/pause/duplicate cases. Compare frozen-before and candidate outputs for adversarial, auto, pending-ad, stopped-auto, restored-clock and unsynchronized-event scenarios. Exercise complete Runtime saving/failure and existing emergency automatic recovery through the default suite.

Bad wallet, mixed wallet, forged historical receipt, bad rewards, invalid port and invalid clock metadata must still reject before a new frame is published. Error and duplicate paths must preserve the complete prior serialized state. Frame return values and public tick context stay detached.

Build and actual isolated packed-browser gates remain mandatory before updating the original previews. Do not claim full U01, physical-device FPS, original cross-package raw-save recovery or98% acceptance from this optimization.
