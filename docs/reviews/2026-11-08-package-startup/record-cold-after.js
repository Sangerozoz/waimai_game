const p=await browser.getPage('main');
await p.setViewport({width:390,height:844,deviceScaleFactor:2,isMobile:true,hasTouch:true});await p.setCacheEnabled(false);
await p.emulateNetworkConditions({offline:false,download:200000,upload:93750,latency:150});
p.__startupErrors=[];p.on('pageerror',e=>p.__startupErrors.push(String(e)));
await p.goto('http://127.0.0.1:64466/?v2=1',{waitUntil:'domcontentloaded'});
await p.evaluate(()=>{
 const trace=globalThis.__coldTrace={entry:null,home:null,running:true};
 const resources=()=>performance.getEntriesByType('resource').map(x=>({url:x.name,durationMs:x.duration,encodedBytes:x.encodedBodySize,decodedBytes:x.decodedBodySize,transferBytes:x.transferSize}));
 async function watch(){
  if(!trace.running)return;
  try{if(globalThis.System){const cc=await System.import('cc'),scene=cc.director.getScene();if(scene){
   if(!trace.entry){const label=scene.getComponentsInChildren(cc.Label).find(l=>l.node.activeInHierarchy&&l.string==='开始游戏');if(label)trace.entry={atMs:performance.now(),slotEmpty:localStorage.getItem('delivery-county-single-slot-v1')===null,resources:resources()};}
   if(!trace.home){const cs=scene.getComponentsInChildren(cc.Component),r=cs.find(c=>cc.js.getClassName(c)==='V2RuntimeController'&&c.ready),ui=cs.find(c=>cc.js.getClassName(c)==='V2GameUI');if(r&&ui?.page==='首页')trace.home={atMs:performance.now(),phase:r.routeMotion.phase,page:ui.page,lastError:r.lastError,resources:resources()};}
  }}}catch(error){trace.observerError=String(error);}
  requestAnimationFrame(watch);
 }
 requestAnimationFrame(watch);return true;
});
JSON.stringify({started:true,url:await p.url()});
