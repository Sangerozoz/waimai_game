// Executable balance probe using current pure production domain functions.
// This is not a real road/player simulation; distances below are sensitivity inputs.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),crypto=require('node:crypto');
const project=process.env.PROJECT_ROOT||'/Users/sanger/Documents/ChatGPT/taptap 2';
const scripts=path.join(project,'delivery-game/assets/scripts');
const editor=process.env.COCOS_CREATOR||'/Applications/Cocos/Creator/3.8.8/CocosCreator.app';
const ts=require(path.join(editor,'Contents/Resources/app.asar.unpacked/node_modules/typescript'));
const output=fs.mkdtempSync(path.join(process.env.TMPDIR||'/Users/sanger/.hermes/cache/scratch','balance-probe-'));
try{
 const program=ts.createProgram(['domain/V2EconomySession.ts','domain/V2EconomyProfiles.ts'].map(p=>path.join(scripts,p)),{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS,strict:true,noEmitOnError:true,rootDir:scripts,outDir:output,skipLibCheck:true,types:[]});
 const emitted=program.emit(),diagnostics=ts.getPreEmitDiagnostics(program).concat(emitted.diagnostics);
 if(diagnostics.length)throw Error(ts.formatDiagnosticsWithColorAndContext(diagnostics,{getCanonicalFileName:f=>f,getCurrentDirectory:()=>project,getNewLine:()=> '\n'}));
 const {V2EconomySession}=require(path.join(output,'domain/V2EconomySession.js'));
 const profiles=require(path.join(output,'domain/V2EconomyProfiles.js'));
 const {V2_SLOT_CONFIG:C}=require(path.join(output,'domain/V2SlotEconomyConfig.js'));
 const context=(id,D)=>{const c=Object.create(null);c[id]={deliveryMetres:D};return c;};
 const rows=[];
 for(const completed of [14,15]){
  const e=new V2EconomySession('slots-v1');
  // Earn all funds/progression through actual domain acceptance and settlement.
  // Outcomes are explicitly perfect in this price-only probe, without road/risk simulation.
  for(let i=0;i<completed;i++){const id='probe-earned-'+i;e.acceptSlotBatch([{id,kind:'ordinary'}],context(id,1000));e.completeDelivery(id);}
  for(const D of [1,100,354,500,1000,2000,4000]){
   const q=V2EconomySession.restore(e.serialize()).acceptSlotBatch([{id:'probe-order',kind:'ordinary'}],context('probe-order',D))[0];
   rows.push({completedAtAcceptance:completed,hypotheticalDeliveryMetres:D,quotedCents:q.incomeCents,quotedCoins:q.incomeCents/100,xpMultiplier:q.xpMultiplier,priceVersion:q.ordinaryPricing.version,occupiedSlots:q.terms.load.occupiedSlots});
  }
 }
 const graduation=rows.filter(r=>r.completedAtAcceptance===15).map(after=>{const before=rows.find(r=>r.completedAtAcceptance===14&&r.hypotheticalDeliveryMetres===after.hypotheticalDeliveryMetres);return {deliveryMetres:after.hypotheticalDeliveryMetres,beforeCents:before.quotedCents,afterCents:after.quotedCents,deltaCents:after.quotedCents-before.quotedCents};});
 const marginal=[];
 for(const modelId of ['starter',...C.vehicles.map(v=>v.id)])for(let level=1;level<30;level++){
  const q=profiles.slotVehicleUpgradeQuote({modelId,level});
  marginal.push({kind:'vehicle',id:modelId,from:level,to:q.nextLevel,costCoins:q.costCents/100,capacityBefore:q.current.capacitySlots,capacityAfter:q.next.capacitySlots,capacityDelta:q.next.capacitySlots-q.current.capacitySlots,incomeGainPercent:(q.next.incomeFactor/q.current.incomeFactor-1)*100,speedGainPercent:(q.next.speedRelativeToStarter/q.current.speedRelativeToStarter-1)*100,serviceReductionDeltaPercent:0});
 }
 for(const id of ['npc-1','npc-15','npc-30'])for(let level=1;level<30;level++){
  const q=profiles.slotRiderUpgradeQuote(id,level);
  marginal.push({kind:'rider',id,from:level,to:q.nextLevel,costCoins:q.costCents/100,capacityBefore:null,capacityAfter:null,capacityDelta:null,incomeGainPercent:(q.next.incomeFactor/q.current.incomeFactor-1)*100,speedGainPercent:0,serviceReductionDeltaPercent:(q.next.fixedServiceReduction-q.current.fixedServiceReduction)*100});
 }
 const files=['domain/V2EconomySession.ts','domain/V2EconomyProfiles.ts','domain/V2SlotEconomyConfig.ts','domain/V2LoadRules.ts'];
 const result={kind:'current-domain-price-and-growth-probe',productionEdited:false,profileId:C.profileId,assumptions:['Pure quote sensitivity inputs, not production route samples','Map1, starter level1, earned progress14/15, no purchases','Perfect settlement in earned-history prefix only; no risk/road timing simulation','Marginal attributes are not a measured payback or player ROI'],sourceHashes:Object.fromEntries(files.map(f=>['delivery-game/assets/scripts/'+f,crypto.createHash('sha256').update(fs.readFileSync(path.join(scripts,f))).digest('hex')])),quoteRows:rows,protectionExit:graduation,priceDrops:graduation.filter(r=>r.deltaCents<0),growthSummary:{vehicleTransitions:marginal.filter(r=>r.kind==='vehicle').length,riderTransitions:marginal.filter(r=>r.kind==='rider').length,allCostsPositiveIntegers:marginal.every(r=>Number.isSafeInteger(r.costCoins)&&r.costCoins>0),vehicleLevelsWithNoCapacityIncrease:marginal.filter(r=>r.kind==='vehicle'&&r.capacityDelta===0).length},marginal};
 const dir=__dirname;fs.writeFileSync(path.join(dir,'current-probe-results.json'),JSON.stringify(result,null,2)+'\n');
 const columns=['kind','id','from','to','costCoins','capacityBefore','capacityAfter','capacityDelta','incomeGainPercent','speedGainPercent','serviceReductionDeltaPercent'];
 fs.writeFileSync(path.join(dir,'marginal-growth.csv'),columns.join(',')+'\n'+marginal.map(r=>columns.map(c=>r[c]??'').join(',')).join('\n')+'\n');
 console.log(JSON.stringify({profileId:result.profileId,rows:rows.length,protectionExit:graduation,priceDrops:result.priceDrops,growthSummary:result.growthSummary,results:path.join(dir,'current-probe-results.json')},null,2));
}finally{fs.rmSync(output,{recursive:true,force:true});}
