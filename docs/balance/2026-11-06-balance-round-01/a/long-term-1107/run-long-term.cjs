/* Read-only production-domain long-term experiment. See strategy.md.
 * Adapted from ../run-model.cjs SHA256 9d2f23996e2f5f2a880d08e1db6366efe47a2ad7b17e302ed616384b578ff901.
 * No production writes, private-state replacement, reward outcomes or storage adapters.
 */
'use strict';
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const crypto = require('node:crypto');
const assert = require('node:assert/strict');
const cp = require('node:child_process');
const ROOT = path.resolve(__dirname, '../../../../..');
const FIRST = path.dirname(__dirname);
const SCRIPTS = path.join(ROOT, 'delivery-game/assets/scripts');
const sha = data => crypto.createHash('sha256').update(data).digest('hex');
const hashFile = file => sha(fs.readFileSync(file));
const json = (file, value) => fs.writeFileSync(file, JSON.stringify(value, null, 2) + '\n');
const cpuSeconds = () => { const v = process.cpuUsage(); return (v.user + v.system) / 1e6; };
const LIMITS = Object.freeze({cpuStopSeconds:270,cpuHardSeconds:300,wallHardSeconds:360,
  heroOrders:20000,events:200000,eventHeadroom:4096,iterations:100000,simulatedSeconds:604800});
const OP = Object.freeze({lobby:4,select:.6,route:2,pickup:1,continue:1,receipt:2,investment:3,supply:2});

function sourceHashes() {
  const expected = JSON.parse(fs.readFileSync(path.join(FIRST, 'run-identity.json'), 'utf8')).sourceHashes;
  assert.equal(Object.keys(expected).length, 36);
  return {expected,actual:Object.fromEntries(Object.keys(expected).map(f => [f,hashFile(path.join(ROOT,f))]))};
}
function firstRoundHashes() {
  const out = {};
  function walk(dir) {
    for (const entry of fs.readdirSync(dir, {withFileTypes:true})) {
      const file = path.join(dir, entry.name);
      if (file === __dirname) continue;
      if (entry.isDirectory()) walk(file);
      else if (entry.isFile()) out[path.relative(ROOT, file)] = hashFile(file);
    }
  }
  walk(FIRST); return out;
}
function differences(before, after) {
  return [...new Set([...Object.keys(before),...Object.keys(after)])].filter(f => before[f] !== after[f])
    .map(file => ({file,before:before[file] ?? null,after:after[file] ?? null}));
}

async function supervisor() {
  const runDir = path.join(__dirname, process.argv[2] || 'run-01');
  assert.equal(path.dirname(runDir), __dirname, 'run output must be an immediate child of authorized directory');
  fs.mkdirSync(runDir); // Never overwrite an earlier attempt.
  const startedAt = new Date().toISOString(), wallStart = performance.now();
  const inputs = sourceHashes(), roundBefore = firstRoundHashes();
  const identity = {startedAt,command:{executable:process.execPath,argv:process.argv,cwd:process.cwd()},
    modelSHA256:hashFile(__filename),strategySHA256:hashFile(path.join(__dirname,'strategy.md')),
    reusedCore:{file:path.relative(ROOT,path.join(FIRST,'run-model.cjs')),sha256:hashFile(path.join(FIRST,'run-model.cjs'))},
    protectedManifestSHA256:hashFile(path.join(ROOT,'docs/team/handoffs/2026-11-07-codex-migration/protected-artifacts.json')),
    limits:LIMITS,sourceHashes:inputs.actual,firstRoundHashes:roundBefore,requiredRouting:{provider:'codex',model:'ccs-sanger/gpt-6.1-sol',reasoning:'max'},
    nodeNote:'Existing PATH Node executable may reside under .hermes/node; it is used only as a local JS runtime, never an agent or provider.'};
  json(path.join(runDir,'run-identity.json'),identity);
  let scratch = null, childResult = null, compilerExit = null, unexpected = null;
  const log = fs.openSync(path.join(runDir,'run.log'),'wx');
  try {
    assert.deepEqual(inputs.actual,inputs.expected,'same 36 inputs must match the first round before execution');
    scratch = fs.mkdtempSync(path.join(os.tmpdir(),'balance-long-term-1107-'));
    identity.scratch = scratch;
    const ts = require('/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/app.asar.unpacked/node_modules/typescript');
    const options = {target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS,strict:true,noEmitOnError:true,
      rootDir:SCRIPTS,outDir:scratch,skipLibCheck:true,types:[]};
    const program = ts.createProgram(['map-sample/V2GameSession.ts','map-sample/PlaceCatalog.ts','domain/V2ProgressTargets.ts']
      .map(f => path.join(SCRIPTS,f)), options);
    const emitted = program.emit(), diagnostics = ts.getPreEmitDiagnostics(program).concat(emitted.diagnostics);
    const graph = program.getSourceFiles().filter(s => s.fileName.startsWith(SCRIPTS + path.sep)).map(s => path.relative(ROOT,s.fileName));
    assert.deepEqual(graph.slice().sort(),Object.keys(inputs.actual).filter(f => f.endsWith('.ts')).sort(),'unchanged compiled source graph');
    compilerExit = diagnostics.length ? 1 : 0;
    identity.compiler = {version:ts.version,options,exit:compilerExit,sourceCount:graph.length,supervisorCPUAfterCompile:cpuSeconds()};
    json(path.join(runDir,'run-identity.json'),identity);
    if (diagnostics.length) throw new Error(ts.formatDiagnosticsWithColorAndContext(diagnostics,
      {getCanonicalFileName:f=>f,getCurrentDirectory:()=>ROOT,getNewLine:()=> '\n'}));
    const args = ['-c','ulimit -t 300; exec "$@"','balance-long-term-worker',process.execPath,__filename,'--worker',runDir,scratch];
    fs.writeSync(log,JSON.stringify({type:'worker-command',executable:'/bin/sh',argv:args,compilerExit,limits:LIMITS})+'\n');
    console.log(JSON.stringify({step:'compiled',exit:0,inputCount:36,scratch,runDir}));
    childResult = await new Promise((resolve,reject) => {
      const child = cp.spawn('/bin/sh',args,{cwd:ROOT,stdio:['ignore','pipe','pipe']});
      let timedOut = false;
      const timer = setTimeout(() => {timedOut=true;child.kill('SIGKILL');}, LIMITS.wallHardSeconds*1000);
      for (const stream of [child.stdout,child.stderr]) stream.on('data',data => {fs.writeSync(log,data);process.stdout.write(data);});
      child.on('error',error=>{clearTimeout(timer);reject(error);});
      child.on('close',(code,signal)=>{clearTimeout(timer);resolve({code,signal,timedOut});});
    });
  } catch (error) { unexpected = {message:error.message,stack:error.stack};fs.writeSync(log,JSON.stringify({type:'supervisor-error',...unexpected})+'\n'); }
  finally {
    let cleanup = {scratch,removed:false};
    if (scratch) {fs.rmSync(scratch,{recursive:true,force:false});cleanup.removed=!fs.existsSync(scratch);}
    const after = sourceHashes(), roundAfter = firstRoundHashes();
    const execution = {startedAt,finishedAt:new Date().toISOString(),compilerExit,childResult,unexpected,
      supervisorCPUSeconds:cpuSeconds(),supervisorWallSeconds:(performance.now()-wallStart)/1000,cleanup,
      inputCount:36,inputChanges:differences(inputs.actual,after.actual),firstRoundFileCount:Object.keys(roundBefore).length,
      firstRoundChanges:differences(roundBefore,roundAfter),sourceHashesAfter:after.actual};
    json(path.join(runDir,'execution.json'),execution);
    fs.writeSync(log,JSON.stringify({type:'supervisor-finished',...execution,sourceHashesAfter:undefined})+'\n');fs.closeSync(log);
    console.log(JSON.stringify({step:'supervisor-finished',...execution,sourceHashesAfter:undefined}));
    process.exitCode = !unexpected && childResult?.code===0 && !execution.inputChanges.length && !execution.firstRoundChanges.length && cleanup.removed ? 0 : 1;
  }
}

class BoundedStop extends Error {constructor(kind,detail={}) {super(kind);this.kind=kind;this.detail=detail;}}

function worker(runDir, scratch) {
  const startWall = performance.now();
  const {V2GameSession} = require(path.join(scratch,'map-sample/V2GameSession.js'));
  const {prepareCity} = require(path.join(scratch,'map-sample/PlaceCatalog.js'));
  const {V2_SLOT_CONFIG:C} = require(path.join(scratch,'domain/V2SlotEconomyConfig.js'));
  const {slotVehiclePurchaseQuote,slotRiderHireQuote,slotMapPurchaseQuote,slotVehicleEffects} = require(path.join(scratch,'domain/V2EconomyProfiles.js'));
  const {slotCandidateRequestCount} = require(path.join(scratch,'domain/V2LoadRules.js'));
  const city = prepareCity(JSON.parse(fs.readFileSync(path.join(ROOT,'delivery-game/assets/resources/map-sample/city.json'),'utf8')));
  const g = new V2GameSession(city,0);
  let e = g.dispatch.economyState, now = 0, sequence = 0, iterations = 0, lastLedger = 0, eventCount = 0, taskIndex = 0;
  let stop = null, unexpected = null, batchCount = 0, lastProgressCPU = 0, nextStageTime = 3600;
  const spent = {vehicle_purchase:0,rider_hire:0,vehicle_upgrade:0,rider_upgrade:0,map_purchase:0,supply_purchase:0};
  const times = {manual:0,travel:0,service:0,supply:0};
  let heroIncome = 0,npcIncome = 0,heroQuoted = 0,signedSlots = 0,signedCapacity = 0,acceptedOrders = 0,roadMetres = 0;
  let quotaAdded = 0,quotaConsumed = 0,quotaClipped = 0,quotaStalled = 0,quotaNoWork = 0,quotaPeak = 0;
  const milestones = {firstCar:null,firstNPC:null,threeEquipped:null,asset80:null,assetFull:null};
  const stages = [],batches = [],receipts = [],supplies = [],quotes = new Map(),heroLedgerTimes = new Map();
  const eventFile = fs.openSync(path.join(runDir,'events.jsonl'),'wx');
  const commandFile = fs.openSync(path.join(runDir,'commands.jsonl'),'wx');
  const append = (fd,value) => fs.writeSync(fd,JSON.stringify(value)+'\n');
  function emit(type,data={}) {
    assert(eventCount<LIMITS.events,'hard event bound');
    append(eventFile,{event:++eventCount,atSeconds:now,type,...data});
  }
  function guard() {
    const cpu = cpuSeconds();
    if(cpu>=LIMITS.cpuStopSeconds) throw new BoundedStop('cpu-cooperative-limit',{cpuSeconds:cpu});
    if(e.heroCompletedOrders>=LIMITS.heroOrders) throw new BoundedStop('hero-order-limit',{heroOrders:e.heroCompletedOrders});
    if(eventCount>=LIMITS.events-LIMITS.eventHeadroom) throw new BoundedStop('event-headroom-limit',{eventCount});
    if(now>=LIMITS.simulatedSeconds) throw new BoundedStop('simulated-time-limit');
  }
  function collectLedger() {
    e = g.dispatch.economyState;
    const delta = e.ledger.entries.slice(lastLedger), heroRows = delta.filter(row=>row.category==='hero_ordinary'||row.category==='hero_special');
    const settled = heroRows.length ? new Map(g.dispatch.snapshot().orders.filter(o=>heroRows.some(r=>r.detail.orderId===o.id)).map(o=>[o.id,o])) : null;
    for (const row of delta) {
      emit('ledger-entry',{entry:row});
      if (row.category==='hero_ordinary'||row.category==='hero_special') {
        heroIncome+=row.amountCents;const id=row.detail.orderId,q=quotes.get(id),order=settled.get(id);
        assert(q,'every hero income has a real accepted quote');heroQuoted+=q.incomeCents;heroLedgerTimes.set(id,row.atMs);
        receipts.push({orderId:id,actor:'hero',ledgerAtMs:row.atMs,receivedCents:row.amountCents,quotedCents:q.incomeCents,
          slots:q.terms.load.occupiedSlots,capacitySlots:q.terms.capacity.capacitySlots,deliveryMetres:q.ordinaryPricing.deliveryMetres,
          vehicleId:q.vehicleId,damage:order.receipt.damage,lateGameSeconds:order.receipt.lateGameSeconds});
      } else if (row.category==='npc_delivery') {
        npcIncome+=row.amountCents;receipts.push({orderId:row.detail.orderId,actor:row.detail.riderId,vehicleId:row.detail.vehicleId,
          ledgerAtMs:row.atMs,receivedCents:row.amountCents});
      } else if (row.category in spent) {
        spent[row.category]-=row.amountCents;
        if(row.category==='supply_purchase') supplies.push({atMs:row.atMs,cents:-row.amountCents,...row.detail});
      }
    }
    lastLedger=e.ledger.entries.length;
    assert.equal(e.cashCents,10000+heroIncome+npcIncome-Object.values(spent).reduce((a,b)=>a+b,0),'cash conservation after every public mutation');
  }
  function assets(n,m,v) {
    const requiredNPCs=Array.from({length:n},(_,i)=>'npc-'+(i+1));
    const npcDone=requiredNPCs.filter(id=>e.riders.some(r=>r.id===id));
    const equipped=requiredNPCs.filter(id=>e.riders.some(r=>r.id===id&&r.vehicleId));
    const maps=Array.from({length:m},(_,i)=>i+1).filter(id=>e.ownedMapIds.includes(id));
    const models=Array.from({length:v},(_,i)=>i+1).filter(id=>e.vehicles.some(car=>car.modelId===id));
    const hero=e.riders.find(r=>r.id==='hero');
    return {requiredNPCs:n,ownedNPCs:npcDone.length,equippedNPCs:equipped.length,requiredMaps:m,ownedMaps:maps,
      requiredModels:v,ownedModels:models,catalogItems:npcDone.length+maps.length+models.length,
      catalogDenominator:n+m+v,heroVehicleId:hero.vehicleId,
      reached:npcDone.length===n&&equipped.length===n&&maps.length===m&&models.length===v&&!!hero.vehicleId};
  }
  function snapshot(label) {
    const f=g.dispatch.fleetState,actors=e.riders.map(r=>({...r}));
    const row={label,atSeconds:now,atMinutes:now/60,atHours:now/3600,cashCents:e.cashCents,heroIncomeCents:heroIncome,npcIncomeCents:npcIncome,
      totalIncomeCents:heroIncome+npcIncome,spentCents:{...spent},operatingNetCents:heroIncome+npcIncome-spent.supply_purchase,
      heroOrders:e.heroCompletedOrders,npcOrders:e.npcCompletedOrders,heroOrdersPerMinute:now?e.heroCompletedOrders/(now/60):0,
      allOrdersPerMinute:now?(e.heroCompletedOrders+e.npcCompletedOrders)/(now/60):0,acceptedOrders,batchCount,
      capacityFillRatio:signedCapacity?signedSlots/signedCapacity:0,meanOrdersPerBatch:batchCount?acceptedOrders/batchCount:0,
      signedSlots,signedCapacity,roadMetres,operationWallSeconds:{...times},quotaMs:f.quotaMs,quotaAddedMs:quotaAdded,
      quotaConsumedMs:quotaConsumed,quotaClippedMs:quotaClipped,quotaStalledSeconds:quotaStalled/1000,quotaNoWorkSeconds:quotaNoWork/1000,
      quotaPeakMs:quotaPeak,quotaUtilization:quotaAdded?quotaConsumed/quotaAdded:0,pendingNPCBatches:f.batches.length,
      selectedMapId:e.selectedMapId,ownedMapIds:e.ownedMapIds,hireCount:e.hireCount,equippedNPCs:actors.filter(r=>r.id!=='hero'&&r.vehicleId).length,
      vehicles:e.vehicles.map(v=>({...v,effects:slotVehicleEffects(v)})),riders:actors,asset80:assets(24,4,8),assetFull:assets(30,5,10),
      stamina:g.tripState.stamina,phase:g.route.progress.phase,workerCPUSeconds:cpuSeconds(),workerElapsedSeconds:(performance.now()-startWall)/1000,
      taskIndex,nextTask:tasks[taskIndex]??null,eventCount,iterations};
    stages.push(row);json(path.join(runDir,'checkpoint.json'),row);emit('stage',{stage:row});return row;
  }
  function checkMilestones() {
    const actors=e.riders.filter(r=>r.id!=='hero'&&r.vehicleId);
    const small=(key,ok)=>{if(!milestones[key]&&ok){milestones[key]=snapshot(key);console.log(JSON.stringify({step:'milestone',name:key,seconds:now,hero:e.heroCompletedOrders,npc:e.npcCompletedOrders,cashCents:e.cashCents}));}};
    small('firstCar',e.vehicles.some(v=>typeof v.modelId==='number'));
    small('firstNPC',e.hireCount>0&&actors.length>0);
    small('threeEquipped',actors.length>=3);
    small('asset80',assets(24,4,8).reached);
    small('assetFull',assets(30,5,10).reached);
  }
  function tickTo(end,label,bucket) {
    guard();const before=g.dispatch.fleetState,prior=e,oldEvents=prior.heroCompletionEvents.length,start=now;
    g.tick(++sequence,end,true,false);now=end;times[bucket]+=end-start;collectLedger();
    const after=g.dispatch.fleetState,newEvents=e.heroCompletionEvents.slice(oldEvents);
    const configuredWorker=prior.riders.some(r=>r.id!=='hero'&&r.vehicleId);
    let workRemaining=configuredWorker?Infinity:Math.max(0,...before.batches.map(b=>b.orders[b.orders.length-1].dueMs-b.elapsedMs));
    let q=before.quotaMs,cursor=before.lastAdvancedAt,consumed=0,clipped=0,stalled=0,noWork=0,added=0;
    function spendUntil(at) {
      assert(at>=cursor);const elapsed=at-cursor;
      if(workRemaining>0) {const work=Math.min(q,elapsed,workRemaining);q-=work;consumed+=work;workRemaining-=work;
        if(workRemaining===0)noWork+=elapsed-work;else stalled+=elapsed-work;
      } else noWork+=elapsed;
      cursor=at;
    }
    for(const row of newEvents) {
      const at=heroLedgerTimes.get(row.id);assert(Number.isSafeInteger(at));spendUntil(at);
      const n=row.teamCompletedAfter,capacity=n>=700?1800000:n>=240?1500000:n>=60?1200000:900000,credit=n>=700?180000:n>=60?120000:60000;
      clipped+=Math.max(0,q+credit-capacity);q=Math.min(capacity,q+credit);added+=credit;quotaPeak=Math.max(quotaPeak,q);
    }
    spendUntil(Math.floor(end*1000));assert.equal(q,after.quotaMs,'exact finite shared-quota accounting');
    quotaAdded+=added;quotaConsumed+=consumed;quotaClipped+=clipped;quotaStalled+=stalled;quotaNoWork+=noWork;quotaPeak=Math.max(quotaPeak,after.quotaMs);
    assert.equal(quotaAdded,after.quotaMs+quotaConsumed+quotaClipped);
    emit('tick',{sequence,fromSeconds:start,toSeconds:now,label,bucket,phase:g.route.progress.phase,
      quotaBeforeMs:before.quotaMs,quotaAfterMs:after.quotaMs,quotaAddedMs:added,quotaConsumedMs:consumed,quotaClippedMs:clipped,quotaStalledMs:stalled,quotaNoWorkMs:noWork});
    if(now>=nextStageTime){snapshot('hour-boundary-observation');nextStageTime=(Math.floor(now/3600)+1)*3600;}
  }
  function advance(seconds,label,bucket='manual') {
    guard();const end=Math.min(LIMITS.simulatedSeconds,now+Math.max(0,seconds));
    if(end>now)tickTo(end,label,bucket);
  }
  const wait=(seconds,label)=>advance(seconds,label,'manual');
  function cmd(command) {
    guard();const before=e.cashCents,ledgerBefore=lastLedger;
    const value=g.dispatch.withLedgerTime(now,()=>g.dispatch.command(command));collectLedger();
    const row={atSeconds:now,command,result:value??null,cashBeforeCents:before,cashAfterCents:e.cashCents,
      ledgerEntryIds:e.ledger.entries.slice(ledgerBefore).map(r=>r.id)};
    append(commandFile,row);emit('public-command',row);checkMilestones();return value;
  }
  function investment(command) {wait(OP.investment,'investment menu');return cmd(command);}
  function heroCar(modelId) {
    const id=investment({type:'buyVehicle',modelId});cmd({type:'assignVehicle',riderId:'hero',vehicleId:null});cmd({type:'assignVehicle',riderId:'hero',vehicleId:id});
    assert(g.dispatch.hasEquippedVehicle);return id;
  }
  function freeCar() {
    const reserved=new Set(g.dispatch.fleetState.batches.map(b=>b.vehicleId));
    return e.vehicles.find(v=>!e.riders.some(r=>r.vehicleId===v.id)&&!reserved.has(v.id));
  }
  const tasks=[];
  const map=id=>tasks.push({kind:'map',id});
  const model=id=>tasks.push({kind:'hero-model',id});
  const npc=(from,to)=>{for(let id=from;id<=to;id++)tasks.push({kind:'npc',id});};
  model(1);npc(1,3);map(2);model(2);model(3);npc(4,6);map(3);model(4);model(5);npc(7,12);
  map(4);model(6);model(7);model(8);npc(13,24);map(5);model(9);model(10);npc(25,30);
  function investments() {
    while(taskIndex<tasks.length) {
      guard();const task=tasks[taskIndex];
      if(taskIndex===0&&e.heroCompletedOrders<10)return;
      if(taskIndex===1&&e.heroCompletedOrders<15)return;
      const reserve=milestones.threeEquipped?300:0;
      let cost;
      if(task.kind==='hero-model') cost=slotVehiclePurchaseQuote(task.id).costCents;
      else if(task.kind==='map') cost=slotMapPurchaseQuote(task.id).costCents;
      else cost=slotRiderHireQuote('npc-'+task.id).costCents+(freeCar()?0:slotVehiclePurchaseQuote(1).costCents);
      if(e.cashCents<cost+reserve)return;
      const beforeTask=taskIndex;
      if(task.kind==='hero-model') heroCar(task.id);
      else if(task.kind==='map') {investment({type:'buyMap',mapId:task.id});cmd({type:'selectMap',mapId:task.id});}
      else {
        let car=freeCar();if(!car){const id=investment({type:'buyVehicle',modelId:1});car=e.vehicles.find(v=>v.id===id);}
        investment({type:'hireRider',riderId:'npc-'+task.id});cmd({type:'assignVehicle',riderId:'npc-'+task.id,vehicleId:car.id});
        if(task.id===1) {
          assert.equal(e.heroCompletedOrders,15);assert.equal(heroIncome,32000);assert.equal(spent.supply_purchase,0);
          assert.equal(spent.vehicle_purchase,30000);assert.equal(spent.rider_hire,12000);assert.equal(e.cashCents,0);
        }
      }
      taskIndex++;snapshot('purchase-step-'+beforeTask);
      if(milestones.assetFull)return;
    }
  }
  function supplyIfNeeded(force=false) {
    const t=g.tripState;if((!force&&t.stamina>=30)||t.action)return false;
    if(g.route.progress.phase==='service'&&g.route.progress.serviceCharged)return false;
    wait(OP.supply,'supply menu');guard();const kind=e.cashCents>=300?'noodles':'rest';
    g.supply(kind);collectLedger();emit('public-supply',{kind,source:'purchase',staminaBefore:t.stamina});
    advance(g.tripState.action.durationSeconds,'supply action','supply');return true;
  }
  assert.equal(e.cashCents,10000);assert.equal(g.nextBatchEffects.capacitySlots,2);assert.equal(e.hireCount,0);
  json(path.join(runDir,'scenario.json'),{operationProfile:OP,limits:LIMITS,tasks,
    inputCitySHA256:hashFile(path.join(ROOT,'delivery-game/assets/resources/map-sample/city.json')),
    supply:{method:'exact read-only prepareCity(city.json), reused for every selected mapId',nodes:city.nodes.length,roads:city.roads.length,
      pois:city.pois.length,operatingPOIs:city.operatingPOIs?.length??city.pois.length,dispatchBounds:city.dispatchBounds??null},
    endpoints:{asset80:{NPCs:24,maps:[1,2,3,4],models:[1,2,3,4,5,6,7,8],catalogNumerator:36,catalogDenominator:45,equippedActors:25},
      assetFull:{NPCs:30,maps:[1,2,3,4,5],models:[1,2,3,4,5,6,7,8,9,10],catalogNumerator:45,catalogDenominator:45,equippedActors:31},
      excludes:'All purchased rider training and vehicle upgrades, including level 30; not all gameplay content.'}});
  emit('fresh-game',{cashCents:e.cashCents,capacitySlots:2});
  try {
    snapshot('start');
    while(true) {
      guard();if(++iterations>LIMITS.iterations)throw new BoundedStop('iteration-limit');
      if(milestones.assetFull){stop={kind:'full-asset-set-reached'};break;}
      const start=now,phase=g.route.progress.phase,t=g.tripState;
      assert(g.dispatch.hasEquippedVehicle,'hero always retains an equipped vehicle between timed operations');
      if(['idle','finished'].includes(phase)) {
        if(phase==='finished')wait(OP.receipt,'receipt reading');
        investments();if(milestones.assetFull){stop={kind:'full-asset-set-reached'};break;}
        supplyIfNeeded();wait(OP.lobby,'lobby reading');
        const offers=g.normalCandidates(),capacity=g.nextBatchEffects.capacitySlots;
        let left=capacity,selected=[],countLimit=e.heroCompletedOrders<10?10-e.heroCompletedOrders:e.heroCompletedOrders<15?15-e.heroCompletedOrders:Infinity;
        for(const offer of offers)if(offer.load.occupiedSlots<=left&&selected.length<countLimit){selected.push(offer);left-=offer.load.occupiedSlots;}
        emit('candidate-pool',{offers:offers.length,requested:slotCandidateRequestCount(capacity),capacitySlots:capacity,
          slot1:offers.filter(o=>o.load.occupiedSlots===1).length,slot2:offers.filter(o=>o.load.occupiedSlots===2).length,selectedOrders:selected.length});
        if(!selected.length)throw new BoundedStop('no-canonical-offers');
        wait(OP.select*selected.length,'selection');guard();const rejections=[];let accepted;
        while(selected.length) {try{accepted=g.acceptBatch(selected);break;}catch(error){rejections.push({orders:selected.length,message:error.message});selected.pop();}}
        if(!selected.length)throw new BoundedStop('all-selected-rejected',{rejections});
        for(const q of accepted)quotes.set(q.id,q);
        const choice=g.routeChoices()[0];assert(choice,'real permitted route exists');
        const row={batch:++batchCount,acceptedAtSeconds:now,capacitySlots:capacity,filledSlots:selected.reduce((a,o)=>a+o.load.occupiedSlots,0),
          routeMetres:choice.metres,weather:choice.weather,staminaEstimate:choice.stamina,mapId:e.selectedMapId,
          orders:selected.map(o=>({id:o.id,food:o.food,quote:quotes.get(o.id)})),rejections};
        batches.push(row);emit('public-acceptBatch',{batch:row});signedSlots+=row.filledSlots;signedCapacity+=capacity;acceptedOrders+=selected.length;roadMetres+=choice.metres;
        wait(OP.route,'route reading');guard();g.beginTrip(choice.preference);emit('public-beginTrip',{batch:batchCount,preference:choice.preference,speed:g.deliveryEffects.speedRelativeToStarter});
      } else if(t.action) advance(t.action.durationSeconds-t.action.elapsedSeconds,'supply action','supply');
      else if(t.blocked&&!(phase==='service'&&g.route.progress.serviceCharged)) supplyIfNeeded(true);
      else if(phase==='pickup'){wait(OP.pickup,'pickup click');guard();g.pickup();emit('public-pickup');}
      else if(phase==='ready'){wait(OP.continue,'continue click');guard();g.continueTrip();emit('public-continueTrip');}
      else if(phase==='travelling') {
        const r=g.route.snapshot(),leg=r.legs[r.cursor];
        const seconds=Math.max(0,(leg.seconds-r.legSeconds)*(t.weather==='rain'?1.1:t.weather==='severe'?1.25:1)/(40*g.deliveryEffects.speedRelativeToStarter));
        advance(Math.max(.000001,seconds+.000001),'road travel','travel');
      } else if(phase==='service') {
        const r=g.route.snapshot(),duration=r.stops[r.cursor].kind==='pickup'?2:1;
        advance(Math.max(.000001,duration-r.serviceSeconds+.000001),'fixed service','service');
      } else throw new Error('Unhandled route phase '+phase);
      if(now===start&&g.route.progress.phase===phase)throw new Error('No progress in '+phase);
      const cpu=cpuSeconds();if(cpu-lastProgressCPU>=15) {
        lastProgressCPU=cpu;snapshot('cpu-progress');console.log(JSON.stringify({step:'progress',cpuSeconds:cpu,simulatedMinutes:now/60,
          hero:e.heroCompletedOrders,npc:e.npcCompletedOrders,hireCount:e.hireCount,equippedNPCs:e.riders.filter(r=>r.id!=='hero'&&r.vehicleId).length,
          maps:e.ownedMapIds,models:[...new Set(e.vehicles.map(v=>v.modelId))],cashCents:e.cashCents,nextTask:tasks[taskIndex],events:eventCount}));
      }
    }
  } catch(error) {
    if(error instanceof BoundedStop) stop={kind:error.kind,...error.detail};
    else {unexpected={message:error.message,stack:error.stack};stop={kind:'actual-domain-or-model-error',...unexpected};process.exitCode=2;}
  } finally {
    collectLedger();const final=snapshot('final');
    const serialized=g.serialize();fs.writeFileSync(path.join(runDir,'end-state.json'),serialized+'\n');
    let restoreValidation;
    try {V2GameSession.restore(city,serialized,{preserveClock:true});restoreValidation={ok:true};}
    catch(error) {restoreValidation={ok:false,message:error.message,stack:error.stack};process.exitCode=2;}
    json(path.join(runDir,'ledger.json'),e.ledger);
    json(path.join(runDir,'batches.json'),batches);
    // Allocate actual supply costs equally (integer cents) to the next signed
    // batch, using the first-round convention. Capex is never called operating cost.
    let previousEnd=-1,allocated=0;
    for(const batch of batches) {
      const ids=batch.orders.map(o=>o.id),delivered=receipts.filter(r=>r.actor==='hero'&&ids.includes(r.orderId));
      const end=delivered.length===ids.length?Math.max(...delivered.map(r=>r.ledgerAtMs)):Math.floor(now*1000);
      const cost=supplies.filter(s=>s.atMs>previousEnd&&s.atMs<=end).reduce((n,s)=>n+s.cents,0);
      for(const r of delivered) {const i=ids.indexOf(r.orderId),share=Math.floor(cost/ids.length)+(i<cost%ids.length?1:0);
        r.batch=batch.batch;r.supplyAllocatedCents=share;r.operatingNetCents=r.receivedCents-share;allocated+=share;}
      previousEnd=end;
    }
    json(path.join(runDir,'receipts.json'),receipts);
    const result={kind:'bounded-production-domain-long-term-single-path',stop,unexpected,limits:LIMITS,operationProfile:OP,
      final,milestones,assetTimeRatio:milestones.asset80&&milestones.assetFull?milestones.asset80.atSeconds/milestones.assetFull.atSeconds:null,
      ratioWithheldReason:milestones.asset80&&milestones.assetFull?null:'Both exact endpoints were not reached on this same legal path; no extrapolation.',
      reachedTaskCount:taskIndex,totalTaskCount:tasks.length,stages,restoreValidation,
      cashConservation:{initialCents:10000,heroIncomeCents:heroIncome,npcIncomeCents:npcIncome,spentCents:spent,finalCashCents:e.cashCents,
        residualCents:e.cashCents-(10000+heroIncome+npcIncome-Object.values(spent).reduce((a,b)=>a+b,0))},
      quotaConservation:{addedMs:quotaAdded,consumedMs:quotaConsumed,clippedMs:quotaClipped,finalMs:g.dispatch.fleetState.quotaMs,
        residualMs:quotaAdded-quotaConsumed-quotaClipped-g.dispatch.fleetState.quotaMs},
      supplyAllocation:{method:'equal integer-cent shares of actual supply since previous batch end, allocated to following signed batch',allocatedCents:allocated,
        unallocatedCents:spent.supply_purchase-allocated},eventCount,iterations,workerCPUSeconds:cpuSeconds(),workerWallSeconds:(performance.now()-startWall)/1000};
    json(path.join(runDir,'result.json'),result);emit('worker-finished',{stop,workerCPUSeconds:result.workerCPUSeconds,restoreValidation,assetTimeRatio:result.assetTimeRatio});
    fs.closeSync(eventFile);fs.closeSync(commandFile);
    console.log(JSON.stringify({step:'worker-finished',stop,hero:final.heroOrders,npc:final.npcOrders,equippedNPCs:final.equippedNPCs,
      simulatedMinutes:now/60,workerCPUSeconds:result.workerCPUSeconds,restoreValidation,assetTimeRatio:result.assetTimeRatio}));
  }
}

if(process.argv[2]==='--worker') worker(process.argv[3],process.argv[4]);
else supervisor().catch(error=>{console.error(error.stack);process.exitCode=1;});
