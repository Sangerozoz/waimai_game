/* Isolated balance experiment. All wallet/assets arise through production commands.
 * Run: node docs/balance/2026-11-06-balance-round-01/a/run-model.cjs [--representative-only] [--candidates]
 * No browser, storage adapter, rewards, Cocos build, or production-file writes.
 */
'use strict';
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const ROOT=path.resolve(__dirname,'../../../..'),SCRIPTS=path.join(ROOT,'delivery-game/assets/scripts');
const ts=require('/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/app.asar.unpacked/node_modules/typescript');
const sha=bytes=>crypto.createHash('sha256').update(bytes).digest('hex');
const write=(name,value)=>fs.writeFileSync(path.join(__dirname,name),typeof value==='string'?value:JSON.stringify(value,null,2)+'\n');
const scratch=fs.mkdtempSync(path.join(os.tmpdir(),'balance-a-1107-'));
const command=process.argv.map(x=>JSON.stringify(x)).join(' '),startedAt=new Date().toISOString();
const modelSHA256=sha(fs.readFileSync(__filename));
const allEvents=[],runLog=[],sourceHashes={};
const log=value=>{runLog.push(value);console.log(JSON.stringify(value));};
function saveEvents(){const columns=['runId','atSeconds','type','orderId','actor','incomeCents','quotedCents','occupiedSlots','capacitySlots','deliveryMetres','ledgerAtMs','category','costCents','detail'];const csv=value=>'"'+String(value??'').replaceAll('"','""')+'"';write('events.csv',columns.join(',')+'\n'+allEvents.map(row=>columns.map(key=>csv(key==='detail'?JSON.stringify(row):row[key])).join(',')).join('\n')+'\n');}
const PROFILES={regular:{lobby:4,select:.6,route:2,pickup:1,continue:1,receipt:2,investment:3,supply:2},slow:{lobby:12,select:2,route:6,pickup:4,continue:4,receipt:6,investment:9,supply:6}};
const POLICIES=['squad-first','starter-upgrades-first','capacity-car-first','npc-first-only-car'];
function representativeCity(){
 const nodes=Array.from({length:8},(_,i)=>({id:'r'+i,x:i*100,y:0}));
 return {title:'representative 100m-spaced corridor, not production geography',width:700,height:100,nodes,
  roads:[{id:'corridor',nodes:nodes.map(n=>n.id),direction:0,kind:'primary',width:6,speed:1,roughness:0,bridge:false}],
  pois:nodes.map((n,i)=>({node:n.id,name:'Representative '+i,kind:i%2?'home':'restaurant'})),buildings:[],areas:[],waterways:[],labels:[]};
}
try{
 const entries=['map-sample/V2GameSession.ts','map-sample/PlaceCatalog.ts','domain/V2ProgressTargets.ts'];
 const options={target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS,strict:true,noEmitOnError:true,rootDir:SCRIPTS,outDir:scratch,skipLibCheck:true,types:[]};
 const program=ts.createProgram(entries.map(x=>path.join(SCRIPTS,x)),options),emitted=program.emit(),diagnostics=ts.getPreEmitDiagnostics(program).concat(emitted.diagnostics);
 for(const source of program.getSourceFiles())if(source.fileName.startsWith(SCRIPTS+path.sep))sourceHashes[path.relative(ROOT,source.fileName)]=sha(fs.readFileSync(source.fileName));
 for(const rel of ['delivery-game/assets/resources/map-sample/city.json','docs/balance/2026-11-06-capacity-slots-economy/parameters.json'])sourceHashes[rel]=sha(fs.readFileSync(path.join(ROOT,rel)));
 const identity={startedAt,command,modelSHA256,compilerVersion:ts.version,compilerOptions:{...options,rootDir:SCRIPTS},scratch,sourceHashes};
 write('run-identity.json',identity);
 if(diagnostics.length)throw new Error(ts.formatDiagnosticsWithColorAndContext(diagnostics,{getCanonicalFileName:f=>f,getCurrentDirectory:()=>ROOT,getNewLine:()=> '\n'}));
 log({step:'strict-domain-compile',exit:0,sourceCount:Object.keys(sourceHashes).length,scratch});
 const {V2GameSession}=require(path.join(scratch,'map-sample/V2GameSession.js'));
 const {V2RouteSession}=require(path.join(scratch,'map-sample/V2RouteSession.js'));
 const {V2EconomySession}=require(path.join(scratch,'domain/V2EconomySession.js'));
 const economyModule=require(path.join(scratch,'domain/V2EconomySession.js'));
 const productionPriceRule=economyModule.V2_ORDINARY_PRICING;
 const {slotVehicleEffects,slotVehicleUpgradeQuote,slotRiderUpgradeQuote}=require(path.join(scratch,'domain/V2EconomyProfiles.js'));
 const {slotCandidateRequestCount}=require(path.join(scratch,'domain/V2LoadRules.js'));
 const {V2_SLOT_CONFIG:CONFIG}=require(path.join(scratch,'domain/V2SlotEconomyConfig.js'));
 const {prepareCity}=require(path.join(scratch,'map-sample/PlaceCatalog.js'));
 const {V2FleetSession}=require(path.join(scratch,'domain/V2FleetSession.js'));
 // Both modules are actually used by Game; exported here only for audit identity.
 assert.equal(typeof V2EconomySession,'function');assert.equal(typeof V2FleetSession,'function');
 const actualRaw=JSON.parse(fs.readFileSync(path.join(ROOT,'delivery-game/assets/resources/map-sample/city.json'),'utf8'));
 const actual=process.argv.includes('--representative-only')?null:prepareCity(actualRaw);
 const cities=[{id:'representative-100m',data:representativeCity(),assumption:'8 POIs on a bidirectional 700m corridor, 100m spacing, road speed 1 metre/game-second; sensitivity fixture only.'}];
 if(actual)cities.push({id:'current-game-supply',data:actual,assumption:'Exact read-only prepareCity(city.json) path used by V2GameBootstrap. No geometry/POI/boundary edits.'});
 const sourceAtEnd=()=>Object.entries(sourceHashes).map(([file,before])=>({file,before,after:sha(fs.readFileSync(path.join(ROOT,file)))})).filter(x=>x.before!==x.after);
 const result={kind:'current-production-domain-balance-first-round',startedAt,command,modelSHA256,compilerExit:0,profileId:CONFIG.profileId,sourceHashes,operationProfiles:PROFILES,
  limitations:['Deterministic isolated domain simulation, not actual player timing, browser, GPU, or population statistics.',
   'No ads or SDK outcomes. No balance/asset injection, fake gifts, rich fixture, map unlocking, or save writing.',
   'Manual waits occur only at stopped/menu states. Game tick remains production behavior; slower input never changes road speed.',
   'First-fit selection from the finite canonical candidate pool; pop the last offer only on a real safe-route/stamina rejection.',
   'No map purchases in this 20/60 minute strategy experiment. The 80/20 long progression target is unverified.',
   'NPC timing is the actual Fleet design clock, not map-routed NPC movement. Hero uses actual Route travel, food risks, weather, stamina and settlements.'],
  scenarios:cities.map(c=>({id:c.id,assumption:c.assumption,nodes:c.data.nodes.length,roads:c.data.roads.length,pois:c.data.pois.length,operatingPOIs:c.data.operatingPOIs?.length??c.data.pois.length,dispatchBounds:c.data.dispatchBounds??null})),runs:[],candidateRuns:[]};

 function simulate(city,policy,profileName,curve='production',horizon=3600,options={}){
  const g=new V2GameSession(city.data,0),op=PROFILES[profileName];let now=0,sequence=0,lastLedger=0,batch=0,stop=null,lastSupply=null;
  let spent={vehicle_purchase:0,rider_hire:0,vehicle_upgrade:0,rider_upgrade:0,map_purchase:0,supply_purchase:0};
  let quoteTotal=0,earnedHero=0,earnedNPC=0,deliveredSlots=0,signedSlots=0,signedCapacity=0,acceptedOrders=0,roadMetres=0,travelSeconds=0,manualSeconds=0,supplySeconds=0;
  let quotaAddedMs=0,quotaClippedMs=0,quotaConsumedMs=0,quotaNoWorkSeconds=0,quotaStalledSeconds=0,quotaPeakMs=0;
  let firstCar=null,firstNPC=null,threeEquipped=null,firstQuotaEmpty=null;
  const checkpoints=[],batches=[],quotes=new Map(),receiptRows=[],recoveries=[],supplyCharges=[];
  const runId=[curve,city.id,policy,profileName,options.suffix||'main'].join('/');
  const state=()=>g.dispatch.economyState;
  const event=(type,data={})=>allEvents.push({runId,atSeconds:+now.toFixed(6),type,...data});
  const initial=state();assert.equal(initial.cashCents,10000);assert.equal(g.nextBatchEffects.capacitySlots,2);assert.equal(initial.heroCompletedOrders,0);assert.equal(initial.hireCount,0);
  event('fresh-game',{cashCents:initial.cashCents,capacitySlots:2});
  function reconcile(){const e=state(),entries=e.ledger.entries;for(const row of entries.slice(lastLedger)){
    if(row.category==='hero_ordinary'||row.category==='hero_special'){
     earnedHero+=row.amountCents;const id=row.detail.orderId,order=g.dispatch.snapshot().orders.find(o=>o.id===id),q=quotes.get(id)||order?.quote;
     if(q){quoteTotal+=q.incomeCents;deliveredSlots+=q.terms.load.occupiedSlots;}
     const out={orderId:id,actor:'hero',incomeCents:row.amountCents,quotedCents:q?.incomeCents??null,occupiedSlots:q?.terms.load.occupiedSlots??null,capacitySlots:q?.terms.capacity.capacitySlots??null,deliveryMetres:q?.ordinaryPricing?.deliveryMetres??null,damage:order?.receipt?.damage??null,lateGameSeconds:order?.receipt?.lateGameSeconds??null,ledgerAtMs:row.atMs,vehicleId:q?.vehicleId};
     receiptRows.push({...out,atSeconds:(row.atMs??now*1000)/1000});event('delivery',out);
    }else if(row.category==='npc_delivery'){
     earnedNPC+=row.amountCents;const out={orderId:row.detail.orderId,actor:row.detail.riderId,incomeCents:row.amountCents,quotedCents:row.amountCents,vehicleId:row.detail.vehicleId,ledgerAtMs:row.atMs};receiptRows.push({...out,atSeconds:(row.atMs??now*1000)/1000});event('delivery',out);
    }else if(row.category in spent){spent[row.category]-=row.amountCents;if(row.category==='supply_purchase')supplyCharges.push({atSeconds:(row.atMs??now*1000)/1000,cents:-row.amountCents});event('spending',{category:row.category,costCents:-row.amountCents,...row.detail,ledgerAtMs:row.atMs});}
   }lastLedger=entries.length;
   assert.equal(e.cashCents,10000+earnedHero+earnedNPC-Object.values(spent).reduce((a,b)=>a+b,0),'earned cash conservation');
   if(!firstCar&&e.vehicles.some(v=>typeof v.modelId==='number'))firstCar={seconds:now,heroOrders:e.heroCompletedOrders,cashCents:e.cashCents};
   if(!firstNPC&&e.hireCount)firstNPC={seconds:now,heroOrders:e.heroCompletedOrders,cashCents:e.cashCents};
   if(!threeEquipped&&e.riders.filter(r=>r.id!=='hero'&&r.vehicleId).length>=3)threeEquipped={seconds:now,heroOrders:e.heroCompletedOrders,cashCents:e.cashCents};
  }
  function summary(at){const e=state(),f=g.dispatch.fleetState,total=earnedHero+earnedNPC;
   const settled=receiptRows.filter(r=>r.actor==='hero'),npc=receiptRows.filter(r=>r.actor!=='hero');
   return {atMinutes:at/60,cashCoins:e.cashCents/100,heroOrders:e.heroCompletedOrders,npcOrders:e.npcCompletedOrders,heroOrdersPerMinute:e.heroCompletedOrders/(at/60),allOrdersPerMinute:(e.heroCompletedOrders+e.npcCompletedOrders)/(at/60),heroQuotedGrossCoins:quoteTotal/100,heroReceivedCoins:earnedHero/100,npcReceivedCoins:earnedNPC/100,totalReceivedCoins:total/100,operatingNetCoins:(total-spent.supply_purchase)/100,operatingNetCoinsPerMinute:(total-spent.supply_purchase)/100/(at/60),cashChangeCoins:(e.cashCents-10000)/100,heroMeanReceivedCoins:settled.length?earnedHero/100/settled.length:0,npcMeanReceivedCoins:npc.length?earnedNPC/100/npc.length:0,npcIncomeShare:total?earnedNPC/total:0,
    spentCoins:Object.fromEntries(Object.entries(spent).map(([k,v])=>[k,v/100])),fleetCount:e.hireCount,equippedNPCs:e.riders.filter(r=>r.id!=='hero'&&r.vehicleId).length,vehicles:e.vehicles.map(v=>({...v,effects:slotVehicleEffects(v)})),riders:e.riders,stamina:g.tripState.stamina,quotaMs:f.quotaMs,quotaCapacityMs:e.heroCompletedOrders+e.npcCompletedOrders>=700?1800000:e.heroCompletedOrders+e.npcCompletedOrders>=240?1500000:e.heroCompletedOrders+e.npcCompletedOrders>=60?1200000:900000,quotaAddedMs,quotaClippedMs,quotaConsumedMs,quotaUtilizationOfAdded:quotaAddedMs?quotaConsumedMs/quotaAddedMs:0,quotaNoWorkSeconds,quotaStalledSeconds,quotaPeakMs,firstQuotaEmpty,heroCapacityFillRatio:signedCapacity?signedSlots/signedCapacity:0,meanOrdersPerBatch:batches.length?acceptedOrders/batches.length:0,acceptedOrders,batchCount:batches.length,roadMetres,travelSeconds,manualSeconds,supplySeconds,firstCar,firstNPC,threeEquipped,phase:g.route.progress.phase,softLock:stop?.kind==='only-car-quota-deadlock',stop};
  }
  function tickTo(end){const before=g.dispatch.fleetState,priorEconomy=state(),oldEvents=priorEconomy.heroCompletionEvents.length;g.tick(++sequence,end,true,false);now=end;reconcile();
   const after=g.dispatch.fleetState,events=state().heroCompletionEvents.slice(oldEvents);let refill=0;
   for(const row of events)refill+=row.teamCompletedAfter>=700?180000:row.teamCompletedAfter>=240?120000:row.teamCompletedAfter>=60?120000:60000;
   // Reconstruct quota exactly at each real hero settlement time. A worker with
   // an equipped car or an outstanding signed batch consumes the shared clock.
   const configuredWorker=priorEconomy.riders.some(r=>r.id!=='hero'&&r.vehicleId);
   const startedWithWorker=before.batches.length>0||configuredWorker;
   let workRemaining=configuredWorker?Infinity:Math.max(0,...before.batches.map(b=>b.orders[b.orders.length-1].dueMs-b.elapsedMs));
   let q=before.quotaMs,cursor=before.lastAdvancedAt,consumed=0,clipped=0,stalled=0;
   const spendUntil=at=>{assert(at>=cursor);const elapsed=at-cursor;if(workRemaining>0){const work=Math.min(q,elapsed,workRemaining);consumed+=work;q-=work;workRemaining-=work;if(workRemaining===0)quotaNoWorkSeconds+=(elapsed-work)/1000;else stalled+=elapsed-work;}else quotaNoWorkSeconds+=elapsed/1000;cursor=at;};
   for(const row of events){const receipt=receiptRows.find(r=>r.orderId===row.id);assert(receipt&&Number.isSafeInteger(receipt.ledgerAtMs),'hero settlement has precise event time');spendUntil(receipt.ledgerAtMs);
    const n=row.teamCompletedAfter,capacity=n>=700?1800000:n>=240?1500000:n>=60?1200000:900000,credit=n>=700?180000:n>=60?120000:60000;
    clipped+=Math.max(0,q+credit-capacity);q=Math.min(capacity,q+credit);quotaPeakMs=Math.max(quotaPeakMs,q);
   }
   spendUntil(Math.floor(end*1000));if(q!==after.quotaMs)write('quota-assertion-context.json',{runId,now,end,before,after,priorRiders:priorEconomy.riders,events,predictedQuotaMs:q,refill,consumed,clipped});assert.equal(q,after.quotaMs,'exact shared-quota reconstruction');
   quotaAddedMs+=refill;quotaClippedMs+=clipped;quotaConsumedMs+=consumed;quotaStalledSeconds+=stalled/1000;quotaPeakMs=Math.max(quotaPeakMs,after.quotaMs);
   if(startedWithWorker&&before.quotaMs>0&&after.quotaMs===0&&!firstQuotaEmpty)firstQuotaEmpty={seconds:now,cashCents:state().cashCents,batches:after.batches.length};
  }
  function summaryCapacity(){const e=state(),n=e.heroCompletedOrders+e.npcCompletedOrders;return n>=700?1800000:n>=240?1500000:n>=60?1200000:900000;}
  function advance(seconds,label){let target=Math.min(horizon,now+Math.max(0,seconds));
   while(checkpoints.length<2){const boundary=checkpoints.length===0?1200:3600;if(boundary>target||boundary>horizon)break;if(now<boundary)tickTo(boundary);checkpoints.push(summary(boundary));if(now>=target)return;}
   if(now<target)tickTo(target);
  }
  function wait(seconds,label){manualSeconds+=Math.min(seconds,horizon-now);advance(seconds,label);}
  function cmd(c){if(now>=horizon)return null;const out=g.dispatch.withLedgerTime(now,()=>g.dispatch.command(c));reconcile();event('command',{command:c,result:out,cashCents:state().cashCents});return out;}
  function invest(c){wait(op.investment,'investment menu');if(now>=horizon)return null;return cmd(c);}
  function assign(riderId,vehicleId){return cmd({type:'assignVehicle',riderId,vehicleId});}
  function carForHero(modelId){const id=invest({type:'buyVehicle',modelId});if(!id)return false;assign('hero',null);assign('hero',id);return true;}
  function fundTeam(){let e=state();if(!e.hireCount){if(e.cashCents<12000)return false;invest({type:'hireRider',riderId:'npc-1'});if(now>=horizon)return false;const free=state().vehicles.find(v=>!state().riders.some(r=>r.vehicleId===v.id));if(free)assign('npc-1',free.id);return true;}
   for(const r of ['npc-2','npc-3']){e=state();if(e.riders.some(x=>x.id===r))continue;const cost=CONFIG.riders.find(x=>x.id===r).price*100+30000;if(e.cashCents<cost)return false;
    const id=invest({type:'buyVehicle',modelId:1});if(!id)return false;invest({type:'hireRider',riderId:r});if(now>=horizon)return false;assign(r,id);reconcile();return true;}
   return false;
  }
  function investments(){let e=state();
   if(options.noInvestment)return;
   if(policy==='npc-first-only-car'){
    const target=options.loanAfterHeroOrders??1;
    if(e.hireCount===0&&e.heroCompletedOrders>=target&&e.cashCents>=12000){invest({type:'hireRider',riderId:'npc-1'});if(now>=horizon)return;const old=state().riders[0].vehicleId;assign('hero',null);assign('npc-1',old);}
    return;
   }
   if(policy==='starter-upgrades-first'){
    const old=e.vehicles.find(v=>v.modelId==='starter');
    if(old.level<10){while(now<horizon&&state().vehicles.find(v=>v.id===old.id).level<10){const v=state().vehicles.find(v=>v.id===old.id),q=g.dispatch.vehicleUpgradePrice(v.id);if(state().cashCents<q.costCents)break;invest({type:'upgradeVehicle',vehicleId:v.id});}return;}
   }
   e=state();const paid=e.vehicles.some(v=>typeof v.modelId==='number');
   if(!paid){const model=policy==='capacity-car-first'?3:1,cost=CONFIG.vehicles[model-1].price*100;
    if((policy!=='squad-first'||e.heroCompletedOrders>=10)&&e.cashCents>=cost)carForHero(model);return;}
   if(policy==='squad-first'&&e.heroCompletedOrders<15)return;
   for(let guard=0;guard<3&&now<horizon;guard++)if(!fundTeam())break;
  }
  function supplyIfNeeded(force=false){const t=g.tripState;if(!force&&t.stamina>=30)return false;if(t.action)return false;
   if(g.route.progress.phase==='service'&&g.route.progress.serviceCharged)return false;
   wait(op.supply,'supply menu');if(now>=horizon)return false;
   const kind=state().cashCents>=300?'noodles':'rest';g.supply(kind);reconcile();event('supply-action',{kind,stamina:t.stamina,active:!!g.dispatch.snapshot().batchIds.length});
   const duration=g.tripState.action.durationSeconds;supplySeconds+=Math.min(duration,horizon-now);advance(duration,'supply action');lastSupply=now;return true;
  }
  function noCar(){const f=g.dispatch.fleetState;
   if(!f.batches.length&&f.quotaMs>0){advance(.001,'start NPC batches');return;}
   if(f.quotaMs>0){advance(f.quotaMs/1000+.001,'exhaust NPC quota');return;}
   const errors={};
   try{cmd({type:'assignVehicle',riderId:'npc-1',vehicleId:null});}catch(e){errors.detachNPC=String(e.message);}
   const car=state().vehicles[0];try{cmd({type:'assignVehicle',riderId:'hero',vehicleId:car.id});}catch(e){errors.returnToHero=String(e.message);}
   if(g.dispatch.hasEquippedVehicle){stop={kind:'recoverable-car-return',seconds:now,errors};recoveries.push(stop);event('loan-recovery',stop);stop=null;return;}
   if(state().cashCents>=30000){const id=cmd({type:'buyVehicle',modelId:1});assign('hero',id);recoveries.push({kind:'earned-replacement',seconds:now});return;}
   try{cmd({type:'buyVehicle',modelId:1});}catch(e){errors.buyReplacement=String(e.message);}
   stop={kind:'only-car-quota-deadlock',seconds:now,cashCents:state().cashCents,quotaMs:f.quotaMs,unpaidOrders:state().fleetQuotes.length,reservedVehicleIds:[...new Set(state().fleetQuotes.map(q=>q.vehicleId))],errors};event('softlock',stop);advance(horizon-now,'stalled');
  }
  // Every operation below is a public production method. No private state replacement.
  for(let guard=0;now<horizon&&guard<20000;guard++){
   const start=now,phase=g.route.progress.phase,t=g.tripState;
   if(!g.dispatch.hasEquippedVehicle){noCar();if(stop)break;continue;}
   if(['idle','finished'].includes(phase)){
    if(phase==='finished')wait(op.receipt,'receipt reading');if(now>=horizon)break;
    investments();if(now>=horizon)break;if(!g.dispatch.hasEquippedVehicle)continue;
    if(supplyIfNeeded()){if(now>=horizon)break;}
    wait(op.lobby,'lobby reading');if(now>=horizon)break;
    const offers=g.normalCandidates(),capacity=g.nextBatchEffects.capacitySlots;let left=capacity,selected=[];
    let countLimit=Infinity;if(policy==='squad-first'&&!options.noInvestment){const count=state().heroCompletedOrders;countLimit=count<10?10-count:count<15?15-count:Infinity;}
    if(policy==='npc-first-only-car'&&state().hireCount===0)countLimit=Math.max(1,(options.loanAfterHeroOrders??1)-state().heroCompletedOrders);
    const usable=options.distanceTarget&&state().heroCompletedOrders>=15?offers.filter(offer=>Math.round(g.route.fastest(offer.pickupNode,offer.dropoffNode).heldMetres)===options.distanceTarget):offers;
    for(const offer of usable)if(offer.load.occupiedSlots<=left&&selected.length<countLimit){selected.push(offer);left-=offer.load.occupiedSlots;}
    event('candidate-pool',{offers:offers.length,requested:slotCandidateRequestCount(capacity),capacitySlots:capacity,slot1:offers.filter(o=>o.load.occupiedSlots===1).length,slot2:offers.filter(o=>o.load.occupiedSlots===2).length,selectedOrders:selected.length});
    if(!selected.length){stop={kind:'no-canonical-offers',seconds:now};event('supply-empty',stop);advance(horizon-now,'no supply');break;}
    wait(op.select*selected.length,'selection');if(now>=horizon)break;
    const reasons=[];let q;
    while(selected.length){try{q=g.acceptBatch(selected);break;}catch(error){reasons.push({orders:selected.length,message:error.message});selected.pop();}}
    if(!selected.length){stop={kind:'all-selected-rejected',seconds:now,reasons};event('selection-blocked',stop);advance(horizon-now,'unserviceable supply');break;}
    batch++;for(const row of q)quotes.set(row.id,row);
    const choice=g.routeChoices()[0];assert(choice,'legal route choice');
    signedSlots+=selected.reduce((a,b)=>a+b.load.occupiedSlots,0);signedCapacity+=capacity;acceptedOrders+=selected.length;roadMetres+=choice.metres;
    const row={batch,acceptedAt:now,orders:selected.map(o=>({id:o.id,slots:o.load.occupiedSlots,deliveryMetres:quotes.get(o.id).ordinaryPricing.deliveryMetres})),capacitySlots:capacity,plannedFilledSlots:capacity-left,actualFilledSlots:selected.reduce((a,b)=>a+b.load.occupiedSlots,0),routeMetres:choice.metres,etaSeconds:choice.seconds,weather:choice.weather,staminaEstimate:choice.stamina,rejections:reasons};
    batches.push(row);event('batch-accepted',row);wait(op.route,'route reading');if(now>=horizon)break;g.beginTrip(choice.preference);event('depart',{batch,preference:choice.preference,speed:g.deliveryEffects.speedRelativeToStarter});
   }else if(t.action){const duration=t.action.durationSeconds-t.action.elapsedSeconds;supplySeconds+=Math.min(duration,horizon-now);advance(duration,'supply');}
   else if(t.blocked&&!(phase==='service'&&g.route.progress.serviceCharged)){supplyIfNeeded(true);}
   else if(phase==='pickup'){wait(op.pickup,'pickup click');if(now<horizon)g.pickup();}
   else if(phase==='ready'){wait(op.continue,'continue click');if(now<horizon)g.continueTrip();}
   else if(phase==='travelling'){
    const r=g.route.snapshot(),leg=r.legs[r.cursor],seconds=Math.max(0,(leg.seconds-r.legSeconds)* (g.tripState.weather==='rain'?1.1:g.tripState.weather==='severe'?1.25:1)/(40*g.deliveryEffects.speedRelativeToStarter));
    // 1us permits the production route transition at exact edge/service boundaries.
    travelSeconds+=Math.min(seconds,horizon-now);advance(Math.max(.000001,seconds+.000001),'road travel');
   }else if(phase==='service'){const r=g.route.snapshot(),duration=r.stops[r.cursor].kind==='pickup'?2:1;advance(Math.max(.000001,duration-r.serviceSeconds+.000001),'fixed service');}
   else throw new Error('Unhandled route phase '+phase);
   if(now===start&&lastSupply!==now&&g.route.progress.phase===phase)throw new Error('No progress '+runId+' '+phase);
  }
  if(now<horizon)throw new Error('Model loop exceeded bound '+runId);
  reconcile();if(horizon===3600&&checkpoints.length<2)checkpoints.push(summary(horizon));
  // Validate a naturally earned end-state through the same public restore gate.
  V2GameSession.restore(city.data,g.serialize(),{preserveClock:true});
  const end=summary(horizon),heroReceipts=receiptRows.filter(r=>r.actor==='hero');
  // Per-order operating net is received income less an explicit pro-rata share
  // of real supply purchases since the previous batch ended. Capex stays separate.
  let previousEnd=-1,allocatedCents=0;
  for(const signed of batches){const ids=signed.orders.map(o=>o.id),delivered=heroReceipts.filter(r=>ids.includes(r.orderId));
   const finished=delivered.length===ids.length,ended=finished?Math.max(...delivered.map(r=>r.atSeconds)):horizon;
   const supplyCents=supplyCharges.filter(r=>r.atSeconds>previousEnd&&r.atSeconds<=ended).reduce((n,r)=>n+r.cents,0);
   signed.supplyCostCents=supplyCents;signed.completed=finished;signed.endedAt=ended;
   for(const row of delivered){const index=ids.indexOf(row.orderId),share=Math.floor(supplyCents/ids.length)+(index<supplyCents%ids.length?1:0);row.allocatedSupplyCents=share;row.operatingNetCents=row.incomeCents-share;row.acceptedAtSeconds=signed.acceptedAt;row.acceptanceToCompletionSeconds=row.atSeconds-signed.acceptedAt;row.batch=signed.batch;allocatedCents+=share;}
   previousEnd=ended;
  }
  const out={id:runId,scenario:city.id,policy,operationProfile:profileName,curve,horizonMinutes:horizon/60,checkpoints,final:end,batches,receipts:receiptRows,recoveries,
   first15Budget:{car:firstCar,npc:firstNPC,first15IncomeCoins:heroReceipts.slice(0,15).reduce((a,b)=>a+b.incomeCents,0)/100,first15QuotesCoins:heroReceipts.slice(0,15).reduce((a,b)=>a+b.quotedCents,0)/100},
   supplyAllocation:{method:'equal integer-cent shares across signed batch orders; supplies since previous batch end charged to following batch',allocatedCents,unallocatedCents:spent.supply_purchase-allocatedCents},
   eventCount:allEvents.filter(e=>e.runId===runId).length,restoreValidated:true};
  for(const row of receiptRows)event('order-economics',row);
  log({step:'scenario-finished',id:runId,hero:end.heroOrders,npc:end.npcOrders,at20:checkpoints[0]?.cashCoins,firstCar,firstNPC,threeEquipped,stop});return out;
 }

 // Baseline always runs first, before any experimental tariff is installed.
 if(!process.argv.includes('--loan-10-only'))for(const city of cities)for(const profile of Object.keys(PROFILES))for(const policy of POLICIES){result.runs.push(simulate(city,policy,profile));write('baseline-results.json',result);}
 const loanCity=cities[0];result.loanSensitivity=[];
 for(const loanAfterHeroOrders of process.argv.includes('--loan-10-only')?[10]:[3,5,10,15])result.loanSensitivity.push(simulate(loanCity,'npc-first-only-car','regular','production',1200,{loanAfterHeroOrders,suffix:'loan-after-'+loanAfterHeroOrders}));
 // Unit-time sensitivity isolates distance using actual Game routes and earned balances.
 result.distanceSensitivity=[];
 for(const spacing of process.argv.includes('--loan-10-only')?[]:[100,354,500,2000,4000]){
  const data=representativeCity(),positions=[0,100,200,554,1054,3054,7054,7154];data.nodes.forEach((n,i)=>n.x=positions[i]);data.width=7154;
  // Complete a legal short-route prefix, then choose only the target held distance.
  // Approach distances remain real and are charged by the production route.
  result.distanceSensitivity.push(simulate({id:'held-distance-'+spacing,data},'squad-first','regular','production',1200,{noInvestment:true,distanceTarget:spacing,suffix:'distance'}));
 }
 // These are isolated, unapproved replacements of one scratch-module export only.
 // Production files and every asset purchase/upgrade fee remain byte-identical.
 if(process.argv.includes('--candidates')){
  const candidates=[{id:'C-base10000-slope0.5',baseBasisPoints:10000,basisPointsPerDeliveryMetre:.5}];
  result.candidates=candidates;for(const candidate of candidates){economyModule.V2_ORDINARY_PRICING=Object.freeze({...productionPriceRule,...candidate});for(const city of cities)for(const profile of Object.keys(PROFILES))for(const policy of POLICIES)result.candidateRuns.push(simulate(city,policy,profile,candidate.id));}
  economyModule.V2_ORDINARY_PRICING=productionPriceRule;
 }
 result.finishedAt=new Date().toISOString();result.sourceDrift=sourceAtEnd();assert.equal(result.sourceDrift.length,0,'read-only production source identity');
 result.scratchRemoved=false;write('baseline-results.json',result);
 saveEvents();
 log({step:'complete',exit:0,baselineRuns:result.runs.length,candidateRuns:result.candidateRuns.length,events:allEvents.length,sourceDrift:result.sourceDrift});
}catch(error){process.exitCode=1;log({step:'failure',exit:1,message:error.stack});write('failure.json',{startedAt,command,error:error.stack,sourceHashes,eventsCompleted:allEvents.length});}
finally{
 saveEvents();
 fs.rmSync(scratch,{recursive:true,force:true});assert(!fs.existsSync(scratch));
 log({step:'scratch-cleanup',path:scratch,removed:true});
 write('run.log',runLog.map(x=>JSON.stringify(x)).join('\n')+'\n');
 const p=path.join(__dirname,'baseline-results.json');if(fs.existsSync(p)){const d=JSON.parse(fs.readFileSync(p));d.scratchRemoved=true;write('baseline-results.json',d);}
}
