# Cocos H5 Dodge Game Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task with checkpoints.

**Goal:** Prepare a macOS Cocos Creator environment and build a small Web Mobile dodge game that can be opened in a browser without installation.

**Architecture:** Use a Cocos Creator 3.8 LTS project with one main scene and four focused TypeScript components. `GameController` owns game state and score, `PlayerController` owns input and player bounds, `ObstacleSpawner` owns obstacle creation and cleanup, and `HUD` owns score/game-over UI. The first version uses colored primitives and text so the workflow exercises the engine and browser build instead of asset production.

**Tech Stack:** Cocos Creator 3.8 LTS, TypeScript, Cocos Web Mobile build, Node.js/npm for local scripts, Python `http.server` for local browser serving.

## Global Constraints

- Use Cocos Creator 3.8 LTS and TypeScript.
- Target the Web Mobile platform first.
- Do not add external art, audio, ads, payments, networking, accounts, or TapTap CLI integration in this prototype.
- Keep the project at `cocos-dodge-demo/` in the current repository.
- Do not commit Cocos cache folders or browser build output.
- Verify behavior in a browser; a successful TypeScript edit alone is not acceptance.
- If Git metadata remains read-only in the sandbox, keep changes in the workspace and report the exact blocked commit command instead of claiming a commit.

---

### Task 1: Prepare Cocos Creator and verify the local toolchain

**Files:**
- Create: `cocos-dodge-demo/` through Cocos Dashboard's project creation flow.
- Modify: `.gitignore` to exclude Cocos caches and build output.

**Interfaces:**
- Produces: a working Cocos Creator 3.8 LTS editor installation and an empty project directory at `cocos-dodge-demo/`.

- [ ] **Step 1: Verify the existing prerequisites**

Run:

```bash
node --version
npm --version
mdfind "kMDItemFSName == 'CocosDashboard.app'" | head -20
mdfind "kMDItemFSName == 'CocosCreator.app'" | head -20
```

Expected: Node and npm print versions; the Cocos searches either print existing app paths or no result.

- [ ] **Step 2: Install Cocos Dashboard when it is missing**

Open the official Cocos Creator download page:

```text
https://www.cocos.com/creator-download
```

Download the macOS Cocos Dashboard DMG, drag `CocosDashboard.app` into `/Applications`, and launch it. Log in only if the Dashboard requires an account before downloading an editor.

- [ ] **Step 3: Install the 3.8 LTS editor from Dashboard**

In Dashboard, open the editor install list and install the available Cocos Creator 3.8 LTS release. If the list shows the patch release, use 3.8.8 so the project matches the current 3.8 LTS documentation.

Expected: Dashboard lists the installed 3.8 LTS editor and can launch it.

- [ ] **Step 4: Create the empty project**

Create a new empty project named `cocos-dodge-demo` at:

```text
/Users/sanger/Documents/ChatGPT/taptap/cocos-dodge-demo
```

Open it in the installed 3.8 LTS editor and verify that the editor can load the project without an import error.

- [ ] **Step 5: Add repository ignores before adding game files**

Add these patterns to `.gitignore`:

```gitignore
cocos-dodge-demo/temp/
cocos-dodge-demo/library/
cocos-dodge-demo/local/
cocos-dodge-demo/build/
cocos-dodge-demo/.cache/
```

Run:

```bash
git diff --check
```

Expected: no whitespace errors. If `.git` is writable, commit with `chore: prepare cocos creator project`; otherwise record the blocked commit and continue.

### Task 2: Create the main scene and the game state shell

**Files:**
- Create: `cocos-dodge-demo/assets/scenes/Main.scene` through the Cocos editor.
- Create: `cocos-dodge-demo/assets/scripts/GameController.ts`.
- Create: `cocos-dodge-demo/assets/scripts/HUD.ts`.

**Interfaces:**
- `GameController.startGame(): void`
- `GameController.endGame(): void`
- `GameController.restartGame(): void`
- `GameController.addScore(amount: number): void`
- `HUD.setScore(score: number): void`
- `HUD.showPlaying(): void`
- `HUD.showGameOver(score: number): void`
- `HUD.onRestartRequested: (() => void) | null`

- [ ] **Step 1: Create the initial scene nodes**

In `Main.scene`, create and name these nodes:

```text
Main
├── Background
├── Player
├── Obstacles
├── HUD
│   ├── ScoreLabel
│   ├── GameOverLabel
│   └── RestartButton
└── GameController
```

Use a solid background color, a colored rectangle for `Player`, and a vertical container for the HUD. Set the canvas to a portrait Web Mobile layout.

- [ ] **Step 2: Implement the state shell**

Define:

```ts
export enum GameState {
  Ready = 'ready',
  Playing = 'playing',
  GameOver = 'game-over',
}
```

`GameController` starts in `Ready`, sets score to `0`, transitions to `Playing` on the first start, and clears score plus child obstacle nodes in `restartGame()`.

- [ ] **Step 3: Implement HUD methods**

`HUD.setScore()` updates the score label. `showPlaying()` hides the game-over label and restart button. `showGameOver()` displays the final score and restart button. The restart button must call `onRestartRequested` instead of reaching into `GameController` directly.

- [ ] **Step 4: Run the editor preview**

Open `Main.scene`, press Preview/Play, and verify that the scene opens with the background, player block, score text, and hidden game-over UI. Stop the preview and check the Cocos console for errors.

Expected: the scene renders and no script import error appears.

### Task 3: Add player input and movement

**Files:**
- Create: `cocos-dodge-demo/assets/scripts/PlayerController.ts`.
- Modify: `cocos-dodge-demo/assets/scenes/Main.scene` to attach `PlayerController` to `Player`.

**Interfaces:**
- `PlayerController.setInput(axis: number): void`
- `PlayerController.setTargetX(x: number): void`
- `PlayerController.resetPosition(): void`
- `PlayerController.getBounds(): Rect`
- `Rect` is imported from `cc` and represents the player's world-space bounds.

- [ ] **Step 1: Define the movement contract**

Use a normalized horizontal axis in `[-1, 1]`. `setInput(-1)` moves left, `setInput(1)` moves right, and `setInput(0)` stops acceleration. Clamp the player position so its full width stays inside the visible game area.

- [ ] **Step 2: Add keyboard input**

Subscribe to Cocos input events in `onEnable()` and unsubscribe in `onDisable()`. Map left arrow/A to `-1`, right arrow/D to `1`, and release to `0`.

- [ ] **Step 3: Add touch drag input**

On touch start and move, convert the touch position into the player's local coordinate space and call `setTargetX()`. Clamp the target before applying it so mobile dragging cannot move the player outside the canvas.

- [ ] **Step 4: Verify input in the browser preview**

Run the scene in the browser preview. Verify keyboard movement in a desktop browser and touch/drag movement using the browser's mobile emulation. Confirm the player cannot leave the left or right boundary.

### Task 4: Add obstacle spawning, collision, scoring, and restart

**Files:**
- Create: `cocos-dodge-demo/assets/scripts/ObstacleSpawner.ts`.
- Modify: `cocos-dodge-demo/assets/scripts/GameController.ts` to consume obstacle events and collision checks.
- Modify: `cocos-dodge-demo/assets/scenes/Main.scene` to attach `ObstacleSpawner` to `Obstacles`.

**Interfaces:**
- `ObstacleSpawner.startSpawning(): void`
- `ObstacleSpawner.stopSpawning(): void`
- `ObstacleSpawner.reset(): void`
- `ObstacleSpawner.updateGame(deltaTime: number): void`
- `ObstacleSpawner.onObstacleEscaped: (() => void) | null`
- `ObstacleSpawner.onPlayerHit: (() => void) | null`

- [ ] **Step 1: Define deterministic obstacle rules**

Use a spawn interval of `0.9` seconds, a downward speed of `420` pixels per second, and a random horizontal position that keeps the obstacle fully visible at spawn time. Use a fixed obstacle size so collision behavior is predictable.

- [ ] **Step 2: Implement spawn and cleanup**

Create colored rectangle nodes under `Obstacles`. Move active obstacles downward each frame. When an obstacle leaves the bottom of the visible area, remove it and invoke `onObstacleEscaped` once.

- [ ] **Step 3: Implement collision detection**

Compare the player's world-space rectangle with each active obstacle rectangle. On the first overlap, stop spawning, invoke `onPlayerHit`, and prevent additional score changes until restart.

- [ ] **Step 4: Wire the state transitions**

`GameController.startGame()` starts the spawner. `onObstacleEscaped` calls `addScore(1)`. `onPlayerHit` calls `endGame()`, updates the HUD, and disables further input. `restartGame()` resets the player, spawner, HUD, score, and state in that order.

- [ ] **Step 5: Verify the complete loop**

Run the browser preview and verify:

```text
ready -> playing -> score increases -> collision -> game-over -> restart -> playing
```

Expected: one collision produces one game-over state, and restarting removes all previous obstacles and resets the score to zero.

### Task 5: Build and serve the Web Mobile version

**Files:**
- Modify: `cocos-dodge-demo/settings/` only if the Cocos build panel writes project-specific Web Mobile settings.
- Create: `cocos-dodge-demo/scripts/serve-web.sh`.
- Modify: `.gitignore` to exclude the final build directory if it is created inside the project.

**Interfaces:**
- `scripts/serve-web.sh <build-directory>` starts a local HTTP server for the built game.

- [ ] **Step 1: Configure the Web Mobile build**

In Cocos Creator's Build panel, choose Web Mobile, set the build output to `/private/tmp/cocos-dodge-demo-web`, and build the project.

Expected: the build finishes successfully and writes an HTML entry point plus generated JavaScript/Wasm/assets.

- [ ] **Step 2: Add the local serving script**

Create `scripts/serve-web.sh` with:

```bash
#!/usr/bin/env bash
set -euo pipefail

build_dir="${1:?usage: scripts/serve-web.sh <build-directory>}"
cd "$build_dir"
exec python3 -m http.server "${PORT:-8080}"
```

Make it executable:

```bash
chmod +x cocos-dodge-demo/scripts/serve-web.sh
```

- [ ] **Step 3: Serve and open the build**

Run:

```bash
cocos-dodge-demo/scripts/serve-web.sh /private/tmp/cocos-dodge-demo-web
```

Open `http://127.0.0.1:8080/` in a browser. Do not open the generated HTML with `file://`; browser security rules require an HTTP server.

- [ ] **Step 4: Perform browser acceptance checks**

Verify all of the following in the built Web Mobile version:

1. The game loads without a JavaScript or asset error.
2. The player responds to keyboard input and touch emulation.
3. Obstacles spawn, move downward, and disappear below the viewport.
4. The score increases after obstacles are avoided.
5. Collision shows the final score and restart button.
6. Restart returns to a clean playing state.
7. The browser console has no uncaught exception during the loop.

- [ ] **Step 5: Record the runnable result**

Write `cocos-dodge-demo/README.md` with the installed Cocos version, the preview steps, the build command/location, and the local serving command. Include the browser URL used for the successful smoke test.

### Task 6: Final verification and handoff

**Files:**
- Modify: `cocos-dodge-demo/README.md` with final verification results.
- Modify: `.gitignore` if the verification reveals generated files that should not be tracked.

**Interfaces:**
- Produces: a reproducible Cocos H5 prototype and a short runbook for continuing development.

- [ ] **Step 1: Run repository checks**

Run:

```bash
git diff --check
```

Expected: no whitespace errors in the final tracked files.

- [ ] **Step 2: Re-run the browser smoke test after a clean build**

Delete `/private/tmp/cocos-dodge-demo-web`, build Web Mobile again, serve it on a new local port, and repeat the seven acceptance checks from Task 5.

- [ ] **Step 3: Inspect the final diff**

Run:

```bash
git status --short
git diff --stat
```

Confirm that only the design/plan documents, Cocos project source, and intentional ignore/runbook files are present. Confirm that `library/`, `temp/`, `local/`, and build output are absent from the diff.

- [ ] **Step 4: Commit when repository metadata permits**

Use these commits at the task boundaries when `.git` is writable:

```bash
git add .gitignore cocos-dodge-demo
git commit -m "feat: add cocos h5 dodge game"
```

If the sandbox still rejects `.git/index.lock`, leave the verified files in place and report that the code is ready but uncommitted because of the filesystem restriction.
