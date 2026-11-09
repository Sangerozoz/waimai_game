const p=await browser.getPage('main');
const pause=ms=>new Promise(resolve=>setTimeout(resolve,ms));
async function click(prefix){
 const point=await p.evaluate(async prefix=>{const cc=await System.import('cc'),scene=cc.director.getScene(),canvas=document.querySelector('canvas'),rect=canvas.getBoundingClientRect();
  const label=scene.getComponentsInChildren(cc.Label).find(l=>{if(!l.node.activeInHierarchy||!l.string.startsWith(prefix))return false;let n=l.node;while(n){if(n.name.startsWith('V2Action-')||n.name==='V2MainAction')return true;n=n.parent;}return false;});
  if(!label)throw Error('Visible action missing '+prefix);const screen=scene.getComponentsInChildren(cc.Camera)[0].worldToScreen(label.node.getWorldPosition());return {text:label.string,x:rect.left+screen.x/canvas.width*rect.width,y:rect.top+(canvas.height-screen.y)/canvas.height*rect.height};},prefix);
 await p.touchscreen.tap(point.x,point.y);return point;
}
const pickupTap=await click('到店取餐');
let phase='';
for(let i=0;i<35;i++){phase=await p.evaluate(()=>globalThis.__lightProfile.runtime.routeMotion.phase);if(phase==='ready')break;await pause(250);}
if(phase!=='ready')throw Error('Pickup did not reach ready; observed '+phase);
await p.evaluate(()=>{globalThis.__lightProfile.begin('ready-wait');return true;});await pause(2500);await p.evaluate(()=>globalThis.__lightProfile.end());
await p.evaluate(()=>{globalThis.__lightProfile.begin('actual-travel');return true;});const continueTap=await click('去配送');await pause(4000);await p.evaluate(()=>globalThis.__lightProfile.end());
const result=await p.evaluate(()=>{const p=globalThis.__lightProfile,r=p.runtime,s=r.snapshot;return {windows:p.windows.filter(w=>['ready-wait','actual-travel'].includes(w.name)).map(w=>({name:w.name,durationMs:w.end-w.start,tags:Object.entries(w.tags).map(([tag,t])=>({tag,count:t.count,totalMs:t.totalMs,selfMs:t.selfMs,maxMs:t.maxMs,errors:t.errors})),frameIntervals:w.frameIntervals,motion:w.motion.slice(0,3).concat(w.motion.slice(-3)),longTaskCount:w.longTasks.length})),end:{phase:r.routeMotion.phase,position:r.routeMotion.position,hero:s.economy.state.heroCompletedOrders,npc:s.economy.state.npcCompletedOrders,cashCents:s.economy.state.cashCents,lastError:r.lastError}};});
JSON.stringify({pickupTap,continueTap,result,errorCount:p.__profileErrors?.length??0,errorHead:(p.__profileErrors||[]).slice(0,2).map(x=>x.slice(0,400))});
