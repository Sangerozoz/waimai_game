# Cartoon reskin independent code review

2026-10-29. Reviewed the captured 548-line before/after diff, current implementation, implementation report, approved design spec, atlas manifest, generated chrome/vehicle images, and relevant tests. The fixed point is `docs/reviews/cartoon-reskin/before/`, not Git HEAD: most of this game was originally untracked. No implementation files were edited and no tests were rerun.

## Spec verdict — changes requested

**S1 · P2 · Keep a visible fallback for generated control icons.** `delivery-game/assets/scripts/map-sample/SampleUI.ts:63–66` returns `cartoonArt(...)` without a fallback for every recognized icon. `CartoonArt.ts:34–41` starts that picture inactive and deliberately leaves it inactive on resource failure. Consequently, if `ui-icons/texture` fails, the positioning control created at `MapSample.ts:223–224` is a completely unlabeled yellow button, with no later retry until the view is rebuilt. The same early return bypasses the existing vector implementations at `SampleUI.ts:69–73`; the navigation captions survive, but their icons vanish. This falls short of spec line 22 (“节点销毁保护与失败占位”) and weakens line 13’s requirement to preserve the positioning entry. Create the native icon first and pass it as `cartoonArt`'s fallback, hiding it only after a successful load. A focused failure-path test at the `icon()` integration boundary would cover the gap; the existing loader test passes a fallback explicitly and cannot catch it.

Otherwise the inspected changes follow the approved scope: blue/white/yellow chrome replaces the superseded white-only/transparent preferences; the center action remains only the two large characters `抢单`; generated images carry no gameplay values; unavailable recruitment/station entries remain untappable; the order-list structure, callbacks, scrolling, safe-area placement, long-text measurement, road geometry, zoom, vehicle node dimensions, economy, clock, and save interfaces are preserved. The generic avatar and unchanged higher-tier vehicle images are explicitly disclosed transitional assets, not review defects.

## Code quality verdict — no additional actionable findings

No repository-specific coding-standard source was found among the scoped files. Existing compact formatting was treated as the local convention; no style-only findings were raised.

- Atlas rectangles are normalized against the documented 1280 coordinate space and converted to actual texture dimensions at runtime; this is compatible with the imported 1254×1254 PNGs. Frame creation rechecks the cache after the shared texture promise resolves, preventing duplicate frames under concurrent requests.
- Failed atlas promises are evicted, so later calls can retry. Strict `isValid(..., true)` plus parent-active checks prevent late results from reviving closed/destroyed views. The map vehicle additionally checks request identity, preserving tier-switch ordering.
- Shared textures and immutable source frames are intentionally retained for game lifetime. Mutable sliced frames are per chrome node and release their explicit reference on `NODE_DESTROYED`; this does not evict the shared atlas. Cocos 3.8.8 engine source confirms that changing insets updates sliced UVs and that marking render data dirty updates the sliced vertices. The header resize path updates both the host and its skin, including sizes changed before asynchronous loading completes.
- Decorative child sprites add no touch listeners or input blockers. Existing touch-cancel/drag handling, action callbacks, enabled guards, and ScrollView configuration are unchanged.
- The relevant tests exercise shared loading, normalized crops, close guards, retries, unique-frame release, and current safe-area/input behavior. The implementation report records 199 passing tests and typecheck exit 0; this reviewer did not independently rerun those checks.

## Material limits

Native rendering and Web Mobile build verification are assigned to the root integration task. Static code/image review cannot certify final rasterized text fit, Chinese font fallback, or header/dock contrast at device scale. In particular, navigation text uses dark blue over a blue/white sliced asset (`MapSample.ts:247–252`); confirm the final label region in the native screenshot before treating visual acceptance as complete. This is a verification limit, not a second code defect without a rendered reproduction. No gameplay, purchasing, save mutation, or new image generation was performed.

Summary: Spec — 1 finding (P2); code quality — 0 additional findings. Fix S1, then retain native screenshot/build evidence as the remaining acceptance check.

## Limited follow-up review — S1 resolved

2026-10-29. Read-only follow-up of `chrome-fallback-fix.patch`, production `CartoonArt.ts` and `SampleUI.ts`, and the revised `cartoon-art.test.cjs`. No tests were rerun and no UI was operated.

**S1 is resolved.** `SampleUI.ts:64–65` now creates and draws the native locator before requesting generated art; line 74 supplies that node as the fallback. `CartoonArt.ts:40–41` hides it only after a successful frame assignment and leaves it visible on failure. The existing navigation vector drawings are reachable again. The added integration test at `cartoon-art.test.cjs:75–82` invokes the production `icon()` boundary and checks that resource failure preserves the fallback. The success/closed-page behavior remains covered by the unchanged loader logic and earlier tests.

**No new definite runtime defect found in the chrome correction.** `CartoonArt.ts:65–77` converts source insets to the actual texture scale, maintains a virtual sprite canvas at least as large as the cropped source, and scales only the decorative child to the requested host size. Its effective displayed size remains `width × height`; caller hit targets and sibling captions retain their original transforms. An initial asynchronous load uses the most recent requested transform dimensions; later resize calls receive explicit host dimensions and recalculate the scale, so virtual dimensions do not accumulate. Per-host frames, reference release, close guards, and render invalidation remain intact. Revised test assertions at lines 56–62 check the effective footprint and that the center region is no longer collapsed by the destination height.

Final scoped verdict: **Spec — pass after S1 fix; code quality — pass, with 0 remaining actionable findings.** This supersedes the earlier changes-requested verdict. Native screenshot/build acceptance and device-scale contrast remain the root integration task's responsibility; this limited source review does not certify visual acceptance or claim a fresh test run.
