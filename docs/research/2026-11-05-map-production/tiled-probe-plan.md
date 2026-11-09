# Tiled edit-to-Cocos probe execution plan

Goal: validate approved small editor workflow using existing art, no new generated images or production game changes.

Architecture: Tiled edits projected-screen image objects; a converter maps image bottom-left to existing world-space anchors. The existing isolated Cocos viewer consumes converted layout. Map is authoritative for manual changes/deletions.

- [ ] Prepare finite map, locked road reference, image collection assets and coordinate converter in tiled-probe/.
- [ ] Obtain portable official Tiled in thread/tmp storage, inspect actual native UI, edit objects, save and reopen.
- [ ] Convert actual saved file; verify anchor positions and persistent IDs, then append without resetting manual edits.
- [ ] Copy existing isolated Cocos built viewer into a new probe-hosted directory; replace only its runtime art package, open and capture actual engine view.
- [ ] Record exact pass/fail for GUI persistence, coordinate conversion, engine rendering and manual edit preservation; leave source maps/assets intact.

No formal game/save tests or full-map production. Existing stage-testing restriction does not prohibit explicitly authorized isolated workflow validation. Downloaded app stays in temporary/thread storage; no system installation required.
