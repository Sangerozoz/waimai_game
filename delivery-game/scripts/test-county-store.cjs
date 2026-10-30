const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const root = path.resolve(__dirname, '..');
const editor = process.env.COCOS_CREATOR || '/Applications/Cocos/Creator/3.8.8/CocosCreator.app';
const ts = require(path.join(editor, 'Contents/Resources/app.asar.unpacked/node_modules/typescript'));
const output = fs.mkdtempSync(path.join(os.tmpdir(), 'delivery-county-store-tests-'));
try {
  const program = ts.createProgram([path.join(root, 'assets/scripts/map-sample/CountySaveStore.ts')], {
    target: ts.ScriptTarget.ES2015,
    module: ts.ModuleKind.CommonJS,
    strict: true,
    noEmitOnError: true,
    rootDir: path.join(root, 'assets/scripts'),
    outDir: output,
    skipLibCheck: true,
    types: [],
  });
  const emitted = program.emit();
  const diagnostics = ts.getPreEmitDiagnostics(program).concat(emitted.diagnostics);
  if (diagnostics.length) {
    process.stderr.write(ts.formatDiagnosticsWithColorAndContext(diagnostics, {
      getCanonicalFileName: file => file,
      getCurrentDirectory: () => root,
      getNewLine: () => '\n',
    }));
    process.exitCode = 1;
  } else {
    const run = spawnSync(process.execPath, ['--test', path.join(root, 'tests/county-save-store.test.cjs')], {
      stdio: 'inherit',
      env: { ...process.env, COUNTY_SAVE_STORE_MODULE: path.join(output, 'map-sample/CountySaveStore.js') },
    });
    process.exitCode = run.status === null ? 1 : run.status;
  }
} finally {
  fs.rmSync(output, { recursive: true, force: true });
}
