'use strict';
// Reuses existing model evidence, transpiling source in memory only. No browser,
// save adapter, Cocos build output, clock alteration or source mutation.
const fs=require('node:fs'),path=require('node:path'),Module=require('node:module');
const assert=require('node:assert/strict'),crypto=require('node:crypto');
const {performance}=require('node:perf_hooks');
const root=path.resolve(__dirname,'../../../../..');
const scripts=path.join(root,'delivery-game/assets/scripts');
const fleetFile=path.join(scripts,'domain/V2FleetSession.ts');
const beforeFile=path.join(__dirname,'source-before/V2FleetSession.ts');
const tsPath=path.join(process.env.COCOS_CREATOR||'/Applications/Cocos/Creator/3.8.8/CocosCreator.app','Contents/Resources/app.asar.unpacked/node_modules/typescript');
const ts=require(tsPath),sha=value=>crypto.createHash('sha256').update(value).digest('hex');
const before=fs.readFileSync(beforeFile,'utf8'),after=fs.readFileSync(fleetFile,'utf8');
const inputBefore=JSON.parse(fs.readFileSync(path.join(__dirname,'input-before.json'),'utf8'));
for(const row of inputBefore.files){
 if(row.path==='delivery-game/assets/scripts/domain/V2FleetSession.ts')assert.equal(sha(before),row.sha256);
 else if(row.path==='delivery-game/tests/product-regression-1106/hero-sync-noop.test.cjs')continue; // Revised test is not loaded by this model benchmark.
 else assert.equal(sha(fs.readFileSync(path.join(root,row.path))),row.sha256,`input drift: ${row.path}`);
}

function variant(name,fleetSource){
 const cache=new Map(),loaded=[];
 function load(file){
  file=path.resolve(file);assert.ok(file.startsWith(scripts+path.sep));
  if(cache.has(file))return cache.get(file).exports;
  const m=new Module(file,module);cache.set(file,m);m.filename=file;
  m.require=id=>{assert.ok(id.startsWith('.'),`unexpected source dependency ${id}`);return load(path.resolve(path.dirname(file),id+'.ts'));};
  const source=file===fleetFile?fleetSource:fs.readFileSync(file,'utf8');
  loaded.push({path:path.relative(root,file),sha256:sha(source)});
  const code=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;
  m._compile(code,file);return m.exports;
 }
 const {V2GameSession:Game}=load(path.join(scripts,'map-sample/V2GameSession.ts'));
 const {prepareCity}=load(path.join(scripts,'map-sample/PlaceCatalog.ts'));
 const city=prepareCity(JSON.parse(fs.readFileSync(path.join(root,'delivery-game/assets/resources/map-sample/city.json'),'utf8')));
 return {name,Game,city,loaded};
}

const variants=[variant('frozen-before',before),variant('actual-after',after)];
const longPath='docs/balance/2026-11-06-balance-round-01/a/long-term-1107/run-01/end-state.json';
const originalPath='docs/balance/2026-11-06-balance-round-01/pm/only-car-reproduction-1107.json';
const longRaw=fs.readFileSync(path.join(root,longPath),'utf8');
const originalBytes=fs.readFileSync(path.join(root,originalPath));
const emergency=JSON.stringify(JSON.parse(originalBytes).fixtures.signedZeroQuota);

// Derive a travelling input solely through the same real Game/Route methods in
// both variants; the archived original terminal remains byte-for-byte unchanged.
function travelling(v){
 const g=v.Game.restore(v.city,longRaw,{preserveClock:true}),actions=[];
 let {nowSeconds:now,sequence}=g.dispatch.tickContext;
 assert.equal(g.route.progress.phase,'pickup');g.pickup();actions.push({command:'pickup'});
 for(let i=0;i<20&&g.route.progress.phase==='service';i++){
  g.tick(++sequence,now+=.25,true,false);actions.push({command:'tick',sequence,nowSeconds:now});
 }
 assert.equal(g.route.progress.phase,'ready');g.continueTrip();actions.push({command:'continueTrip'});
 assert.equal(g.route.progress.phase,'travelling');
 return {raw:g.serialize(),actions};
}
const derived=variants.map(travelling);assert.equal(derived[0].raw,derived[1].raw);
const workloads=[
 {name:'new-empty',raw:new variants[0].Game(variants[0].city).serialize(),source:'new game in memory'},
 {name:'existing-150min-pickup',raw:longRaw,source:longPath},
 {name:'existing-150min-travelling',raw:derived[0].raw,source:longPath,derivation:derived[0].actions},
 {name:'signed-zero-quota-terminal',raw:emergency,source:originalPath+'#fixtures.signedZeroQuota'},
];

function run(v,raw){
 const start=performance.now(),g=v.Game.restore(v.city,raw,{preserveClock:true}),restored=performance.now();
 const c=g.dispatch.tickContext;g.tick(c.sequence+1,c.nowSeconds+1/30,true,false);const ticked=performance.now();
 const serialized=g.serialize(),saved=performance.now();
 v.Game.restore(v.city,serialized,{preserveClock:true});const end=performance.now();
 return {serialized,sample:{restoreBeforeMs:restored-start,tickMs:ticked-restored,serializeMs:saved-ticked,restoreAfterMs:end-saved,totalMs:end-start,outputSHA256:sha(serialized)}};
}
const stats=values=>{const sorted=values.slice().sort((a,b)=>a-b),middle=Math.floor(sorted.length/2);return {medianMs:sorted.length%2?sorted[middle]:(sorted[middle-1]+sorted[middle])/2,minMs:sorted[0],maxMs:sorted[sorted.length-1]};};
const results=[];
for(const workload of workloads){
 const samples=[[],[]];let compared=0;
 // Warm both modules twice. Reverse execution order on alternate iterations to
 // reduce ordering bias; there are no wall-time assertions in the unit suite.
 for(let i=0;i<10;i++){
  const pair=[];
  for(const index of i%2?[1,0]:[0,1])pair[index]=run(variants[index],workload.raw);
  assert.equal(pair[0].serialized,pair[1].serialized,workload.name);compared++;
  if(i>=2)for(let index=0;index<2;index++)samples[index].push(pair[index].sample);
 }
 const raw=JSON.parse(workload.raw),summary=samples.map((rows,index)=>({variant:variants[index].name,total:stats(rows.map(r=>r.totalMs)),tick:stats(rows.map(r=>r.tickMs))}));
 results.push({name:workload.name,source:workload.source,derivation:workload.derivation||null,inputSHA256:sha(workload.raw),inputBytes:Buffer.byteLength(workload.raw),heroCompletedOrders:raw.dispatch.economy.state.heroCompletedOrders,npcCompletedOrders:raw.dispatch.economy.state.npcCompletedOrders,phase:raw.route.phase,byteEqualComparisons:compared,summary,medianTotalReductionPercent:(1-summary[1].total.medianMs/summary[0].total.medianMs)*100,samples});
}
process.stdout.write(JSON.stringify({status:'PASS_PAIRED_MODEL_TRANSACTION_ONLY',recordedAt:new Date().toISOString(),scope:'in-memory source restore/tick/serialize/full-restore candidate; no disk commit, UI rendering, FPS, real player storage or fresh long-term simulation',medianPolicy:'arithmetic mean of the two middle values for eight retained samples',node:process.version,platform:process.platform,architecture:process.arch,sourceBeforeSHA256:sha(before),sourceAfterSHA256:sha(after),fixtureSources:[{path:longPath,sha256:sha(longRaw)},{path:originalPath,sha256:sha(originalBytes)}],loadedInputs:variants.map(v=>({variant:v.name,files:v.loaded})),byteEqualComparisons:results.reduce((sum,r)=>sum+r.byteEqualComparisons,0),results},null,2)+'\n');
