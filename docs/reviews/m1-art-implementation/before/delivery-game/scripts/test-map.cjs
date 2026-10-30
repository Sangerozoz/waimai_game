const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const {spawnSync} = require('node:child_process');
const root = path.resolve(__dirname, '..');
const ts = require('/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/app.asar.unpacked/node_modules/typescript');
const output = fs.mkdtempSync(path.join(os.tmpdir(), 'delivery-map-test-'));
try {
 const dir = path.join(root, 'assets/scripts/map-sample');
 const program = ts.createProgram(['MapTypes.ts','CityExtent.ts','SafeAreaLayout.ts','PlaceCatalog.ts','FoodCatalog.ts','RoadRouter.ts','DeliveryClock.ts','CountyRules.ts','OrderBook.ts','ReceiptPresentation.ts','BillingPresentation.ts'].map(f=>path.join(dir,f)), {target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS,strict:true,noEmitOnError:true,rootDir:path.join(root,'assets/scripts'),outDir:output,skipLibCheck:true,types:[]});
 const emission=program.emit();
 const diagnostics=ts.getPreEmitDiagnostics(program).concat(emission.diagnostics);
 if(diagnostics.length) { console.error(ts.formatDiagnosticsWithColorAndContext(diagnostics,{getCanonicalFileName:f=>f,getCurrentDirectory:()=>root,getNewLine:()=> '\n'})); process.exitCode=1; }
 else {const run=spawnSync(process.execPath,['--test',...['map-routing','map-gestures','map-vehicle','map-hud','tap-gestures','city-content','food-selection','delivery-clock','damage-events','billing','order-book','county-rules','county-session','receipt-presentation','modal-shade','stage-one-feedback'].map(name=>path.join(root,`tests/${name}.test.cjs`))],{stdio:'inherit',env:{...process.env,MAP_ROUTER_MODULE:path.join(output,'map-sample/RoadRouter.js')}});process.exitCode=run.status ?? 1;}
} finally {fs.rmSync(output,{recursive:true,force:true});}
