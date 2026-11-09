const p=await browser.getPage('main');
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function clickAction(prefix){
 const point=await p.evaluate(async prefix=>{
  const cc=await System.import('cc'),scene=cc.director.getScene(),canvas=document.querySelector('canvas'),rect=canvas.getBoundingClientRect();
  const label=scene.getComponentsInChildren(cc.Label).find(l=>{
   if(!l.node.activeInHierarchy||!l.string.startsWith(prefix))return false;
   let n=l.node;while(n){if(n.name.startsWith('V2Action-')||n.name==='V2MainAction')return true;n=n.parent;}return false;
  });
  if(!label)throw Error('Visible action missing: '+prefix);
  const camera=scene.getComponentsInChildren(cc.Camera)[0],point=camera.worldToScreen(label.node.getWorldPosition());
  return {text:label.string,x:rect.left+point.x/canvas.width*rect.width,y:rect.top+(canvas.height-point.y)/canvas.height*rect.height};
 },prefix);
 if(point.x<0||point.x>390||point.y<0||point.y>844)throw Error('Action out of viewport');
 await p.touchscreen.tap(point.x,point.y);return point;
}
async function window(name,ms){
 await p.evaluate(name=>globalThis.__runtimeProfile.begin(name),name);
 await pause(ms);
 return await p.evaluate(()=>globalThis.__runtimeProfile.end());
}
const start=await p.evaluate(()=>{
 const r=globalThis.__runtimeProfile.runtime,s=r.snapshot;
 return {route:r.routeMotion,hero:s.economy.state.heroCompletedOrders,npc:s.economy.state.npcCompletedOrders,cashCents:s.economy.state.cashCents};
});
const pickup=await window('pickup-wait',3500);
const pickupTap=await clickAction('到店取餐');
await p.waitForFunction(()=>globalThis.__runtimeProfile.runtime.routeMotion.phase==='ready',{timeout:12000});
const ready=await window('ready-wait',3000);
await p.evaluate(()=>globalThis.__runtimeProfile.begin('actual-travel'));
const continueTap=await clickAction('去配送');
await pause(4500);
const travel=await p.evaluate(()=>globalThis.__runtimeProfile.end());
const result=await p.evaluate(()=>{
 const p=globalThis.__runtimeProfile,r=p.runtime,s=r.snapshot;
 const stats=rows=>{
  const a=rows.slice().sort((x,y)=>x-y),n=a.length;
  return n?{count:n,totalMs:a.reduce((x,y)=>x+y,0),medianMs:n%2?a[(n-1)/2]:(a[n/2-1]+a[n/2])/2,p95Ms:a[Math.min(n-1,Math.ceil(n*.95)-1)],maxMs:a[n-1]}:{count:0};
 };
 const windows=p.windows.map(w=>{
  const events=p.events.filter(e=>e.window===w.name),frames=p.frames.filter(f=>f.window===w.name),tags=[...new Set(events.map(e=>e.tag))];
  return {...w,durationMs:w.end-w.start,frames:stats(frames.filter(f=>f.intervalMs!==null).map(f=>f.intervalMs)),over50ms:frames.filter(f=>f.intervalMs>50).length,
   tags:tags.map(tag=>{const rows=events.filter(e=>e.tag===tag);return {tag,elapsed:stats(rows.map(e=>e.durationMs)),self:stats(rows.map(e=>e.selfMs)),throws:rows.filter(e=>e.threw).length};}),
   phases:[...new Set(frames.map(f=>f.phase))],longTasks:p.longTasks.filter(e=>e.start<w.end&&e.start+e.durationMs>w.start)};
 });
 return {scope:'actual instrumented packed Runtime/UI/Store in fresh headless Chrome; wrappers forward original methods; rAF intervals are not physical device FPS',windows,hooks:p.hooks,dropped:p.dropped,
  events:p.events,frames:p.frames,longTasks:p.longTasks,
  end:{route:r.routeMotion,hero:s.economy.state.heroCompletedOrders,npc:s.economy.state.npcCompletedOrders,cashCents:s.economy.state.cashCents,quotaMs:s.fleet.fleet.quotaMs,slotCharacters:localStorage.getItem('delivery-county-single-slot-v1').length,lastError:r.lastError},
  userStorageAccess:false};
});
({start,pickup,pickupTap,ready,continueTap,travel,result,errors:p.__profileErrors});
