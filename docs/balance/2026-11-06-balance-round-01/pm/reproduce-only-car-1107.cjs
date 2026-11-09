// Isolated reproduction through production public methods; never reads storage.
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os');
const assert=require('node:assert/strict'),crypto=require('node:crypto');
const ROOT=path.resolve(__dirname,'../../../..');
const source=path.join(ROOT,'delivery-game/assets/scripts');
const ts=require('/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/app.asar.unpacked/node_modules/typescript');
const scratch=fs.mkdtempSync(path.join(os.tmpdir(),'pm-only-car-1107-'));
const digest=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const report={scope:'Fresh in-memory current-city public-command reproduction; no browser, user save, reward, or wallet injection.',startedAt:new Date().toISOString(),command:process.argv,checkpoints:[],errors:{},fixtures:{}};
let exitCode=0;
try{
 const program=ts.createProgram(['map-sample/V2GameSession.ts','map-sample/PlaceCatalog.ts'].map(f=>path.join(source,f)),{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS,strict:true,noEmitOnError:true,rootDir:source,outDir:scratch,skipLibCheck:true,types:[]});
 const emission=program.emit(),diagnostics=ts.getPreEmitDiagnostics(program).concat(emission.diagnostics);
 if(diagnostics.length)throw new Error(ts.formatDiagnosticsWithColorAndContext(diagnostics,{getCanonicalFileName:f=>f,getCurrentDirectory:()=>ROOT,getNewLine:()=> '\n'}));
 report.compilerExit=0;
 report.sourceHashes=Object.fromEntries(program.getSourceFiles().filter(f=>f.fileName.startsWith(source+path.sep)).map(f=>[path.relative(ROOT,f.fileName),digest(f.fileName)]));
 const {V2GameSession}=require(path.join(scratch,'map-sample/V2GameSession.js'));
 const {prepareCity}=require(path.join(scratch,'map-sample/PlaceCatalog.js'));
 const city=prepareCity(JSON.parse(fs.readFileSync(path.join(ROOT,'delivery-game/assets/resources/map-sample/city.json'),'utf8')));
 const game=new V2GameSession(city,0);let now=0,sequence=0;
 const state=()=>game.dispatch.economyState;
 const tick=seconds=>{now+=seconds;game.tick(++sequence,now,true,false);};
 const checkpoint=label=>report.checkpoints.push({label,atSeconds:now,cashCents:state().cashCents,heroCompletedOrders:state().heroCompletedOrders,riders:state().riders,fleet:game.dispatch.fleetState});
 checkpoint('fresh100coins2slots');
 game.acceptBatch([game.normalCandidates()[0]]);
 game.beginTrip(game.routeChoices()[0].preference);
 for(let i=0;state().heroCompletedOrders===0&&i<1000;i++){
  const phase=game.route.progress.phase;
  if(phase==='pickup')game.pickup();
  else if(phase==='ready')game.continueTrip();
  else tick(.5);
 }
 assert.equal(state().heroCompletedOrders,1);
 assert.equal(state().cashCents,12000);
 checkpoint('firstDeliveryCompleted');
 game.dispatch.command({type:'hireRider',riderId:'npc-1'});
 game.dispatch.command({type:'assignVehicle',riderId:'hero',vehicleId:null});
 game.dispatch.command({type:'assignVehicle',riderId:'npc-1',vehicleId:'starter-1'});
 report.fixtures.beforeNPCSigning=JSON.parse(game.serialize());
 tick(60);
 assert.equal(state().cashCents,0);
 assert.equal(game.dispatch.fleetState.quotaMs,0);
 assert.ok(state().fleetQuotes.length>0);
 checkpoint('quotaExhaustedOldContractsReserved');
 report.fixtures.signedZeroQuota=JSON.parse(game.serialize());
 for(const [label,command] of [
  ['detachNPC',{type:'assignVehicle',riderId:'npc-1',vehicleId:null}],
  ['returnToHero',{type:'assignVehicle',riderId:'hero',vehicleId:'starter-1'}],
  ['buyReplacement',{type:'buyVehicle',modelId:1}]
 ]){
  try{game.dispatch.command(command);report.errors[label]=null;}
  catch(error){report.errors[label]=error.message;}
 }
 assert.equal(report.errors.detachNPC,null);
 assert.match(report.errors.returnToHero,/旧批次/);
 assert.match(report.errors.buyReplacement,/余额不足/);
 const originalContracts=JSON.stringify(state().fleetQuotes);
 game.supply('rest');tick(game.tripState.action.durationSeconds);
 assert.equal(game.dispatch.fleetState.quotaMs,0);
 assert.equal(JSON.stringify(state().fleetQuotes),originalContracts);
 assert.equal(game.normalCandidates().length,0);
 checkpoint('freeRestDidNotRefillQuotaOrReleaseContracts');
 const raw=game.serialize();
 assert.equal(V2GameSession.restore(city,raw,{preserveClock:true}).serialize(),raw);
 report.restoreValidated=true;
 report.sourceDrift=Object.entries(report.sourceHashes).filter(([p,h])=>digest(path.join(ROOT,p))!==h);
 assert.deepEqual(report.sourceDrift,[]);
 report.status='REPRODUCED_ZERO_CASH_ZERO_QUOTA_RESERVED_ONLY_CAR';
}catch(error){exitCode=1;report.status='REPRODUCTION_FAILED';report.error=error.stack;}
finally{
 fs.rmSync(scratch,{recursive:true,force:true});report.scratchRemoved=!fs.existsSync(scratch);
 report.exitCode=exitCode;report.finishedAt=new Date().toISOString();
 fs.writeFileSync(path.join(__dirname,'only-car-reproduction-1107.json'),JSON.stringify(report,null,2)+'\n');
 console.log(JSON.stringify({status:report.status,exitCode,scratchRemoved:report.scratchRemoved,errors:report.errors,checkpoints:report.checkpoints.map(c=>({label:c.label,atSeconds:c.atSeconds,cashCents:c.cashCents,quotaMs:c.fleet.quotaMs,batches:c.fleet.batches.length})),error:report.error},null,2));
 process.exitCode=exitCode;
}
