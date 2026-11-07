# Read-only map evidence review

You are an independent MAP reviewer, not product staff. Use only this short brief and named current map files. Do not read long old chat histories, make a worktree/fork, modify any files/configuration, run full-game tests, open game sessions/saves, send other workers work, or generate images. Return your review in your final message; the parent writes the review record. Do not use GPT-6-astra. Requested execution: provider `codex`, exact model `ccs-sanger/gpt-6.1-sol`, reasoning `max`, environment `env_e54zrbdgxt`, same checkout `/Users/sanger/Documents/ChatGPT/taptap 2`.

Review the current uncommitted standalone artifact (not unrelated changes in this shared checkout):

- `docs/art/2026-11-07-map-sanger-continuation/road-evidence-002/PLAN.md`
- `trace-input.json`, `build_evidence.py`, `verify_evidence.py`, `viewer-template.html`
- `actual-graph.json`, `planning-graph.json`, `planning-land-ledger.json`
- `tiled/actual-eight.tmj`, `tiled/whole-city-planning.tmj`
- `verification/static-artifact-checks.json`, `verification/tiled-cli-v1/commands.json`, `verification/tiled-cli-v1/result.json`
- The original image is `../builtin-capacity-002/native.png` (1672×941, SHA256 71748e21f4ee55193ae5ee2ec06310c17ed178c5014388853cbe8523918abb94). Use an image-view tool to compare roads to the trace.
- Only as normative source: `docs/art/2026-11-06-city-image-map/planning/scope-recovery-v1/CITY-CONTRACT.md` and `scope-plan.json`.

Paths without a directory above are relative to `road-evidence-002/`. Treat author-generated hashes and passing checks as evidence to inspect, not a reason to skip independent judgment. You may run read-only Python checks without writing files or caches.

Check two axes:

1. **Spec/truthfulness**: native bytes unaltered; eight actual complete blocks; 31-node/38-edge graph really follows visible asphalt; no invented metre mapping or ordinary region admission; no unsupported lane semantics; planning remains a separate inherited proposal;住宅约半 is conditional assigned-block net only, not a completed blue-zone denominator. Current ordinary regions remain A2/B1/C and D has not resumed. No full-city/half-area/4K/user acceptance claim.
2. **Artifact correctness**: exact common endpoints and planar crossings; route and excluded-edge behavior; TMJ coordinate and property round-trip; convex land offset calculations; browser viewer source and relative images; generated-file guard protects future hand edits. Installed Tiled is 1.12.2 per app Info.plist; rasterizer reports its own 1.0 utility version. Official CLI exports passed but GUI/game/user acceptance are not certified.

Provide specific findings with file:line, severity Critical/Important/Minor, impact and fix. Separate artwork limitations (repeat-looking commercial building combination, warm lit-window appearance or low detail if visible) from code correctness; this sample has no user art approval. Give a clear verdict for publishing **standalone evidence only**, not production city readiness. Do not rewrite any file. Report what you actually inspected and checks you actually ran.
