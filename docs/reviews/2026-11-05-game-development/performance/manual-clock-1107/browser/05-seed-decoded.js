const p=await browser.getPage('main');
const seeded=await p.evaluate(async()=>{
 const state=globalThis.__runtimeProfileSeed;if(!state||state.parts.length!==state.total)throw Error('Incomplete seed data');
 if(typeof DecompressionStream!=='function')throw Error('Browser gzip decoder unavailable');
 const bytes=Uint8Array.from(atob(state.parts.join('')),c=>c.charCodeAt(0));
 const raw=await new Response(new Blob([bytes]).stream().pipeThrough(new DecompressionStream('gzip'))).text();
 const digest=[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(raw)))].map(x=>x.toString(16).padStart(2,'0')).join('');
 if(digest!=="a258d09550462ff08ce0a9b2b40ff6e3be8f07fab5260b10c3bad6fdb5360ef5")throw Error('Lossless seed digest mismatch');
 if(localStorage.getItem('delivery-county-single-slot-v1')!==null)throw Error('Fresh-origin slot is not empty');
 const cc=await System.import('cc'),{prepareCity}=await System.import('chunks:///_virtual/PlaceCatalog.ts'),{V2GameSession}=await System.import('chunks:///_virtual/V2GameSession.ts');
 const asset=await new Promise((resolve,reject)=>cc.resources.load('map-sample/city',cc.JsonAsset,(error,asset)=>error?reject(error):resolve(asset)));
 const parsed=JSON.parse(raw),city=prepareCity(asset.json);V2GameSession.restore(city,raw,{preserveClock:true});
 localStorage.setItem('delivery-county-single-slot-v1',raw);
 return {oneInitializationWrite:true,bytes:raw.length,hero:parsed.dispatch.economy.state.heroCompletedOrders,npc:parsed.dispatch.economy.state.npcCompletedOrders,mapKey:parsed.route.mapKey};
});
await p.reload({waitUntil:'networkidle0'});
await p.waitForFunction(async()=>{const cc=await System.import('cc');return !!cc.director.getScene()?.getComponentsInChildren(cc.Label).find(l=>l.node.activeInHierarchy&&l.string==='继续游戏');},{timeout:15000});
({seeded,errors:p.__profileErrors});
