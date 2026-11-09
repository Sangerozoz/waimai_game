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

const before=await observe();if(before.state.heroCompletedOrders!==3||before.loan.phase!=='returned')throw Error('Second delivery precondition changed');
await clickText('抢单');
const row=await p.evaluate(async()=>{const cc=await System.import('cc'),scene=cc.director.getScene(),canvas=document.querySelector('canvas'),rect=canvas.getBoundingClientRect();let found;const scan=node=>{if(!found&&node.activeInHierarchy&&/^Order-v2-road-/.test(node.name))found=node;for(const child of node.children)scan(child);};scan(scene);if(!found)throw Error('Offer missing');const screen=scene.getComponentsInChildren(cc.Camera)[0].worldToScreen(found.getWorldPosition());return {name:found.name,x:rect.left+screen.x/canvas.width*rect.width,y:rect.top+(canvas.height-screen.y)/canvas.height*rect.height};});
await p.touchscreen.tap(row.x,row.y);await pause(200);await clickText('选择路线 ›');const planned=await observe();if(planned.state.orders.at(-1).quote.vehicleId!=='starter-1'||'vehicleRef' in planned.state.orders.at(-1).quote)throw Error('Next signed batch did not use returned real car');await clickText('选择出发 ›');
await p.waitForFunction(async()=>{const cc=await System.import('cc'),r=cc.director.getScene().getComponentsInChildren(cc.Component).find(c=>cc.js.getClassName(c)==='V2RuntimeController');return r?.routeSnapshot?.phase==='pickup';},{timeout:10000});await pause(650);await clickText('到店取餐');
await p.waitForFunction(async()=>{const cc=await System.import('cc'),r=cc.director.getScene().getComponentsInChildren(cc.Component).find(c=>cc.js.getClassName(c)==='V2RuntimeController');return r?.routeSnapshot?.phase==='ready';},{timeout:6000});await pause(650);await clickText('去配送 ›');
await p.waitForFunction(async()=>{const cc=await System.import('cc'),r=cc.director.getScene().getComponentsInChildren(cc.Component).find(c=>cc.js.getClassName(c)==='V2RuntimeController');return r?.snapshot?.economy.state.heroCompletedOrders===4;},{timeout:10000});
const completed=await observe();await p.shot({type:'jpeg',maxEdge:960,quality:78});
if(completed.state.heroCompletedOrders!==4||completed.state.vehicles.length!==1||completed.state.riders[0].vehicleId!=='starter-1'||completed.state.cashCents!==10000||completed.loan.phase!=='returned')throw Error('Second real delivery changed loan ownership');
({before,row,planned,completed,errors:p.__loanErrors});
