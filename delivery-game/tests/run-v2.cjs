// Explicit isolated suite; execute only with current product-test authorization.
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {spawnSync}=require('node:child_process');
const root=path.resolve(__dirname,'..');
const editor=process.env.COCOS_CREATOR||'/Applications/Cocos/Creator/3.8.8/CocosCreator.app';
const ts=require(path.join(editor,'Contents/Resources/app.asar.unpacked/node_modules/typescript'));
const output=fs.mkdtempSync(path.join(os.tmpdir(),'delivery-v2-test-'));
try{
 const program=ts.createProgram(['map-sample/V2GameSession.ts','map-sample/PlaceCatalog.ts','map-sample/CountyV2Session.ts','map-sample/CountySaveStore.ts','map-sample/V2RuntimeStore.ts','domain/V2DispatchSession.ts','domain/V2FleetSession.ts','domain/V2ProgressTargets.ts'].map(f=>path.join(root,'assets/scripts',f)),{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS,strict:true,noEmitOnError:true,rootDir:path.join(root,'assets/scripts'),outDir:output,skipLibCheck:true,types:[]});
 const result=program.emit(),diagnostics=ts.getPreEmitDiagnostics(program).concat(result.diagnostics);
 if(diagnostics.length){process.stderr.write(ts.formatDiagnosticsWithColorAndContext(diagnostics,{getCanonicalFileName:f=>f,getCurrentDirectory:()=>root,getNewLine:()=> '\n'}));process.exitCode=1;}
 else{
  const defaults=['v2-route.test.cjs','v2-trip-rules.test.cjs','v2-supply-inventory.test.cjs','v2-ledger-targets.test.cjs','v2-economy.test.cjs','v2-county-adapter.test.cjs','v2-fleet.test.cjs','v2-dispatch.test.cjs','rewards-v2.test.cjs'];
  const regression=path.join(__dirname,'product-regression-1106');
  if(fs.existsSync(regression))defaults.push(...fs.readdirSync(regression).filter(f=>f.endsWith('.test.cjs')).sort().map(f=>path.join('product-regression-1106',f)));
  const files=process.argv.length>2?process.argv.slice(2):defaults;
  for(const file of files)if(!defaults.includes(file))throw new Error('Unknown isolated V2 test file: '+file);
  const result=spawnSync(process.execPath,['--test',...files.map(f=>path.join(__dirname,f))],{stdio:'inherit',env:{...process.env,MAP_ROUTER_MODULE:path.join(output,'map-sample/RoadRouter.js')}});process.exitCode=result.status??1;
 }
}finally{fs.rmSync(output,{recursive:true,force:true});}
