const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { spawnSync } = require('node:child_process');

const root = path.resolve(__dirname, '..');
const editor = process.env.COCOS_CREATOR || '/Applications/Cocos/Creator/3.8.8/CocosCreator.app';
const ts = require(path.join(editor, 'Contents/Resources/app.asar.unpacked/node_modules/typescript'));
const output = fs.mkdtempSync(path.join(os.tmpdir(), 'delivery-domain-tests-'));
try {
  const sources = ['GameConfig.ts', 'DeliverySession.ts'].map(name => path.join(root, 'assets/scripts/domain', name));
  const program = ts.createProgram(sources, {
    target: ts.ScriptTarget.ES2020,
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
    const run = spawnSync(process.execPath, ['--test', path.join(root, 'tests/delivery-session.test.cjs')], {
      stdio: 'inherit',
      env: { ...process.env, DELIVERY_SESSION_MODULE: path.join(output, 'domain/DeliverySession.js') },
    });
    process.exitCode = run.status === null ? 1 : run.status;
  }
} finally {
  fs.rmSync(output, { recursive: true, force: true });
}
