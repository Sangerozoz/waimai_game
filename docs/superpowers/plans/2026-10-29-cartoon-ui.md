# Cartoon UI Implementation Plan

> **For agentic workers:** Use subagent-driven-development for the production UI task; root handles image generation and integration verification. Steps use checkbox syntax for tracking.

**Goal:** Apply the user's three approved dimensional cartoon references to the playable delivery game and generate reusable original art.

**Architecture:** Keep domain/state modules intact. One shared atlas loader and the existing shared rendering helpers supply the new art and chrome to all current views. Preserve existing dimensions and reflow contracts wherever possible.

**Tech Stack:** Cocos Creator 3.8.8, TypeScript, builtin ImageGen, PNG sprite atlases, existing Node test harnesses.

## Global Constraints

- Work in the current `codex/food-delivery` checkout because almost the entire current game is untracked; recovery copies and SHA baselines are saved before mutation. Do not reset, stash, move, or commit unrelated user work.
- User has approved the visual direction and implementation. Do not pause for another design/implementation approval.
- Preserve all domain rules, save data, callbacks, disabled entries, responsive safety, and manual user testing boundary.
- Original art remains intact; new generated art lives under `map-sample/cartoon`.
- All interface text remains native labels.

## Task 1: Generate and register the artwork (root)

- [x] Save three reference images and recovery copies of all production scripts.
- [x] Generate a transparent 12-icon atlas: courier, recruitment, scooter, map, bills, station, coin, star, food bag, close, locate, confirm.
- [x] Generate a transparent vehicle atlas: D and D+ side views above corresponding north-facing top views.
- [x] Generate a transparent 16-dish atlas matching `FoodCatalog.ts` ordering.
- [x] Generate four blank dimensional panel/button frames.
- [x] Save exact prompts and metadata in `output/imagegen/cartoon-ui/manifest.json`.

## Task 2: Implement the unified playable skin (one implementation agent)

**Files:** Create `delivery-game/assets/scripts/map-sample/CartoonArt.ts`; modify `SampleUI.ts`, `PresentationLayout.ts`, `MapSample.ts`, `OrderPhone.ts`, `CityMap.ts`, `FoodImages.ts`, `MapVehicle.ts`, `VehicleSideArt.ts`; update relevant existing test boundaries, adding atlas behavior tests only when needed.

**Interfaces:** `cartoonArt(parent:Node,key:string,x:number,y:number,width:number,height:number,fallback?:Node):Node` loads one resource atlas selected by key and fits its crop into the requested box. Key mapping and normalized crop rectangles are in the asset manifest provided by root. Expose loader helpers to MapVehicle if needed to preserve its late-response tier protection. Shared helpers continue to export existing `C`, `item`, `box`, `button`, `icon`, `label`, `tap` APIs.

- [x] Read the spec, existing scripts and current test harnesses, then run `npm test` and `npm run typecheck` to logs.
- [x] Implement the atlas loader with cache, failure retry, parent/picture strict validity and no reactivation after close. Cover new asynchronous behavior before implementation; avoid redundant style assertions.
- [x] Give components thick white/blue rims, dimension, consistent highlight and text styling, while keeping click bounds unchanged.
- [x] Integrate original icons throughout the header/navigation/controls and new vehicle/dish art through existing presentation boundaries.
- [x] Restyle the phone, general sheets/dialogs and map colors to the approved direction while preserving functionality and safe area contracts.
- [x] Run relevant checks, typecheck, and full tests; record exact output and modified file list in `docs/reviews/cartoon-reskin/implementation-report.md`.

## Task 3: Review, build and deliver (root plus independent reviewer)

- [x] Compare all scripts against the baseline and confirm only rendering/presentation modules changed.
- [x] Review spec compliance and code quality with a scoped baseline diff package; fix important findings before delivery.
- [x] Run `npm test`, `npm run typecheck`, `npm run build:map`; save logs in `docs/reviews/cartoon-reskin/`.
- [x] Use Cocos tools to import assets and refresh the native Game View, then capture the actual home screenshot without gameplay actions.
- [x] Update current art direction in `delivery-game/README.md` and `docs/asset-library.md`, preserving older history and manual testing boundary.
- [x] Deliver actual preview and art-directory links, with clear limits for user-only flow/phone acceptance.

Final evidence: `docs/reviews/cartoon-reskin/delivery-report.md`. Implementation/build/static home verification are complete; player flow and device visual acceptance remain manual.
