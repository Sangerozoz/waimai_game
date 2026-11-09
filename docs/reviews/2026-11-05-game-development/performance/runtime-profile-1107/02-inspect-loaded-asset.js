const p=await browser.getPage('main');
p.__profileErrors=[];
p.on('pageerror',error=>p.__profileErrors.push(String(error)));
p.on('console',message=>{if(message.type()==='error')p.__profileErrors.push(message.text());});
await p.setViewport({width:390,height:844,deviceScaleFactor:2,isMobile:true,hasTouch:true});
await p.goto('http://127.0.0.1:4182/?v2=1',{waitUntil:'networkidle0'});
await p.waitForFunction(async()=>{
 if(!globalThis.System)return false;
 const cc=await System.import('cc');
 return !!cc.director.getScene()?.getComponentsInChildren(cc.Label).find(l=>l.node.activeInHierarchy&&l.string==='开始游戏');
},{timeout:15000});
const result=await p.evaluate(async()=>{
 if(localStorage.getItem('delivery-county-single-slot-v1')!==null)throw Error('Fresh headless origin unexpectedly contains progress');
 const cc=await System.import('cc'),{prepareCity}=await System.import('chunks:///_virtual/PlaceCatalog.ts'),{V2RouteSession}=await System.import('chunks:///_virtual/V2RouteSession.ts');
 const asset=await new Promise((resolve,reject)=>cc.resources.load('map-sample/city',cc.JsonAsset,(error,asset)=>error?reject(error):resolve(asset)));
 const raw=asset.json,city=prepareCity(raw);
 const sorted=x=>Array.isArray(x)?x.map(sorted):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,sorted(x[k])])):x;
 const digest=async x=>[...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(JSON.stringify(sorted(x)))))].map(x=>x.toString(16).padStart(2,'0')).join('');
 const bounds=city.dispatchBounds||city.playBounds,nodes=city.nodes.filter(n=>!bounds||n.x>=bounds.minX&&n.x<=bounds.maxX&&n.y>=bounds.minY&&n.y<=bounds.maxY),allowed=new Set(nodes.map(n=>n.id)),roads=[];
 for(const road of city.roads){let run=[],part=0;const flush=()=>{if(run.length>1)roads.push({...road,id:road.id+':v2:'+part++,nodes:run});run=[];};for(const id of road.nodes){if(allowed.has(id))run.push(id);else flush();}flush();}
 const places=city.pois.filter((p,i)=>allowed.has(p.node)&&(!city.operatingPOIs||city.operatingPOIs.includes(i)));
 return {url:location.href,viewport:{width:innerWidth,height:innerHeight,dpr:devicePixelRatio},freshOrigin:true,actualMapKey:new V2RouteSession(city).snapshot().mapKey,
  identity:{rawCitySortedSHA256:await digest(raw),routingGeometrySortedSHA256:await digest([nodes,roads,places]),cityPreparedSortedSHA256:await digest(city)},
  labels:cc.director.getScene().getComponentsInChildren(cc.Label).filter(l=>l.node.activeInHierarchy).map(l=>l.string),
  mainBundle:performance.getEntriesByType('resource').filter(e=>/assets\/main\/index\./.test(e.name)).map(e=>e.name)};
});
({result,errors:p.__profileErrors});
