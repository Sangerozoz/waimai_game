const p=await browser.getPage('main');
const result=await p.evaluate(async()=>{
 const cc=await System.import('cc'),p=globalThis.__runtimeProfile,r=p.runtime,s=r.snapshot;
 const stats=rows=>{
  const a=rows.slice().sort((x,y)=>x-y),n=a.length;
  return n?{count:n,totalMs:a.reduce((x,y)=>x+y,0),medianMs:n%2?a[(n-1)/2]:(a[n/2-1]+a[n/2])/2,p95Ms:a[Math.min(n-1,Math.ceil(n*.95)-1)],maxMs:a[n-1]}:{count:0};
 };
 const windows=p.windows.map(w=>{
  const events=p.events.filter(e=>e.window===w.name),frames=p.frames.filter(f=>f.window===w.name),tags=[...new Set(events.map(e=>e.tag))];
  return {...w,durationMs:w.end-w.start,frames:stats(frames.filter(f=>f.intervalMs!==null).map(f=>f.intervalMs)),over50ms:frames.filter(f=>f.intervalMs>50).length,
   tags:tags.map(tag=>{const rows=events.filter(e=>e.tag===tag);return {tag,elapsed:stats(rows.map(e=>e.durationMs)),self:stats(rows.map(e=>e.selfMs)),throws:rows.filter(e=>e.threw).length};}),
   phases:[...new Set(frames.map(f=>f.phase))],longTasks:p.longTasks.filter(e=>e.start<w.end&&e.start+e.durationMs>w.start),
   motionHead:frames.slice(0,2),motionTail:frames.slice(-2)};
 });
 return {scope:'actual instrumented packed Runtime/UI/Store in fresh headless Chrome; wrappers forward originals; rAF intervals are not physical device FPS',windows,dropped:p.dropped,
  traceCounts:{events:p.events.length,frames:p.frames.length,longTasks:p.longTasks.length},
  end:{route:r.routeMotion,hero:s.economy.state.heroCompletedOrders,npc:s.economy.state.npcCompletedOrders,cashCents:s.economy.state.cashCents,quotaMs:s.fleet.fleet.quotaMs,slotCharacters:localStorage.getItem('delivery-county-single-slot-v1').length,lastError:r.lastError},
  labels:cc.director.getScene().getComponentsInChildren(cc.Label).filter(l=>l.node.activeInHierarchy).map(l=>l.string),userStorageAccess:false};
});
({result,errors:p.__profileErrors});
