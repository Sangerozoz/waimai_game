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

const before=await observe();await clickText('取消');const cancelled=await observe();if(cancelled.loan.phase!=='returnable'||cancelled.state.riders[0].vehicleId!==null)throw Error('Return cancel changed state');
await clickText('取回并归还');const confirmation=await clickText('确认归还');const returned=await observe();await p.shot({type:'jpeg',maxEdge:960,quality:78});
if(returned.loan.phase!=='returned'||returned.state.loanRecord.active!==false||returned.state.riders[0].vehicleId!=='starter-1'||returned.state.riders.find(r=>r.id==='npc-1').vehicleId!==null||returned.state.vehicles.length!==1||returned.state.cashCents!==8000||returned.slotVersion!==7)throw Error('Return is not an atomic real-car swap');
await p.reload({waitUntil:'networkidle0'});await p.waitForFunction(async()=>{const cc=await System.import('cc');return !!cc.director.getScene()?.getComponentsInChildren(cc.Label).find(l=>l.string==='继续游戏');},{timeout:10000});await clickText('继续游戏');
await p.waitForFunction(async()=>{const cc=await System.import('cc');return !!cc.director.getScene()?.getComponentsInChildren(cc.Component).find(c=>cc.js.getClassName(c)==='V2RuntimeController'&&c.ready);},{timeout:10000});await pause(650);
const reloaded=await observe();await p.shot({type:'jpeg',maxEdge:960,quality:78});
if(reloaded.loan.phase!=='returned'||reloaded.state.riders[0].vehicleId!=='starter-1'||reloaded.state.cashCents!==8000||JSON.stringify(reloaded.state.orders)!==JSON.stringify(returned.state.orders))throw Error('Returned loan or old signed histories failed reload');
({before,cancelled,confirmation,returned,reloaded,errors:p.__loanErrors});
