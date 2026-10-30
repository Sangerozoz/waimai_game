# Independent review — phone safe area

Reviewed the scoped design/plan and production changes against the saved baseline. Ran `node scripts/test-map.cjs` in `delivery-game`: 133 tests passed, zero failed. No production files or game saves changed; no browser automation used.

## Findings

### [P2] Remap browser safe edges when Cocos rotates its portrait canvas

Location: `delivery-game/assets/scripts/map-sample/MapSample.ts:103` (also the foreground read at line 91).

The build configuration explicitly sets web-mobile orientation to `portrait`. On a landscape phone, Cocos 3.8.8's web screen adapter sets `isFrameRotated`, rotates GameDiv by +90 degrees, and swaps the logical window dimensions. However, its `safeAreaEdge` getter still reads the physical CSS `--safe-top/bottom/left/right` values unchanged; `sys.getSafeAreaRect(false)` then calls `_convertToUISpace`, which only subtracts the viewport offset and divides by scale. Neither operation rotates those edges. Treating that returned rect as already aligned with the rotated game moves padding onto the wrong axis.

Concrete example before any SHOW_ALL letterboxing: an 844 × 390 landscape browser with physical left notch inset 59 CSS pixels and bottom home-indicator inset 21 produces logical design insets `{left:108.92,bottom:38.77,top:0,right:0}` at logical width 720. With the engine's +90-degree canvas rotation, the correct logical insets are `{bottom:108.92,right:38.77,top:0,left:0}`. The menu retains insufficient bottom clearance and can remain under the notch; the physical bottom gesture strip is likewise applied to the wrong logical edge. Letterbox intersection reduces the required clearance but does not correct its axis. The +90-degree mapping is game top = browser right, bottom = browser left, left = browser top, right = browser bottom (DOM y grows downward, UI y upward).

Normalize the browser safe-area edges into the engine canvas orientation before converting/intersecting them, or configure a layout that does not CSS-rotate the canvas and handle landscape explicitly. Add a regression exercising the actual portrait-lock rotation mapping rather than only passing preconverted rectangles to the HUD harness.

Engine evidence inspected locally: `pal/screen-adapter/web/screen-adapter.js` (`safeAreaEdge`, `_windowSizeInCssPixels`, `_updateFrameState`, `_resizeFrame`); `cocos/core/platform/sys.ts:371–408`; `cocos/ui/view.ts:586–590`. All are under `/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/resources/3d/engine/`.

### [P3] Apply horizontal safe bounds to the map footer as well

Location: `delivery-game/assets/scripts/map-sample/MapSample.ts:108` (CityMap's footer construction at `CityMap.ts:57–60`).

The new layout computes left/right insets and applies them to header/menu/sheet controls, but supplies CityMap only a vertical footer offset. Its scale label stays at design x = -334…-224, its scale line at -327…-267, and its attribution touch target at -71…339. With the same asymmetric safe rectangle used by the new test (`x:42,width:620`, hence centered safe bounds -318…302), the scale label/line and attribution extend into unsafe side space. The design explicitly includes scale/attribution avoidance. Pass the horizontal usable region into the map footer and add actual footer-node bounds assertions; the current test named for attribution only examines the mocked CityMap constructor's vertical geometry.

## Scoped re-review — both findings resolved

Inspected `rotatedViewportInsets`, `MapSample.readSafeInsets`, and the updated actual CityMap footer construction. The +90-degree mapping now matches the engine's CSS rotation; its CSS-frame scaling and centered SHOW_ALL offsets precede clipping. Both foreground and rebuild reads share the same reader, and the alternate path is restricted to GameDiv's actual inline 90-degree rotation. The unrotated/native engine path remains intact. Scale nodes now include the left inset, and attribution's right edge/available width incorporate horizontal safe bounds.

Independently reran `node scripts/test-map.cjs` after these fixes: **135 passed, zero failed**, including the two new regressions for left/right physical notches plus the home indicator and the actual footer labels/stroke endpoints. No outstanding concrete P1/P2/P3 issues found in this scoped re-review. Actual device appearance remains unverified; no browser or user-save interaction was performed.
