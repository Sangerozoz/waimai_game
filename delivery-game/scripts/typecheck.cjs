const { spawnSync } = require('node:child_process');
const path = require('node:path');
const editor = process.env.COCOS_CREATOR || '/Applications/Cocos/Creator/3.8.8/CocosCreator.app';
const compiler = path.join(editor, 'Contents/Resources/app.asar.unpacked/node_modules/typescript/lib/tsc.js');
const run = spawnSync(process.execPath, [compiler, '--noEmit', '--pretty', 'false'], {
  cwd: path.resolve(__dirname, '..'), stdio: 'inherit',
});
process.exitCode = run.status === null ? 1 : run.status;
