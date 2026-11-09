// Authorized isolated compiler/validator regression; never touches runtime storage.
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const root = path.resolve(__dirname, '../..');
const editor = process.env.COCOS_CREATOR || '/Applications/Cocos/Creator/3.8.8/CocosCreator.app';
const ts = require(path.join(editor, 'Contents/Resources/app.asar.unpacked/node_modules/typescript'));

test('selectedMapId validators compile and reject malformed or unowned IDs without weakening legal kg/slots snapshots', async t => {
  const output = fs.mkdtempSync(path.join(os.tmpdir(), 'v2-selected-map-'));
  try {
    const program = ts.createProgram([path.join(root, 'assets/scripts/domain/V2EconomySession.ts')], {
      target: ts.ScriptTarget.ES2020, module: ts.ModuleKind.CommonJS, strict: true,
      noEmitOnError: true, rootDir: path.join(root, 'assets/scripts'), outDir: output,
      skipLibCheck: true, types: [],
    });
    const emitted = program.emit();
    const diagnostics = ts.getPreEmitDiagnostics(program).concat(emitted.diagnostics);
    assert.equal(diagnostics.length, 0, ts.formatDiagnosticsWithColorAndContext(diagnostics, {
      getCanonicalFileName: f => f, getCurrentDirectory: () => root, getNewLine: () => '\n',
    }));
    const { V2EconomySession, validateV2EconomySnapshot } = require(path.join(output, 'domain/V2EconomySession.js'));
    for (const profile of ['kg-v1', 'slots-v1']) {
      await t.test(`${profile}: legal initial and purchased selected maps survive validation/restoration`, () => {
        const initial = new V2EconomySession(profile);
        const snapshot = JSON.parse(initial.serialize());
        assert.doesNotThrow(() => validateV2EconomySnapshot(snapshot));
        assert.equal(V2EconomySession.restore(initial.serialize()).state.selectedMapId, 1);
        snapshot.state.cashCents = 100000000;
        snapshot.state.ledger.opening.balanceCents = snapshot.state.cashCents;
        const funded = V2EconomySession.restore(JSON.stringify(snapshot));
        funded.buyMap(2); funded.selectMap(2);
        assert.equal(V2EconomySession.restore(funded.serialize()).state.selectedMapId, 2);
      });
      await t.test(`${profile}: unknown, noninteger, out-of-range and unowned selected maps reject`, () => {
        const source = new V2EconomySession(profile).serialize();
        for (const selectedMapId of [undefined, null, true, false, '1', {}, [], NaN, Infinity, -1, 0, 1.5, 6, Number.MAX_SAFE_INTEGER, 2]) {
          const snapshot = JSON.parse(source);
          snapshot.state.selectedMapId = selectedMapId;
          assert.throws(() => validateV2EconomySnapshot(snapshot), undefined, String(selectedMapId));
          assert.throws(() => V2EconomySession.restore(JSON.stringify(snapshot)), undefined, String(selectedMapId));
        }
      });
    }
  } finally {
    fs.rmSync(output, { recursive: true, force: true });
  }
});
