const p=await browser.getPage('main');
await p.evaluate(async()=>{
 const cc=await System.import('cc'),names=['V2RuntimeController','V2RuntimeStore','V2GameSession','V2DispatchSession','V2FleetSession','V2EconomySession','V2GameUI','CityMap'],classes={};
 for(const name of names)classes[name]=(await System.import('chunks:///_virtual/'+name+'.ts'))[name];
 const profile=globalThis.__lightProfile={active:null,windows:[],stack:[],runtime:null,ui:null,running:true};
 function call(tag,original,receiver,args){
  const window=profile.active;if(!window)return Reflect.apply(original,receiver,args);
  const start=performance.now(),entry={children:0},parent=profile.stack.at(-1);profile.stack.push(entry);let error=false;
  try{return Reflect.apply(original,receiver,args);}catch(e){error=true;throw e;}
  finally{
   const duration=performance.now()-start;profile.stack.pop();if(parent)parent.children+=duration;
   const t=window.tags[tag]??(window.tags[tag]={count:0,totalMs:0,selfMs:0,maxMs:0,errors:0,samples:[]});
   t.count++;t.totalMs+=duration;t.selfMs+=Math.max(0,duration-entry.children);t.maxMs=Math.max(t.maxMs,duration);if(error)t.errors++;
   if(t.samples.length<80)t.samples.push(Math.round(duration*1000)/1000);
  }
 }
 function method(target,name,tag){const original=target[name];if(typeof original!=='function')throw Error('Missing '+tag);target[name]=function(...args){return call(tag,original,this,args);};}
 const G=classes.V2GameSession,D=classes.V2DispatchSession,F=classes.V2FleetSession,E=classes.V2EconomySession;
 method(classes.V2RuntimeController.prototype,'update','runtime.update');method(classes.V2RuntimeController.prototype,'mutate','runtime.mutate');
 method(G,'restore','game.restore');method(G.prototype,'tick','game.tick');method(G.prototype,'serialize','game.serialize');
 method(D,'restore','dispatch.restore');for(const name of ['snapshot','serialize','transact','validate'])method(D.prototype,name,'dispatch.'+name);
 method(F,'restore','fleet.restore');for(const name of ['serialize','validate','atomic','syncHeroCompletions','advanceTo'])method(F.prototype,name,'fleet.'+name);
 method(E,'restore','economy.restore');method(E.prototype,'serialize','economy.serialize');
 const descriptor=Object.getOwnPropertyDescriptor(E.prototype,'state');Object.defineProperty(E.prototype,'state',{...descriptor,get:function(){return call('economy.state',descriptor.get,this,[]);}});
 method(classes.V2RuntimeStore.prototype,'commit','store.commit');method(classes.V2GameUI.prototype,'update','ui.update');method(classes.V2GameUI.prototype,'render','ui.render');method(classes.CityMap.prototype,'setRider','map.setRider');
 for(const name of ['getItem','setItem']){const original=Storage.prototype[name];Storage.prototype[name]=function(...args){return args[0]==='delivery-county-single-slot-v1'?call('storage.'+name,original,this,args):Reflect.apply(original,this,args);};}
 profile.begin=name=>{if(profile.active)throw Error('Active window');const w={name,start:performance.now(),end:null,tags:{},frameIntervals:[],motion:[],longTasks:[],lastFrame:null};profile.windows.push(w);profile.active=w;};
 profile.end=()=>{const w=profile.active;if(!w)throw Error('No active window');w.end=performance.now();profile.active=null;return w.name;};
 const observer=new PerformanceObserver(list=>{const w=profile.active;if(w)for(const item of list.getEntries())if(w.longTasks.length<100)w.longTasks.push({start:item.startTime,durationMs:item.duration});});observer.observe({type:'longtask',buffered:false});profile.observer=observer;
 function frame(at){if(!profile.running)return;const w=profile.active;if(w){if(w.lastFrame!==null&&w.frameIntervals.length<500)w.frameIntervals.push(Math.round((at-w.lastFrame)*1000)/1000);w.lastFrame=at;
  if(w.motion.length<100){const r=profile.runtime,m=r?.routeMotion;w.motion.push({at,phase:m?.phase??null,cursor:m?.cursor??null,position:m?.position??null,follow:profile.ui?.map?.isFollowing??null});}}
  requestAnimationFrame(frame);}
 requestAnimationFrame(frame);profile.begin('open-continue');
 return 'instrumented';
});
const point=await p.evaluate(async()=>{const cc=await System.import('cc'),s=cc.director.getScene(),canvas=document.querySelector('canvas'),r=canvas.getBoundingClientRect(),l=s.getComponentsInChildren(cc.Label).find(l=>l.node.activeInHierarchy&&l.string==='继续游戏');if(!l)throw Error('Continue missing');const screen=s.getComponentsInChildren(cc.Camera)[0].worldToScreen(l.node.getWorldPosition());return {x:r.left+screen.x/canvas.width*r.width,y:r.top+(canvas.height-screen.y)/canvas.height*r.height};});
await p.touchscreen.tap(point.x,point.y);
await p.waitForFunction(async()=>{const cc=await System.import('cc');return !!cc.director.getScene()?.getComponentsInChildren(cc.Component).find(c=>cc.js.getClassName(c)==='V2RuntimeController'&&c.ready);},{timeout:40000});
const result=await p.evaluate(async()=>{const cc=await System.import('cc'),cs=cc.director.getScene().getComponentsInChildren(cc.Component),p=globalThis.__lightProfile;p.runtime=cs.find(c=>cc.js.getClassName(c)==='V2RuntimeController');p.ui=cs.find(c=>cc.js.getClassName(c)==='V2GameUI');p.end();return {phase:p.runtime.routeMotion.phase,page:p.ui.page,windowCount:p.windows.length,lastError:p.runtime.lastError};});
JSON.stringify({result,errorCount:p.__profileErrors?.length??0});
