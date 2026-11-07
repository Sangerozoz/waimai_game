Two Minor verifier gaps were reproduced in memory and then fixed, without changing any image, graph, TMJ, area data, or source plan. Keep your same Codex/Sanger/max route and same read-only scope. No worktree/fork, files/configuration writes, image generation, game tests or old-thread reading.

Please review only the changed `verify_evidence.py` in this same directory and the new `verification/review-gap-reproduction.json` and `verification/static-artifact-checks.json`.

1. `planning_edge_matches` now requires exactly two vertices, complete object-name coverage and exact planning properties. Two in-memory probes reject an appended third vertex and a changed `from` property.
2. `offset_by_line_intersections` independently constructs intersections of adjacent shifted supporting lines. Each of128 net/sensitivity polygons must match all vertices and area, not just halfplane containment. A probe rejects an extra1m deduction.

Fresh standalone verification passed125 checks. Confirm whether the two named findings are resolved; give precise remaining issues if any. Do not repeat the whole original artifact review or claim additional game/browser/GUI acceptance. Return findings in your final message.
