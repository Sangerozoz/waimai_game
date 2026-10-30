# M1 art A implementation — independent code review

**Current verdict after scoped Round 1 re-review: Spec Compliance PASS; Quality PASS. Both original P2 findings are resolved; no new actionable defect found in the fix diff. Rendered/device verification remains with the integrating agent.**

Reviewed 2026-10-29 against Task 1 brief and the implementation plan's Global Constraints. Baseline is the supplied full before/after `review-package.txt`, not HEAD. Code was read only; no tests, browser actions, game actions, saves, imports or builds were run by this reviewer. Follow-up reads were limited to named text-layout risks and their valid domain inputs.

## Initial Spec Compliance — historical findings, now resolved

- **P2 — valid offer metadata is clipped after wrapping** — `delivery-game/assets/scripts/map-sample/MapSample.ts:215`. The route and delivery panel puts food, quantity, weight and fragility into a fixed 58-unit-high `readable` label, which uses wrapping plus CLAMP. At 320×568 with no insets, auxiliary size is 30 and available width is 460. The current catalog and generated offers allow `麻婆豆腐饭 · 3份 · 3kg · 普通餐品`; even the implementation's own width estimate requires two lines / 94 units. The second line cannot be fully read, and scrolling the route viewport cannot reveal text clipped inside the label. This violates the readable-content/layout requirement. Measure and allocate the metadata height, keeping it clear of the route cards and progress content.
- **P2 — large wallet values are clipped in bills** — `delivery-game/assets/scripts/map-sample/MapSample.ts:363–370` (also the live update at line 378). Bill rows use a fixed height derived only from body size. At 320×568 with no insets, a highlighted wallet value has width 349.8, font size 42 and only 95.4 units of height. A valid balance such as `¥1234567890123.45` requires two lines (approximately 128 units by `textHeight`) and is clamped. `CountySnapshot.ts:20–23` accepts this amount, below MAX_SAFE_INTEGER cents; the new header explicitly supports long balances but the bill page does not. Allocate height from both label and value and update that allocation if live values grow. Preserve the correct source-index mapping.

The remaining approved scope is represented in the diff: phone frame and ten offers; scrollable modal contents with fixed actions; all twelve bill indices and original ≥/— presentation source; original region requirements; both original door choices without dismiss; configuration-backed vehicle information; exact-copy side-image evidence; unchanged domain and original-resource evidence. No unrequested game-state behavior was found.

## Initial Quality — historical assessment

The two P2 findings above are functional text-layout defects, not subjective polish. No additional blocking quality defect was found. New scroll content uses a top-anchored content node, rectangular mask, vertical ScrollView and inner-event cancellation. Bill labels remain assigned by original metric index. Disabled buttons omit tap bindings. Side-image promises are shared, failures evict the failed cache entry, and successful callbacks check strict parent/picture validity and inactive hierarchy before writing; image aspect ratio is preserved.

The new repeated `view.getFrameSize()` calls retain the CSS/frame unit convention needed by SHOW_ALL metrics. The parent reports deprecation log stacks in native preview. This is log noise / future API maintenance, not evidence of a present functional regression; replacing it with a pixel-based size without conversion would need separate verification.

## Verification boundaries

The implementation report records 187 passing tests and successful typecheck; these were not rerun. Node mocks confirm geometry/state behavior but do not establish actual glyph metrics or rendered clipping. The parent reports a loaded native home screenshot and no startup errors; this reviewer did not inspect or operate that preview. Cocos import/build, final rendered typography, long addresses, real scrolling/touch behavior, and device safe areas remain the integrating agent's checks. Do not claim complete visual acceptance from this code review.

**Initial verdict (superseded below):** Spec Compliance: changes requested (2 × P2). Quality: changes requested for the same 2 defects; no additional blockers.

## Scoped Round 1 re-review — PASS

Scope: only `round1-review-diff.txt`, the appended Round 1 implementation report, and the supplied final verification log excerpts. No whole-review repetition or test rerun; no source edits or runtime/state operations.

- **Original metadata P2: RESOLVED.** Metadata now receives its measured height, with the original top edge retained. The extra height propagates to route positions and scroll content height, delivery stage/timer/progress, arrived prompts and completed text. For the reported valid two-line example, height increases from 58 to 94 and dependent content moves down 36; route content remains reachable and fixed actions/map boundaries remain unchanged. The dedicated regression covers routes, running and done states and checks the relevant separations.
- **Original wallet P2: RESOLVED.** Bill rows reserve the measured height of the maximum valid cents balance with a historical ≥ prefix at the largest value font. The reported narrow-device case now provides 134 units for the value, sufficient for both lines. Stable preallocation also covers live growth without rebuilding or resetting the scroll content; source-index label assignments are retained. The dedicated regression checks an existing wallet Label updated to a legal large balance, unchanged modal/content position, and reopening with the large value.

The new progress-group parent is consistent with `updateProgress`: its local y remains −60 while the parent supplies the metadata displacement. The completed-state spacing adjustment also retains room above the fixed buttons for the reported case. No direct functional regression was found in this scoped fix.

Latest provided evidence records **189 tests passing** and typecheck exit 0 (`verification/round1-npm-test.log`, `round1-typecheck.log`); inspected log excerpts show no test failure and no typecheck diagnostics. The previous 187-test evidence above remains historical. This review does not establish actual font rasterization or device touch/scroll behavior.

**Current verdict:** Spec Compliance PASS (both P2s resolved). Quality PASS (no new actionable finding in the scoped fix). Integration build/import/render checks remain with the parent.
