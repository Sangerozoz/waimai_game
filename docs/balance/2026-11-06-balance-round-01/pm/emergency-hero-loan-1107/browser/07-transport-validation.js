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

const expected={"sourceMapKey": "fnv2:318216:7809e3ba:9ad7ba6", "arrays": {"nodes": {"count": 42102, "sortedSHA": "9e91d496aa6fcd608e44f8d745c1835929a1ddd2d50cae37bdafba393468cdb1"}, "roads": {"count": 9970, "sortedSHA": "d71c22b545f3b270777bf2b286c6d0d9ef36463ee3c70c03c0feae345b54caa5"}, "pois": {"count": 617, "sortedSHA": "65e4baabea474da1aee7b2b7f1431453a1e41edb6a722511362f65811130a893"}}, "rawCitySortedSHA256": "c96f0c0c181db23b2bba7c01d5839a682dfedde35011128bc798c71411531eff", "routingGeometrySortedSHA256": "8fb422c406a3e10a1ac1e461a80df3d1f923b343abc97aa225a8ff69e7c5257c", "cityPreparedSortedSHA256": "bb88642edf762478e10a0766f067d8d6008788fa6cbbf4020ac6d155ee54504e", "sourceUnchanged": true};
const diagnostic=await p.evaluate(async expected=>{
 const cc=await System.import('cc'),{prepareCity}=await System.import('chunks:///_virtual/PlaceCatalog.ts'),{V2GameSession}=await System.import('chunks:///_virtual/V2GameSession.ts'),{V2RouteSession}=await System.import('chunks:///_virtual/V2RouteSession.ts');
 const bytes=localStorage.getItem('delivery-county-single-slot-v1'),original=JSON.parse(bytes),raw=cc.resources.get('map-sample/city',cc.JsonAsset).json,city=prepareCity(raw);
 const sorted=x=>Array.isArray(x)?x.map(sorted):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,sorted(x[k])])):x;
 const digest=async x=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(sorted(x)))))].map(x=>x.toString(16).padStart(2,'0')).join('');
 const bounds=city.dispatchBounds||city.playBounds,nodes=city.nodes.filter(n=>!bounds||n.x>=bounds.minX&&n.x<=bounds.maxX&&n.y>=bounds.minY&&n.y<=bounds.maxY),allowed=new Set(nodes.map(n=>n.id)),roads=[];
 for(const road of city.roads){let run=[],part=0;const flush=()=>{if(run.length>1)roads.push({...road,id:road.id+':v2:'+part++,nodes:run});run=[];};for(const id of road.nodes){if(allowed.has(id))run.push(id);else flush();}flush();}
 const places=city.pois.filter((p,i)=>allowed.has(p.node)&&(!city.operatingPOIs||city.operatingPOIs.includes(i)));
 const identity={rawCitySortedSHA256:await digest(raw),routingGeometrySortedSHA256:await digest([nodes,roads,places]),cityPreparedSortedSHA256:await digest(city)};
 for(const key of Object.keys(identity))if(identity[key]!==expected[key])throw Error('Geometry identity mismatch: '+key);
 const adjusted=JSON.parse(bytes),actualMapKey=new V2RouteSession(city).snapshot().mapKey;adjusted.route.mapKey=actualMapKey;
 const restored=V2GameSession.restore(city,JSON.stringify(adjusted),{preserveClock:true});
 if(restored.dispatch.emergencyLoanStatus.phase!=='available')throw Error('Adapted input differs');
 if(localStorage.getItem('delivery-county-single-slot-v1')!==bytes)throw Error('Read-only diagnostic changed original slot');
 return {identity,originalMapKey:original.route.mapKey,actualMapKey,adaptedMemoryRestore:true,originalSlotUnchanged:true,changedPaths:['route.mapKey'],loan:restored.dispatch.emergencyLoanStatus};
},expected);({diagnostic,errors:p.__loanErrors});
