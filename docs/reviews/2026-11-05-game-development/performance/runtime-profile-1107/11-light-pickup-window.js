const p=await browser.getPage('main');
await p.evaluate(()=>{globalThis.__lightProfile.begin('pickup-wait');return true;});
await new Promise(resolve=>setTimeout(resolve,3000));
const result=await p.evaluate(()=>{const p=globalThis.__lightProfile;p.end();const w=p.windows.at(-1);return {name:w.name,durationMs:w.end-w.start,tags:Object.entries(w.tags).map(([tag,t])=>({tag,count:t.count,totalMs:t.totalMs,selfMs:t.selfMs,maxMs:t.maxMs,errors:t.errors})),frameIntervals:w.frameIntervals,motion:w.motion.slice(0,2).concat(w.motion.slice(-2)),longTaskCount:w.longTasks.length,phase:p.runtime.routeMotion.phase,lastError:p.runtime.lastError};});
JSON.stringify({result,errorCount:p.__profileErrors?.length??0});
