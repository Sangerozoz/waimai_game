// Isolated domain TDD only. Writes are confined to this receipt directory and a unique scratch.
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const assert=require('node:assert/strict'),crypto=require('node:crypto');
const {spawnSync}=require('node:child_process');
const HERE=__dirname,ROOT=path.resolve(HERE,'../../../../..');
const SOURCE=path.join(ROOT,'delivery-game/assets/scripts');
const A=path.join(ROOT,'docs/balance/2026-11-06-balance-round-01/a');
const mode=process.argv[2];assert.ok(['red','green','capture-history'].includes(mode),'Expected red, green or capture-history');
const tag=process.argv[3]||mode;assert.match(tag,/^[a-z0-9-]+$/);
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const json=file=>JSON.parse(fs.readFileSync(file,'utf8'));
const write=(name,data)=>fs.writeFileSync(path.join(HERE,name),typeof data==='string'?data:JSON.stringify(data,null,2)+'\n');
function walk(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?walk(path.join(dir,e.name)):[path.join(dir,e.name)]);}
const identity=json(path.join(A,'run-identity.json'));
function protectedHashes(){
 const files=new Set([...walk(SOURCE),...Object.keys(identity.sourceHashes).map(f=>path.join(ROOT,f))]);
 const manifest=json(path.join(A,'artifact-manifest.json'));
 for(const f of ['artifact-manifest.json',...Object.keys(manifest.files)])files.add(path.join(A,f));
 const oldB=path.dirname(HERE);
 for(const entry of fs.readdirSync(oldB,{withFileTypes:true})){
  const target=path.join(oldB,entry.name);if(target===HERE)continue;
  for(const file of entry.isDirectory()?walk(target):[target])files.add(file);
 }
 for(const file of ['v2-economy.test.cjs','v2-fleet.test.cjs','v2-dispatch.test.cjs','product-regression-1106/current-contract.test.cjs','product-regression-1106/helpers.cjs'])files.add(path.join(ROOT,'delivery-game/tests',file));
 for(const file of ['docs/balance/2026-11-06-balance-round-01/pm/only-car-reproduction-1107.json','docs/superpowers/specs/2026-11-07-hero-car-reserve-design.md','docs/superpowers/plans/2026-11-07-hero-car-reserve.md'])files.add(path.join(ROOT,file));
 return Object.fromEntries([...files].sort().map(f=>[path.relative(ROOT,f),sha(f)]));
}
const before=protectedHashes();
const sourceMismatches=Object.entries(identity.sourceHashes).filter(([file,hash])=>before[file]!==hash);
assert.deepEqual(sourceMismatches,[],'A36 input identity must match before any compile');
const scratch=fs.mkdtempSync(path.join(os.tmpdir(),'b-hero-car-reserve-1107-'));
const input=path.join(scratch,'scripts'),output=path.join(scratch,'compiled');
const record={mode,tag,startedAt:new Date().toISOString(),command:process.argv,runnerSHA256:sha(__filename),scratch,compilerExit:null,testExit:null,exitCode:1,protectedBefore:before,a36Before:identity.sourceHashes};
let testOutput='';
try{
 fs.cpSync(SOURCE,input,{recursive:true});
 record.overlays={};
 if(mode==='green')for(const file of ['V2EconomySession.ts','V2FleetSession.ts']){
  const from=path.join(HERE,'stage/domain',file);fs.copyFileSync(from,path.join(input,'domain',file));record.overlays[file]=sha(from);
 }
 const ts=require('/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/app.asar.unpacked/node_modules/typescript');
 const entries=['map-sample/V2GameSession.ts','map-sample/PlaceCatalog.ts','map-sample/V2RuntimeStore.ts','domain/V2DispatchSession.ts','domain/V2FleetSession.ts','domain/V2ProgressTargets.ts'];
 const options={target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS,strict:true,noEmitOnError:true,rootDir:input,outDir:output,skipLibCheck:true,types:[]};
 record.compilerVersion=ts.version;record.compilerOptions=options;
 const program=ts.createProgram(entries.map(f=>path.join(input,f)),options),emission=program.emit();
 const diagnostics=ts.getPreEmitDiagnostics(program).concat(emission.diagnostics);
 record.compilerExit=diagnostics.length?1:0;
 record.compiledSourceHashes=Object.fromEntries(program.getSourceFiles().filter(f=>f.fileName.startsWith(input+path.sep)).map(f=>[path.relative(input,f.fileName),sha(f.fileName)]));
 if(diagnostics.length)throw new Error(ts.formatDiagnosticsWithColorAndContext(diagnostics,{getCanonicalFileName:f=>f,getCurrentDirectory:()=>ROOT,getNewLine:()=> '\n'}));
 console.log(JSON.stringify({phase:'strict-domain-compile',mode,exit:0,compilerVersion:ts.version}));
 if(mode==='capture-history'){
  const {V2EconomySession}=require(path.join(output,'domain/V2EconomySession.js'));
  const {V2FleetSession}=require(path.join(output,'domain/V2FleetSession.js'));
  const fixtures={},actions={};
  for(const profile of ['kg-v1','slots-v1']){
   const e=new V2EconomySession(profile),f=new V2FleetSession(e,0),log=[];
   function deliver(id){if(e.usesSlots)e.acceptSlotBatch([{id,kind:'ordinary'}],{[id]:{deliveryMetres:100}});else e.acceptOrdinary(id);f.completeHeroDelivery(id);log.push({action:'completeHeroDelivery',id,cashCents:e.state.cashCents,quotaMs:f.state.quotaMs});}
   for(let i=0;i<3;i++)deliver('historic-reserve-'+profile+'-'+i);
   e.hireRider('npc-1');e.assignVehicle('hero',null);e.assignVehicle('npc-1','starter-1');
   log.push({action:'hireAndAssignOnlyCar',cashCents:e.state.cashCents,quotaMs:f.state.quotaMs});
   fixtures[profile]={beforeSigning:JSON.parse(f.serialize())};f.advanceTo(1000);
   fixtures[profile].signedRemaining=JSON.parse(f.serialize());
   assert.equal(f.state.quotaMs,179000);assert.equal(f.state.batches.length,1);
   assert.equal(V2FleetSession.restore(f.serialize()).serialize(),f.serialize());
   log.push({action:'advanceTo',nowMs:1000,cashCents:e.state.cashCents,quotaMs:f.state.quotaMs});
   const e2=new V2EconomySession(profile),f2=new V2FleetSession(e2,0);
   for(let i=0;i<30;i++){const id='historic-reservation-'+profile+'-'+i;if(e2.usesSlots)e2.acceptSlotBatch([{id,kind:'ordinary'}],{[id]:{deliveryMetres:100}});else e2.acceptOrdinary(id);f2.completeHeroDelivery(id);}
   const car=e2.buyVehicle(1);e2.assignVehicle('hero',car);e2.hireRider('npc-1');e2.hireRider('npc-2');e2.assignVehicle('npc-1','starter-1');f2.advanceTo(1000);
   e2.assignVehicle('npc-1',null);e2.assignVehicle('hero',null);e2.assignVehicle('npc-2',car);
   assert.equal(V2FleetSession.restore(f2.serialize()).serialize(),f2.serialize());
   fixtures[profile].reservedOldCarAndConfiguredNewCar=JSON.parse(f2.serialize());
   actions[profile]={signedRemaining:log,reservationFixture:{heroDeliveries:30,via:'public Economy/Fleet commands only',cashCents:e2.state.cashCents,quotaMs:f2.state.quotaMs,paidVehicleId:car}};
  }
  write('historical-fixtures.json',{scope:'Original production compiler output; fresh public Economy/Fleet commands only; no snapshot edits, wallet/quota injections, browser or storage.',sourceHashes:identity.sourceHashes,compilerVersion:ts.version,fixtures,actions});
  record.fixtureSHA256=sha(path.join(HERE,'historical-fixtures.json'));record.exitCode=0;
 }else{
  const test=path.join(HERE,'stage/tests/hero-car-reserve.test.cjs');
  const files=[test];
  if(mode==='green')files.push(...['v2-economy.test.cjs','v2-fleet.test.cjs','v2-dispatch.test.cjs','product-regression-1106/current-contract.test.cjs'].map(f=>path.join(ROOT,'delivery-game/tests',f)));
  record.testFiles=Object.fromEntries(files.map(f=>[path.relative(ROOT,f),sha(f)]));
  const args=['--test',...files];
  record.testCommand=[process.execPath,...args];
  const result=spawnSync(process.execPath,args,{encoding:'utf8',env:{...process.env,MAP_ROUTER_MODULE:path.join(output,'map-sample/RoadRouter.js'),HERO_CAR_RESERVE_ROOT:ROOT,HERO_CAR_RESERVE_HISTORY:path.join(HERE,'historical-fixtures.json')},maxBuffer:20*1024*1024});
  testOutput=(result.stdout||'')+(result.stderr||'');write(tag+'.log',testOutput);process.stdout.write(testOutput);
  record.testExit=result.status??1;record.testSignal=result.signal;record.spawnError=result.error?String(result.error):null;
  record.counts=Object.fromEntries(['tests','pass','fail','cancelled','skipped'].map(k=>[k,Number(new RegExp('^# '+k+' (\\d+)','m').exec(testOutput)?.[1]??-1)]));
  record.exitCode=record.testExit;
 }
}catch(error){record.error=error.stack;console.error(error.stack);record.exitCode=1;}
finally{
 fs.rmSync(scratch,{recursive:true,force:true});record.scratchRemoved=!fs.existsSync(scratch);
 const after=protectedHashes();record.protectedCount=Object.keys(before).length;record.protectedDrift=Object.entries(before).filter(([f,h])=>after[f]!==h).map(([file,before])=>({file,before,after:after[file]}));
 record.a36After=Object.fromEntries(Object.keys(identity.sourceHashes).map(f=>[f,sha(path.join(ROOT,f))]));record.a36Drift=Object.entries(identity.sourceHashes).filter(([f,h])=>record.a36After[f]!==h);
 if(record.protectedDrift.length||record.a36Drift.length||!record.scratchRemoved)record.exitCode=1;
 record.finishedAt=new Date().toISOString();write(tag+'-receipt.json',record);
 console.log(JSON.stringify({phase:'complete',mode,exit:record.exitCode,counts:record.counts,protectedCount:record.protectedCount,protectedDrift:record.protectedDrift,a36Drift:record.a36Drift,scratchRemoved:record.scratchRemoved}));
 process.exitCode=record.exitCode;
}
