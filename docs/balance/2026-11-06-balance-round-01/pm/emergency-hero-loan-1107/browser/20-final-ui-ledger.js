const p=await browser.getPage('main');
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function clickText(text){
 const point=await p.evaluate(async text=>{
  const cc=await System.import('cc'),scene=cc.director.getScene(),canvas=document.querySelector('canvas'),rect=canvas.getBoundingClientRect();
  const label=scene.getComponentsInChildren(cc.Label).find(label=>{
   if(label.string!==text||!label.node.activeInHierarchy)return false;
   let node=label.node;while(node){if(node.name.startsWith('V2Action-')||node.name==='V2MainAction')return true;node=node.parent;}return false;
  });
  if(!label)throw new Error('Visible action label missing: '+text);
  const camera=scene.getComponentsInChildren(cc.Camera)[0],screen=camera.worldToScreen(label.node.getWorldPosition());
  return {x:rect.left+screen.x/canvas.width*rect.width,y:rect.top+(canvas.height-screen.y)/canvas.height*rect.height,text};
 },text);
 if(point.x<0||point.y<0||point.x>390||point.y>844)throw new Error('Action outside viewport: '+JSON.stringify(point));
 await p.touchscreen.tap(point.x,point.y);await pause(200);return point;
}
async function observe(){
 return await p.evaluate(async()=>{
  const cc=await System.import('cc'),scene=cc.director.getScene(),components=scene.getComponentsInChildren(cc.Component);
  const runtime=components.find(c=>cc.js.getClassName(c)==='V2RuntimeController'),ui=components.find(c=>cc.js.getClassName(c)==='V2GameUI'),snap=runtime?.snapshot,route=runtime?.routeSnapshot,trip=runtime?.tripState;
  return {at:Date.now(),url:location.href,title:document.title,page:ui?.page,configuration:ui?.configureRider,loan:runtime?.emergencyLoanStatus,
   state:snap?{cashCents:snap.economy.state.cashCents,heroCompletedOrders:snap.economy.state.heroCompletedOrders,heroExperience:snap.economy.state.heroExperience,npcCompletedOrders:snap.economy.state.npcCompletedOrders,vehicles:snap.economy.state.vehicles,riders:snap.economy.state.riders,loanRecord:snap.economy.state.heroEmergencyLoan,quotaMs:snap.fleet.fleet.quotaMs,npcBatches:snap.fleet.fleet.batches,batchIds:snap.batchIds,orders:snap.orders}:null,
   route:route?{phase:route.phase,position:route.position,cursor:route.cursor,tripId:route.tripId,serviceCharged:route.serviceCharged}:null,
   trip:trip?{stamina:trip.stamina,rating:trip.rating,gameSeconds:trip.gameSeconds,action:trip.action,orders:trip.orders}:null,
   lastError:runtime?.lastError,uiMessage:ui?.message,slotVersion:JSON.parse(localStorage.getItem('delivery-county-single-slot-v1'))?.version,
   labels:scene.getComponentsInChildren(cc.Label).filter(label=>label.node.activeInHierarchy).map(label=>label.string)};
 });
}

await pause(900);const final=await observe();
const audit=await p.evaluate(async()=>{
 const raw=localStorage.getItem('delivery-county-single-slot-v1'),game=JSON.parse(raw),s=game.dispatch.economy.state;
 const orderEntries=s.ledger.entries.filter(e=>e.id.startsWith('order:'));
 const ids=orderEntries.map(e=>e.id);if(ids.length!==new Set(ids).size)throw Error('Duplicate delivery ledger');
 const calculated=s.ledger.opening.balanceCents+s.ledger.entries.reduce((n,e)=>n+e.amountCents,0);
 if(calculated!==s.cashCents||s.cashCents!==10000)throw Error('Final ledger does not reconcile');
 const emergency=game.dispatch.orders.filter(o=>o.quote.vehicleRef),real=game.dispatch.orders.filter(o=>!o.quote.vehicleRef);
 if(emergency.length!==2||emergency.some(o=>o.status!=='completed')||real.length!==2||real.some(o=>o.quote.vehicleId!=='starter-1'||o.status!=='completed'))throw Error('Historical contracts differ');
 if(s.vehicles.length!==1||s.heroEmergencyLoan.active!==false||s.riders[0].vehicleId!=='starter-1'||game.dispatch.fleet.fleet.batches.length!==0)throw Error('Final real-car/loan/NPC state differs');
 const sha=[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(raw)))].map(x=>x.toString(16).padStart(2,'0')).join('');
 return {versions:{Game:game.version,Dispatch:game.dispatch.version,Economy:game.dispatch.economy.version,Fleet:game.dispatch.fleet.version},calculatedCashCents:calculated,deliveryLedgerIds:ids,emergencyHistory:emergency.map(o=>({id:o.id,status:o.status,vehicleRef:o.quote.vehicleRef})),realHistory:real.map(o=>({id:o.id,status:o.status,vehicleId:o.quote.vehicleId})),localStorageKeys:Object.keys(localStorage),finalSlotSHA256:sha,serializedSlot:raw};
});
if(final.state.heroCompletedOrders!==4||final.state.npcCompletedOrders!==2||final.state.cashCents!==10000||final.labels.includes('应急借车')||final.lastError)throw Error('Final UI differs');
await p.shot({type:'jpeg',maxEdge:960,quality:78});({final,audit,errors:p.__loanErrors});
