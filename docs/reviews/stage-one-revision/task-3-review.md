# Task 3 independent review

Date: 2026-10-28. Read-only source/spec/quality review of the supplied Task3 delta against `task-2-end-snapshot.zip`. The review wrote only this report. Task4 acceptance/build-script work is excluded from the Task3 verdict.

## SPEC — PASS (static and recorded automated evidence)

Critical: 0. Important: 0. Minor: 0. No actionable spec defects found.

- `OrderPhone.ts:34–51` retains ten rows, no pagination, a masked ScrollView, `cancelInnerEvents`, and the existing movement-aware tap helper. Cards show picture, meal/servings, merchant, customer address, expected income, combined pickup/delivery distance, and expected duration. Only urgent/fragile labels remain.
- `MapSample.ts:159–177` preserves the removed decision information after acceptance: weight, fragility, direct/door demand, deadline, per-route risk, selection and return. Every accepted-route estimate uses `book.timingForRoute`, including the selected running route, so frozen historic timing is respected.
- `MapSample.ts:184–212,249–264` automatically presents direct completion after advance and doorstep completion after the choice. Receipt opening/closing contains no settlement or reward mutation. Confirmation calls finish before rebuilding the idle panel and opening the next phone.
- `ReceiptPresentation.ts:4–11` uses completed-order number plus order ID to suppress repeated automatic presentation within a session; a restored receipt may be presented once using its saved award. Manual reopening stays available. `MapSample.ts:72–89,240–246` preserves an open receipt across resize, leaves a dismissed receipt closed, deactivates the old root immediately and creates one active modal.
- `MapSample.ts:224–282` reads vehicle speed, upgrade amount, capacity and income factors from COUNTY_VEHICLES. Current values are D 12km/h, D+ 13.2km/h, ¥200, with consistent 50-XP/fifth-order text. No obsolete pause entry/status or ¥320 price remains in the reviewed UI. The remaining numeric 320 is progress-bar geometry.

## QUALITY — PASS (static)

Critical: 0. Important: 0. Minor: 0. No actionable quality defects found.

- `FoodImages.ts:6–24` caches one local texture and at most sixteen retained SpriteFrames for the application session. No per-opening texture/frame accumulation is introduced. `FoodImages.ts:28–34` checks strict validity and active hierarchy before touching nodes after asynchronous completion, including deferred ancestor destruction; load failure resets the shared promise for retry.
- The installed Cocos 3.8.8 engine source confirms Texture2D-backed SpriteFrame texture/rect/originalSize setters and CUSTOM sprite sizing support the implementation. Its ScrollView capture handler cancels child events after movement and stops the eventual touch end, matching the existing tap handling.
- PNG inspection confirms 1254×1254 pixels and sixteen catalog-ordered foods. Rounded boundaries compute 313/314px crops from the actual texture dimensions, stay inside the atlas, and do not assume a 1024px image. Metadata exposes the expected texture subasset and clamp/linear/no-mipmap settings.
- The Task3 snapshot copies of FoodImages, OrderPhone, MapSample and ReceiptPresentation match live source. Recorded protected hashes match live Main.scene, old DeliverySession, GameConfig and city.json; the two protected domain files also match the Task2 ZIP. Main.scene/city.json are not members of that source ZIP, so no direct ZIP comparison of those two is claimed.

## Verification evidence and limits

Reviewed `task-3-red.log`: the two behavioral presentation tests fail at the intended assertions, with the earlier 51 checks passing. Reviewed `task-3-green.log`: 53 pass / 0 fail. Reviewed `task-3-all-tests.log`: 27 legacy + 53 map/county + 18 store tests, all zero failures, and 4 Python map-data tests OK. Reviewed the clean typecheck output and implementation report. Per assignment, this reviewer did not rerun the full suite.

No browser, renderer, Cocos import/build, persisted-save injection or live user-save mutation was performed. These verdicts do not claim visual acceptance: actual image import/rendering, text legibility, scroll gestures, modal input blocking, runtime resize and a browser reload remain runtime acceptance checks. The user's earlier acceptance results were not modified.
