// Tests the argument expression from the actual Cocos-built orders() callsite,
// paired with the real strict loadSummary/LoadRules helpers. Not a whole-render test.
const {test}=require('node:test');const assert=require('node:assert/strict');
const fs=require('node:fs'),path=require('node:path'),vm=require('node:vm'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'..');
const ts=require(path.join(process.env.COCOS_CREATOR||'/Applications/Cocos/Creator/3.8.8/CocosCreator.app','Contents/Resources/app.asar.unpacked/node_modules/typescript'));
const build=process.env.UI_GAME_BUILD_ROOT||path.join(root,'build/v2-tick-follow-1106');
const bundleDir=path.join(build,'assets/main'),bundle=path.join(bundleDir,fs.readdirSync(bundleDir).find(name=>/^index\.[^.]+\.js$/.test(name)));
const bytes=fs.readFileSync(bundle),built=bytes.toString('utf8'),start=built.indexOf('本批车辆条款缺失');
assert.notEqual(start,-1,'actual planned-order block must exist in build');
const match=/([A-Za-z_$][\w$]*)\(((?:\[\]\.concat|Array\.from)\(([A-Za-z_$][\w$]*)\.values\(\)\)),([A-Za-z_$][\w$]*)\)/.exec(built.slice(start,start+1000));
assert.ok(match,'locate actual batch-Map argument expression rather than a synthetic replacement');
const loadScope={exports:{}};
vm.runInNewContext(ts.transpileModule(fs.readFileSync(path.join(root,'assets/scripts/domain/V2LoadRules.ts'),'utf8'),{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText,loadScope);
const ui=fs.readFileSync(path.join(root,'assets/scripts/map-sample/V2GameUI.ts'),'utf8'),ast=ts.createSourceFile('V2GameUI.ts',ui,ts.ScriptTarget.Latest,true,ts.ScriptKind.TS);
const declaration=ast.statements.find(node=>ts.isFunctionDeclaration(node)&&node.name?.text==='loadSummary');assert.ok(declaration);
const scope={exports:{},parseV2Capacity:loadScope.exports.parseV2Capacity,totalV2Load:loadScope.exports.totalV2Load};
vm.runInNewContext(ts.transpileModule(declaration.getText(ast)+'\nexports.loadSummary=loadSummary;',{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText,scope);
function summary(loads,capacity){const batch=new Map(loads.map((load,index)=>['order-'+index,load]));const actualArgument=vm.runInNewContext(match[2],{[match[3]]:batch});return scope.exports.loadSummary(actualArgument,capacity);}
test('Cocos planned slots batch receives actual load records, not one Map iterator',t=>{
 t.diagnostic(JSON.stringify({bundle,sha256:crypto.createHash('sha256').update(bytes).digest('hex'),actualExpression:match[2]}));
 assert.equal(summary([{version:'slots-v1',occupiedSlots:2}],{version:'slots-v1',capacitySlots:2}),'2/2格');
});
test('Cocos grouped slots summary enumerates each accepted order',()=>{
 assert.equal(summary([{version:'slots-v1',occupiedSlots:1},{version:'slots-v1',occupiedSlots:1}],{version:'slots-v1',capacitySlots:2}),'2/2格');
});
test('Cocos historical kg summary retains the old unit and valid exact total',()=>{
 assert.equal(summary([{version:'kg-v1',weightKg:1.25},{version:'kg-v1',weightKg:.75}],{version:'kg-v1',capacityKg:5}),'2/5kg');
});
test('strict capacity rules continue rejecting mixed units',()=>{
 assert.throws(()=>summary([{version:'kg-v1',weightKg:1}],{version:'slots-v1',capacitySlots:2}),/配送容量单位或条款无效/);
});
