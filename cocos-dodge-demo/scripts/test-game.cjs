const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const root = path.resolve(__dirname, '..');
const editor = process.env.COCOS_CREATOR || '/Applications/Cocos/Creator/3.8.8/CocosCreator.app';
const ts = require(path.join(editor, 'Contents/Resources/app.asar.unpacked/node_modules/typescript'));
const source = path.join(root, 'assets/scripts/GameSession.ts');
const outputDir = fs.mkdtempSync(path.join(os.tmpdir(), 'cocos-dodge-tests-'));
try {
  const result = ts.transpileModule(fs.readFileSync(source, 'utf8'), {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2020 },
  });
  const output = path.join(outputDir, 'GameSession.cjs');
  fs.writeFileSync(output, result.outputText);
  const run = spawnSync(process.execPath, ['--test', path.join(root, 'tests/game-session.test.cjs')], {
    stdio: 'inherit', env: { ...process.env, GAME_SESSION_MODULE: output },
  });
  process.exitCode = run.status === null ? 1 : run.status;
} finally {
  fs.rmSync(outputDir, { recursive: true, force: true });
}
