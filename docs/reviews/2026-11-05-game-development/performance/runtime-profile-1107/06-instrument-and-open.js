const p=await browser.getPage('main');
const installed=await p.evaluate(async()=>{
 const cc=await System.import('cc');
 const modules={};
 for(const name of ['V2RuntimeController','V2RuntimeStore','V2GameSession','V2DispatchSession','V2FleetSession','V2EconomySession','V2GameUI','CityMap']){
  const imported=await System.import('chunks:///_virtual/'+name+'.ts');
  if(typeof imported[name]!=='function')throw Error('Missing packed class '+name);
  modules[name]=imported[name];
 }
 if(globalThis.__runtimeProfile)throw Error('Profiling is already installed');
 const profile=globalThis.__runtimeProfile={events:[],frames:[],longTasks:[],windows:[],hooks:[],dropped:{events:0,frames:0,longTasks:0},runtime:null,ui:null,active:null,stack:[],nextId:0,previousFrame:null,running:true};
 const push=(key,row)=>{if(profile[key].length<60000)profile[key].push(row);else profile.dropped[key]++;};
 function observed(tag,original,args,receiver){
  const window=profile.active;if(!window)return Reflect.apply(original,receiver,args);
  const start=performance.now(),frame={id:++profile.nextId,tag,childMs:0},parent=profile.stack.at(-1);
  profile.stack.push(frame);let threw=false,result;
  try{result=Reflect.apply(original,receiver,args);return result;}
  catch(error){threw=true;throw error;}
  finally{
   const end=performance.now(),durationMs=end-start;
   profile.stack.pop();if(parent)parent.childMs+=durationMs;
   push('events',{window:window.name,id:frame.id,parentId:parent?.id??null,tag,start,end,durationMs,selfMs:Math.max(0,durationMs-frame.childMs),threw,
    ...(typeof result==='string'?{resultCharacters:result.length}:{}),
    ...(tag==='store.commit'?{inputCharacters:args[0].length}:{})});
  }
 }
 function wrap(object,name,tag){
  const original=object[name];if(typeof original!=='function')throw Error('Missing profile method '+tag);
  object[name]=function(...args){return observed(tag,original,args,this);};profile.hooks.push(tag);
 }
 function getter(object,name,tag){
  const descriptor=Object.getOwnPropertyDescriptor(object,name);if(!descriptor?.get)throw Error('Missing profile getter '+tag);
  const original=descriptor.get;
  Object.defineProperty(object,name,{...descriptor,get:function(){return observed(tag,original,[],this);}});profile.hooks.push(tag);
 }
 const R=modules.V2RuntimeController,G=modules.V2GameSession,D=modules.V2DispatchSession,F=modules.V2FleetSession,E=modules.V2EconomySession,U=modules.V2GameUI;
 for(const [name,tag] of [['update','runtime.update'],['mutate','runtime.mutate']])wrap(R.prototype,name,tag);
 for(const [name,tag] of [['restore','game.restore']])wrap(G,name,tag);
 for(const name of ['tick','serialize'])wrap(G.prototype,name,'game.'+name);
 wrap(D,'restore','dispatch.restore');
 for(const name of ['snapshot','serialize','transact','validate'])wrap(D.prototype,name,'dispatch.'+name);
 wrap(F,'restore','fleet.restore');
 for(const name of ['serialize','validate','atomic','syncDraft','syncHeroCompletions','advanceTo'])wrap(F.prototype,name,'fleet.'+name);
 wrap(E,'restore','economy.restore');
 for(const name of ['serialize','replaceFrom'])wrap(E.prototype,name,'economy.'+name);
 getter(E.prototype,'state','economy.state');
 wrap(modules.V2RuntimeStore.prototype,'commit','store.commit');
 for(const name of ['update','render','refreshHUD','refreshNPCActivity','refreshRiderStatuses','refreshFunds'])wrap(U.prototype,name,'ui.'+name);
 for(const name of ['setRider','syncOverlay','syncDetails'])wrap(modules.CityMap.prototype,name,'map.'+name);
 for(const name of ['getItem','setItem']){
  const original=Storage.prototype[name];
  Storage.prototype[name]=function(...args){
   if(args[0]==='delivery-county-single-slot-v1'||args[0]==='delivery-county-single-slot-epoch-v1')return observed('storage.'+name,original,args,this);
   return Reflect.apply(original,this,args);
  };profile.hooks.push('storage.'+name);
 }
 profile.begin=name=>{
  if(profile.active)throw Error('A profile window is already active');
  const window={name,start:performance.now(),end:null};profile.windows.push(window);profile.active=window;profile.previousFrame=null;return window.start;
 };
 profile.end=()=>{if(!profile.active)throw Error('No active profile window');profile.active.end=performance.now();const window={...profile.active};profile.active=null;profile.previousFrame=null;return window;};
 const observer=new PerformanceObserver(list=>{for(const item of list.getEntries())push('longTasks',{start:item.startTime,durationMs:item.duration,name:item.name});});
 observer.observe({type:'longtask',buffered:false});profile.observer=observer;
 function frame(at){
  if(!profile.running)return;
  if(profile.active){
   const runtime=profile.runtime,motion=runtime?.routeMotion,view=profile.ui?.map?.captureView();
   push('frames',{window:profile.active.name,at,intervalMs:profile.previousFrame===null?null:at-profile.previousFrame,
    phase:motion?.phase??null,cursor:motion?.cursor??null,tripId:motion?.tripId??null,position:motion?.position??null,
    follow:view?.follow??null,offset:view?.offset??null,scale:view?.scale??null,publishedAtSeconds:runtime?.publishedAtSeconds??null});
   profile.previousFrame=at;
  }
  requestAnimationFrame(frame);
 }
 requestAnimationFrame(frame);profile.begin('open-continue');
 return {hooks:profile.hooks,slotCharacters:localStorage.getItem('delivery-county-single-slot-v1').length};
});
const point=await p.evaluate(async()=>{
 const cc=await System.import('cc'),scene=cc.director.getScene(),canvas=document.querySelector('canvas'),rect=canvas.getBoundingClientRect();
 const label=scene.getComponentsInChildren(cc.Label).find(l=>l.node.activeInHierarchy&&l.string==='继续游戏');
 if(!label)throw Error('Continue action is not visible');
 const camera=scene.getComponentsInChildren(cc.Camera)[0],screen=camera.worldToScreen(label.node.getWorldPosition());
 return {x:rect.left+screen.x/canvas.width*rect.width,y:rect.top+(canvas.height-screen.y)/canvas.height*rect.height};
});
if(point.x<0||point.x>390||point.y<0||point.y>844)throw Error('Continue action outside viewport');
await p.touchscreen.tap(point.x,point.y);
await p.waitForFunction(async()=>{
 const cc=await System.import('cc');
 return !!cc.director.getScene()?.getComponentsInChildren(cc.Component).find(c=>cc.js.getClassName(c)==='V2RuntimeController'&&c.ready);
},{timeout:45000});
const opened=await p.evaluate(async()=>{
 const cc=await System.import('cc'),components=cc.director.getScene().getComponentsInChildren(cc.Component),profile=globalThis.__runtimeProfile;
 profile.runtime=components.find(c=>cc.js.getClassName(c)==='V2RuntimeController');profile.ui=components.find(c=>cc.js.getClassName(c)==='V2GameUI');
 const window=profile.end(),snapshot=profile.runtime.snapshot,route=profile.runtime.routeMotion;
 return {window,phase:route.phase,page:profile.ui.page,cashCents:snapshot.economy.state.cashCents,heroCompletedOrders:snapshot.economy.state.heroCompletedOrders,npcCompletedOrders:snapshot.economy.state.npcCompletedOrders,
  quotaMs:snapshot.fleet.fleet.quotaMs,npcBatches:snapshot.fleet.fleet.batches.length,batchIds:snapshot.batchIds,
  slotCharacters:localStorage.getItem('delivery-county-single-slot-v1').length,lastError:profile.runtime.lastError,
  labels:cc.director.getScene().getComponentsInChildren(cc.Label).filter(l=>l.node.activeInHierarchy).map(l=>l.string),eventCount:profile.events.length};
});
({installed,continueTap:point,opened,errors:p.__profileErrors});
