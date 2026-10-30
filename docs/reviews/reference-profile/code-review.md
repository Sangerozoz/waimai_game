# Reference profile — scoped review

**PASS: no actionable code blocker found in the supplied three-file change.**

Reviewed the brief, local reference image, exact revision diff, implementation report and supplied verification summaries. Follow-up source reads were limited to the authoritative XP function and the changed header line locations. No tests were rerun; no browser/game/save/build operations were performed.

- The information structure matches the approved scope: overlapping square avatar, nickname above an XP track, and adjacent wallet/rating pills with leading marks. White/cream/yellow styling is preserved. No energy, gems, plus buttons, economy fields or bottom-navigation changes appear in this diff.
- `experienceProgress` discovers start/end boundaries through `countyExperienceLevel`, using bounded binary searches instead of cloning a threshold table. The first boundaries 0/50/185/367 and level-transition resets are exercised by the new regression. Progress is clamped and finite, including the maximum safe integer input; update refreshes both text and actual fill geometry.
- Header width allocations remain separated. The avatar overlaps the identity plate by 14 units while clearing text by 8. In the ordinary uninset 320/393/430 states its 104-unit height exceeds the plate height. Longer XP text can increase the plate/header height. Numeric text receives its own width after the badge inset, a minimum body font and measured multiline height; live balance updates redraw/reposition the card and dependent station.
- **Compact identity text, `MapSample.ts:173`:** the assigned heights are below the full line boxes, but this alone does not prove clipping. For example, the 320 layout uses a 45-unit name box for font 34 / line-height 49, and a 40-unit one-line XP box for font 30 / line-height 43. Multiline height preserves the line-count term, reducing only outer space. This merits the planned native raster check; there is no confirmed clipping defect from the code or node mocks, so it is not reported as a blocker. Do not equate the geometry tests with actual glyph verification.

Provided full-test evidence records **192 passing tests** (27 domain +143 map +18 store +4 map-data), with typecheck exit 0 reported and no diagnostics. Relevant new checks cover XP boundaries/fill updates, reference structure, maximum-safe balance and asymmetric side safe areas.

**Current verdict: Spec PASS; Quality PASS.** Actual in-engine typography, reference resemblance and device rendering remain with the integrating agent's screenshot/preview verification.

## Final compact-XP follow-up — PASS

Reviewed only `followup-review-diff.txt` and supplied final verification summaries; no test reruns or runtime/save operations. The parent reports that the initial native normal-state screenshot matched the reference structure and rendered legibly.

The normal level-2 wrap risk is addressed directly: removing the decorative separator shortens the text, the XP font fits the available identity text width down to an explicit 24-unit minimum, and both header text labels now have an explicit 1.2 line height. Allocated heights include every counted line at that same line height plus 4 units. At the requested normal 320-width examples this retains one XP line and a plate shorter than the 104-unit avatar. Dynamic updates recompute the font, line count, plate, bar and card together; extended XP values preserve all digits by wrapping after the minimum font is reached. Wallet/rating layout, threshold derivation and the bottom navigation are unchanged by this follow-up.

The expanded regression checks 0/100/184/185 XP at all three requested widths, full single-line row allocation, avatar/plate hierarchy and extreme XP wrapping. Supplied final logs record **192 tests passing** and no typecheck diagnostics (reported exit 0). No new actionable functional regression was found in this bounded diff. The earlier compact-height concern is resolved at the code level; final native raster verification remains with the parent.

**Final scoped verdict: Spec PASS; Quality PASS.**
