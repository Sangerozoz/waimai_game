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

await p.goto('http://127.0.0.1:4208/?v2=1',{waitUntil:'networkidle0'});
const original=await p.evaluate(async()=>{const raw=localStorage.getItem('delivery-county-single-slot-v1'),sha=[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(raw)))].map(x=>x.toString(16).padStart(2,'0')).join('');return {url:location.href,sha,version:JSON.parse(raw).version,mapKey:JSON.parse(raw).route.mapKey};});
if(original.sha!=='987a2af631e96a6f275897302a9bdf8da5ca5bc85fe64e19168a6ddb72533366')throw Error('Original failed input changed');({original,errors:p.__loanErrors});
