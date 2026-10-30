# Reference profile header implementation

Status: source implementation and automated verification complete; actual Cocos render / preview / build reserved for the main agent.

- Rounded-square 104-unit code avatar overlaps the identity plate by14 units, with8 units before the nickname text. Nickname sits above a yellow XP track. White outer card, cream plates, yellow badges and ink text preserve the project palette without shadows.
- Separate horizontal wallet / rating pills use leading ¥ / 评 badges. The wallet numeric label omits its repeated ¥ and preserves every monetary digit. Its font stays at least body size; long values wrap and grow the header. Station placement follows the actual header height. Existing bottom controls and SampleUI were not edited.
- Pure `experienceProgress` derives both boundaries by a bounded integer binary search calling `countyExperienceLevel`; no XP threshold table or business rule was added. Tests cover0..50,50..185,185..367 and a safe-integer upper bound.

Validation (working directory `delivery-game`):

| Command | Exit | Result / raw log |
| --- | --- | --- |
| Inline Cocos TypeScript compile harness, then `node --test tests/map-hud.test.cjs` with temporary `MAP_ROUTER_MODULE` |0|30/30; `hud-tests.log` |
| `npm test` |0|27 domain +143 map +18 county-store +4 map-data =192 passing; `full-tests.log` |
| `npm run typecheck` |0|No diagnostics; `typecheck.log` |

Final full tests include320/393/430 layouts, asymmetric30/50 side safe areas, white card / inset preservation, separate group bounds, badge/value separation including maximum safe balance, and actual XP fill refresh across level boundaries. Final full suite and typecheck each ran once.

SHA comparison against all102 baseline asset files found exactly the two authorized asset source changes (`MapSample.ts`, `PresentationLayout.ts`); `baseline-comparison.json` records the result. The relevant HUD test file is the only additional project file edited. No game/save, preview, browser, build, stage, commit or push action was taken.

Limits: HUD tests use Cocos node/graphics stubs and approximate text measurement. They verify layout geometry and progress calculations, not platform font glyph metrics, actual rounded-corner rasterization or final in-engine visual resemblance. Main agent should inspect the refreshed Cocos render before final delivery.

## Named review follow-up: normal XP rows

Compact XP text now uses `Lv.2 50/135`. Its font fits the available character width down to24 design units, with wrapping retained for extreme values. Header name and XP line heights now match their compact row calculation at `ceil(fontSize *1.2)`; XP height uses its actual fitted font. Normal0XP dimensions remain unchanged.

The existing reference geometry test now covers XP0/100/184/185 at320/393/430 and asserts a taller avatar, one-line nickname/XP, complete line-height containment and CLAMP overflow. MAX_SAFE_INTEGER XP retains the complete numeric label and expands its row at the24-unit font minimum.

Follow-up verification (each run once after the named edit): focused inline Cocos compile + `node --test tests/map-hud.test.cjs`:30/30, exit0 (`followup-hud-tests.log`); `npm test`:192/192, exit0 (`followup-full-tests.log`); `npm run typecheck`:exit0, no diagnostics (`followup-typecheck.log`). No build or preview was run.
