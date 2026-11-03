/* Independent coordinate visualizer. It never loads or writes game storage. */
(async()=>{
 const canvas=document.getElementById('view'),ctx=canvas.getContext('2d'),view=canvas.parentElement,slider=document.getElementById('progress'),percent=document.getElementById('percent');
 const sceneName=new URLSearchParams(location.search).get('scene')==='county'?'county':'sample';
 const sceneFile=sceneName==='county'?'county-scene-layout.json':'sample-scene-layout-v2.json';
 const minScale=.06;if(sceneName==='county')document.getElementById('overview').hidden=false;
 const [data,reference]=await Promise.all([fetch(sceneFile).then(r=>{if(!r.ok)throw Error('地块数据不可用');return r.json()}),fetch('sample-route-reference.json').then(r=>{if(!r.ok)throw Error('路线数据不可用');return r.json()})]);
 const materialSpec={asphalt:['HG01-asphalt.png',12],paving:['HG02-sidewalk.png',6],grass:['HG03-grass.png',8],water:['HG04-water.png',16],roof:['RF01-clean-roof.png',6]};
 const materials={};
 await Promise.all(Object.entries(materialSpec).map(([key,[file,metres,metresY]])=>new Promise(resolve=>{
  const image=new Image();image.onload=()=>{const pattern=ctx.createPattern(image,'repeat');if(pattern){pattern.setTransform(new DOMMatrix().scale(metres/image.naturalWidth,(metresY||metres)/image.naturalHeight));materials[key]=pattern;}resolve();};image.onerror=()=>resolve();image.src='materials/'+file;
 })));
 const facadeImages={};
 await Promise.all([['store','SF01-storefront-bay.png'],['upper','SF02-upper-floor-bay.png']].map(([key,file])=>new Promise(resolve=>{const image=new Image();image.onload=()=>{facadeImages[key]=image;resolve()};image.onerror=()=>resolve();image.src='materials/'+file;})));
 const treeImage=await new Promise(resolve=>{const image=new Image();image.onload=()=>resolve(image);image.onerror=()=>resolve(null);image.src='materials/HT01-ground-tree-v1.png';});
 // Only the initial D vehicle has approved candidate frames; absent/failed frames use a marker.
 try{
  const response=await fetch('rider-directions/manifest.json');if(!response.ok)throw Error('方向素材未提供');
  const manifest=await response.json(),names=['n','ne','e','se','s','sw','w','nw'],frames={};
  if(manifest.version===1&&manifest.vehicleTier===1&&Array.isArray(manifest.assets))await Promise.all(manifest.assets.map(asset=>new Promise(resolve=>{
   const direction=asset.screen_heading;if(!names.includes(direction)||asset.file!=='rider-d-'+direction+'.png'||!Array.isArray(asset.subject_bbox_alpha_gt_16)||!Array.isArray(asset.groundAnchor)||!Array.isArray(asset.frontWheelContact)||!Array.isArray(asset.backWheelContact)){resolve();return;}
   const [left,top,right,bottom]=asset.subject_bbox_alpha_gt_16,wheelPixels=Math.hypot(asset.frontWheelContact[0]-asset.backWheelContact[0],asset.frontWheelContact[1]-asset.backWheelContact[1]);
   if(!(right>left&&bottom>top&&wheelPixels>0)){resolve();return;}
   const image=new Image();image.onload=()=>{frames[direction]={image,crop:[left,top,right-left,bottom-top],contact:asset.groundAnchor,wheelPixels,wheelbaseMetres:manifest.wheelbaseMetresCandidate,heading:direction};resolve();};image.onerror=()=>resolve();image.src='rider-directions/'+asset.file;
  })));
  window.CountySampleRider.registerFrames(frames);
 }catch(_){/* Keep position marker when the candidate art is unavailable. */}
 let outer=null;
 if(sceneName==='county'){try{const response=await fetch('outer-landscape.json');if(response.ok)outer=new window.CountyOuterLandscape(await response.json());}catch(_){/* Blue-area scene remains available if outer scenery is missing. */}}
 const bounds=data.bounds,displayBounds=outer?outer.data.displayBounds:bounds,center=[-1530,-20],referenceRoute=reference.outbound.points,sceneIndex=new window.CountySceneIndex(data);
 let riderDirection='s',previousRider=null;
 let route=referenceRoute,liveState=null;const live=new URLSearchParams(location.search).get('live')==='1'&&window.parent!==window;
 if(live){slider.disabled=true;document.querySelector('header p').textContent='实时只读投影 · 配送操作在原游戏中完成';}
 let scale=1,pan=[0,0],width=1,height=1,dpr=1;const touches=new Map();let gesture=null;
 // The same affine ground projection is used by every spatial layer.
 const ground=p=>[(p[0]-center[0]-(p[1]-center[1]))*.8660254,-((p[0]-center[0])+(p[1]-center[1]))*.5];
 const screen=(p,z=0)=>{const q=ground(p);return [width/2+pan[0]+q[0]*scale,height/2+pan[1]+(q[1]-z)*scale]};
 // World-space pattern phase is fixed to ground coordinates, including when panning and zooming.
 function textured(rings,name,opacity=1,z=0){
  const pattern=materials[name];if(scale<.3||!pattern||!rings?.length)return;
  ctx.save();ctx.globalAlpha=opacity;
  const a=.8660254*scale,b=-.5*scale,c=-.8660254*scale,d=-.5*scale;
  const e=width/2+pan[0]-a*center[0]-c*center[1],f=height/2+pan[1]-b*center[0]-d*center[1]-z*scale;
  ctx.transform(a,b,c,d,e,f);ctx.beginPath();for(const ring of rings){if(!ring?.length)continue;ring.forEach((p,i)=>{if(i)ctx.lineTo(p[0],p[1]);else ctx.moveTo(p[0],p[1])});ctx.closePath();}
  ctx.fillStyle=pattern;ctx.fill('evenodd');ctx.restore();
 }
 function polygon(ring,fill,stroke,z=0){if(!ring?.length)return;ctx.beginPath();ring.forEach((p,i)=>{const q=screen(p,z);if(i)ctx.lineTo(...q);else ctx.moveTo(...q)});ctx.closePath();if(fill){ctx.fillStyle=fill;ctx.fill()}if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=Math.max(.7,scale*.25);ctx.stroke()}}
 function path(points,color,lineWidth){if(points.length<2)return;ctx.beginPath();points.forEach((p,i)=>{const q=screen(p);if(i)ctx.lineTo(...q);else ctx.moveTo(...q)});ctx.strokeStyle=color;ctx.lineWidth=lineWidth;ctx.lineJoin='round';ctx.lineCap='round';ctx.stroke()}
 function road(points,w,color,material){for(let i=1;i<points.length;i++){const a=points[i-1],b=points[i],dx=b[0]-a[0],dy=b[1]-a[1],len=Math.hypot(dx,dy);if(!len)continue;const nx=-dy/len*w/2,ny=dx/len*w/2;const shape=[[a[0]+nx,a[1]+ny],[b[0]+nx,b[1]+ny],[b[0]-nx,b[1]-ny],[a[0]-nx,a[1]-ny]];polygon(shape,color);if(material)textured([shape],material,.62)}}
 function building(obj){window.CountyStreetFacades.draw(ctx,obj,{screen,polygon,textured,scale,facadeImages});}
 function tree(t){
  const p=screen(t.groundAnchor),r=Math.max(1,t.crownDiameterMetres*scale*.42);
  ctx.fillStyle='#586a4b44';ctx.beginPath();ctx.ellipse(p[0]+r*.4,p[1]+r*.25,r*1.1,r*.42,0,0,Math.PI*2);ctx.fill();
  if(treeImage){const source=[151,12,973,1215],targetHeight=(t.heightMetres||7)*scale,targetWidth=targetHeight*source[2]/source[3],rootX=(637-source[0])/source[2],rootY=(1218-source[1])/source[3];
   ctx.drawImage(treeImage,...source,p[0]-rootX*targetWidth,p[1]-rootY*targetHeight,targetWidth,targetHeight);return;}
  const z=(t.heightMetres||5)*scale*.55;ctx.strokeStyle='#806d4f';ctx.lineWidth=Math.max(.7,scale*.5);ctx.beginPath();ctx.moveTo(...p);ctx.lineTo(p[0],p[1]-z);ctx.stroke();ctx.fillStyle='#829f67';ctx.beginPath();ctx.arc(p[0],p[1]-z,r,0,Math.PI*2);ctx.fill();
 }
 function drawRider(point,label,tier){const frame=scale>=2.5&&tier===1?window.CountySampleRider.frames[riderDirection]:null;if(!window.CountySampleRider.draw(ctx,frame,screen(point),scale))marker(point,label,'#db6f28');}
 function drawRoadMarkings(roads){
  if(scale<.8)return;const jointMap=new Map();
  for(const rd of roads){if(!rd.nodeA||!rd.nodeB||rd.bridge)continue;for(const id of [rd.nodeA,rd.nodeB]){const list=jointMap.get(id);if(list)list.push(rd);else jointMap.set(id,[rd]);}}
  for(const rd of roads){
   if(rd.bridge||rd.width<7)continue;const [a,b]=rd.points,dx=b[0]-a[0],dy=b[1]-a[1],len=Math.hypot(dx,dy);if(len<16)continue;
   const ux=dx/len,uy=dy/len,nx=-uy,ny=ux;
   for(let d=10;d<len-10;d+=11)path([[a[0]+ux*d,a[1]+uy*d],[a[0]+ux*(d+3),a[1]+uy*(d+3)]],'#edf2ed',Math.max(.7,scale*.18));
   for(const [id,start,sign] of [[rd.nodeA,a,1],[rd.nodeB,b,-1]]){
    const joint=jointMap.get(id)||[];if(joint.length<3||joint.some(v=>v.bridge))continue;
    const hasCross=joint.some(v=>{if(v===rd)return false;const [p,q]=v.points,vx=q[0]-p[0],vy=q[1]-p[1],length=Math.hypot(vx,vy);return length>8&&Math.abs((vx*ux+vy*uy)/length)<.5;});if(!hasCross)continue;
    const d=Math.min(len*.35,6),cx=start[0]+ux*d*sign,cy=start[1]+uy*d*sign,usable=Math.max(0,rd.width/2-.6);
    for(let side=-usable;side<=usable;side+=1.2){const x=cx+nx*side,y=cy+ny*side;path([[x-ux*.8,y-uy*.8],[x+ux*.8,y+uy*.8]],'#f8f6ed',Math.max(.8,scale*.55));}
   }
  }
 }
 function featureRect(feature){const [a,b]=feature.bounds;return [[a[0],a[1]],[b[0],a[1]],[b[0],b[1]],[a[0],b[1]]];}
 function featureCenter(feature){const [a,b]=feature.bounds;return [(a[0]+b[0])/2,(a[1]+b[1])/2];}
 function court(feature){
  const [a,b]=feature.bounds,left=Math.min(a[0],b[0]),right=Math.max(a[0],b[0]),bottom=Math.min(a[1],b[1]),top=Math.max(a[1],b[1]);
  polygon(featureRect(feature),'#bd8f7d','#eee3d0');
  const margin=Math.min(1.3,(right-left)/8,(top-bottom)/8),l=left+margin,r=right-margin,bot=bottom+margin,t=top-margin;
  const stroke=Math.max(.7,scale*.18),white='#f9f3e4';path([[l,bot],[r,bot],[r,t],[l,t],[l,bot]],white,stroke);
  const mx=(l+r)/2,my=(bot+t)/2;path([[mx,bot],[mx,t]],white,stroke);
  const circle=[];for(let i=0;i<=24;i++){const angle=i*Math.PI/12;circle.push([mx+Math.cos(angle)*Math.min(3,(r-l)/8),my+Math.sin(angle)*Math.min(3,(t-bot)/8)])}path(circle,white,stroke);
  for(const edge of [l,r]){const inset=edge===l?1:-1;path([[edge,my-3],[edge+inset*3,my-3],[edge+inset*3,my+3],[edge,my+3]],white,stroke);}
 }
 function gardenBed(feature){
  const [a,b]=feature.bounds,left=Math.min(a[0],b[0]),right=Math.max(a[0],b[0]),bottom=Math.min(a[1],b[1]),top=Math.max(a[1],b[1]);
  polygon(featureRect(feature),'#7f9a67','#c5b399');
  const w=right-left,h=top-bottom;if(w<1||h<1)return;
  const columns=Math.max(1,Math.min(8,Math.floor(w/1.3))),rows=Math.max(1,Math.min(4,Math.floor(h/1.3)));
  for(let y=0;y<rows;y++)for(let x=0;x<columns;x++){
   const p=screen([left+w*(x+.5)/columns,bottom+h*(y+.5)/rows]),r=Math.max(.7,Math.min(3,scale*.52));
   ctx.fillStyle=(x+y)%4===0?'#d7a7a0':(x+y)%3===0?'#e4cf9a':'#6f965d';ctx.beginPath();ctx.ellipse(p[0],p[1],r,r*.65,0,0,Math.PI*2);ctx.fill();
  }
 }
 function bench(feature){
  const [a,b]=feature.bounds,left=Math.min(a[0],b[0]),right=Math.max(a[0],b[0]),bottom=Math.min(a[1],b[1]),top=Math.max(a[1],b[1]),corners=featureRect(feature);
  const center=featureCenter(feature),shadow=screen(center);ctx.fillStyle='#4e493d44';ctx.beginPath();ctx.ellipse(shadow[0]+scale*.35,shadow[1]+scale*.25,Math.max(1,(right-left)*scale*.42),Math.max(.6,(top-bottom)*scale*.35),0,0,Math.PI*2);ctx.fill();
  for(const q of [[left,bottom],[right,bottom],[left,top],[right,top]]){const foot=screen(q),seat=screen(q,.65);ctx.strokeStyle='#75634e';ctx.lineWidth=Math.max(.6,scale*.18);ctx.beginPath();ctx.moveTo(...foot);ctx.lineTo(...seat);ctx.stroke();}
  polygon(corners,'#ba8556','#795d44',.65);
  const backA=screen([left,top],1.1),backB=screen([right,top],1.1);ctx.strokeStyle='#8a6343';ctx.lineWidth=Math.max(.7,scale*.3);ctx.beginPath();ctx.moveTo(...backA);ctx.lineTo(...backB);ctx.stroke();
 }
 function marker(point,text,color){const p=screen(point);ctx.fillStyle=color;ctx.beginPath();ctx.arc(p[0],p[1],7,0,Math.PI*2);ctx.fill();ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.stroke();ctx.font='bold 12px system-ui';ctx.fillStyle='#263b40';ctx.fillText(text,p[0]+10,p[1]-7)}
 function routeAt(f){const lengths=route.slice(1).map((p,i)=>Math.hypot(p[0]-route[i][0],p[1]-route[i][1])),total=lengths.reduce((a,b)=>a+b,0);let d=total*f;for(let i=0;i<lengths.length;i++){if(d<=lengths[i]){const t=lengths[i]?d/lengths[i]:0;return [route[i][0]+(route[i+1][0]-route[i][0])*t,route[i][1]+(route[i+1][1]-route[i][1])*t]}d-=lengths[i]}return route[route.length-1]}
 function visibleBounds(){
  const points=[[-50,-50],[width+50,-50],[-50,height+50],[width+50,height+50]].map(([x,y])=>{
   const u=(x-width/2-pan[0])/scale,v=(y-height/2-pan[1])/scale;
   return [center[0]+u/(2*.8660254)-v,center[1]-u/(2*.8660254)-v];
  });
  // Include high facades and trees whose ground anchors lie outside the screen.
  return {l:Math.min(...points.map(p=>p[0]))-40,b:Math.min(...points.map(p=>p[1]))-40,r:Math.max(...points.map(p=>p[0]))+40,t:Math.max(...points.map(p=>p[1]))+40};
 }
 function render(){ctx.setTransform(dpr,0,0,dpr,0,0);ctx.clearRect(0,0,width,height);ctx.fillStyle='#dce8df';ctx.fillRect(0,0,width,height);if(outer)outer.draw(ctx,outer.query(visibleBounds()),{screen,polygon,textured,road,tree,scale});ctx.save();const clip=[[bounds.minX,bounds.minY],[bounds.maxX,bounds.minY],[bounds.maxX,bounds.maxY],[bounds.minX,bounds.maxY]];ctx.beginPath();clip.forEach((p,i)=>{const q=screen(p);if(i)ctx.lineTo(...q);else ctx.moveTo(...q)});ctx.closePath();ctx.clip();ctx.fillStyle='#e9dfcb';ctx.fill();
 const visible=sceneIndex.query(visibleBounds());
 const colors={mixed:'#e6d9c3',residential:'#e8decc',garden:'#cbd8b6',park:'#b9d2ae',campus:'#dfd4ba',riverfront:'#c4d9be',plaza:'#e5d9c6'};
 for(const parcel of visible.parcel){if(parcel.renderGround===false)continue;ctx.beginPath();for(const ring of parcel.rings){ring.forEach((p,i)=>{const q=screen(p);if(i)ctx.lineTo(...q);else ctx.moveTo(...q)});ctx.closePath()}ctx.fillStyle=colors[parcel.landUse]||'#e8dfcc';ctx.fill('evenodd');const grass=['garden','park','riverfront'].includes(parcel.landUse);textured(parcel.rings,grass?'grass':'paving',grass ? .42 : .30)}
 for(const water of visible.water){const poly=water.points||water;polygon(poly,'#88bdba');textured([poly],'water',.36)}for(const water of visible.stream)road(water,12,'#8dbfbe','water');
 for(const feature of visible.feature){if(feature.type==='pedestrian-path'&&feature.points)path(feature.points,'#d8c6a6',Math.max(1,(feature.widthMetres||2)*scale*.7));else if(feature.bounds?.length===2&&feature.type==='sports-court')court(feature);else if(feature.bounds?.length===2&&feature.type==='garden-bed')gardenBed(feature)}
 for(const rd of visible.road)road(rd.points,rd.width+3,'#e7e2da','paving');
 for(const rd of visible.road)road(rd.points,rd.width,rd.bridge?'#89959f':'#768897',null);
 drawRoadMarkings(visible.road);
 if(route.length>1)path(route,'#277fc4',Math.max(2,2*scale));
 let riderPoint,riderLabel,riderTier;
 if(liveState){riderPoint=liveState.rider;riderLabel='当前骑手 · '+liveState.vehicleTier+'档';riderTier=liveState.vehicleTier;}
 else {const f=Number(slider.value)/1000,p=routeAt(f),q=routeAt(Math.min(1,f+.001)),prev=routeAt(Math.max(0,f-.001));riderDirection=window.CountySampleRider.directionForVector(q[0]-prev[0],q[1]-prev[1],riderDirection);riderPoint=p;riderLabel='骑手示意';riderTier=1;}
 const objects=[...visible.building.map(v=>({kind:'building',value:v})),...visible.tree.map(v=>({kind:'tree',value:v})),...visible.feature.filter(v=>v.type==='bench'&&v.bounds?.length===2).map(v=>({kind:'bench',value:v})),{kind:'rider',value:riderPoint}];
 objects.sort((a,b)=>{const point=o=>o.kind==='rider'?o.value:o.kind==='tree'?o.value.groundAnchor:o.kind==='bench'?featureCenter(o.value):o.value.footprint.reduce((acc,p)=>[acc[0]+p[0]/o.value.footprint.length,acc[1]+p[1]/o.value.footprint.length],[0,0]);return ground(point(a))[1]-ground(point(b))[1]});
 for(const o of objects){if(o.kind==='tree')tree(o.value);else if(o.kind==='bench')bench(o.value);else if(o.kind==='rider'){if(scale>=2.5)drawRider(o.value,riderLabel,riderTier);}else building(o.value);}
 if(scale<2.5)marker(riderPoint,riderLabel,'#db6f28');
 if(liveState){for(const stop of liveState.stops)if(stop?.point)marker(stop.point,stop.name,'#d97937');}else for(const e of data.entrances)marker(e.groundAnchor,e.name,'#d97937');ctx.restore();}
 function resize(){const rect=view.getBoundingClientRect();width=rect.width;height=rect.height;dpr=window.devicePixelRatio||1;canvas.width=Math.round(width*dpr);canvas.height=Math.round(height*dpr);scale=Math.min(width/110,height/150);pan=[0,0];render()}
 window.addEventListener('message',event=>{if(!live||event.origin!==location.origin||event.source!==window.parent||event.data?.type!=='county-sample-live-v1')return;const state=event.data;if(!Array.isArray(state.rider)||state.rider.length!==2||!state.rider.every(Number.isFinite)||!Array.isArray(state.route)||!Array.isArray(state.stops))return;if(previousRider){const dx=state.rider[0]-previousRider[0],dy=state.rider[1]-previousRider[1];if(Math.hypot(dx,dy)>.001)riderDirection=window.CountySampleRider.directionForVector(dx,dy,riderDirection);}previousRider=state.rider.slice();liveState=state;route=state.route;const p=state.rider,inside=p[0]>=bounds.minX&&p[0]<=bounds.maxX&&p[1]>=bounds.minY&&p[1]<=bounds.maxY;percent.value=inside?'实时':'范围外';render();});
 document.getElementById('overview').addEventListener('click',()=>{const corners=[[displayBounds.minX,displayBounds.minY],[displayBounds.maxX,displayBounds.minY],[displayBounds.maxX,displayBounds.maxY],[displayBounds.minX,displayBounds.maxY]].map(ground),xs=corners.map(p=>p[0]),ys=corners.map(p=>p[1]),minX=Math.min(...xs),maxX=Math.max(...xs),minY=Math.min(...ys),maxY=Math.max(...ys);scale=Math.max(minScale,Math.min((width-30)/(maxX-minX),(height-30)/(maxY-minY)));pan=[-(minX+maxX)*scale/2,-(minY+maxY)*scale/2];render();});
 slider.addEventListener('input',()=>{percent.value=Math.round(Number(slider.value)/10)+'%';render()});document.getElementById('reset').addEventListener('click',resize);const snapshotGesture=()=>{const points=Array.from(touches.values());if(points.length===1)gesture={kind:'drag',x:points[0].x,y:points[0].y};else if(points.length===2){const [a,b]=points;gesture={kind:'pinch',distance:Math.max(1,Math.hypot(a.x-b.x,a.y-b.y)),midX:(a.x+b.x)/2,midY:(a.y+b.y)/2};}else gesture=null;};
 view.addEventListener('pointerdown',e=>{touches.set(e.pointerId,{x:e.clientX,y:e.clientY});view.setPointerCapture(e.pointerId);snapshotGesture()});
 view.addEventListener('pointermove',e=>{if(!touches.has(e.pointerId))return;touches.set(e.pointerId,{x:e.clientX,y:e.clientY});const points=Array.from(touches.values());
  if(gesture?.kind==='drag'&&points.length===1){pan[0]+=points[0].x-gesture.x;pan[1]+=points[0].y-gesture.y;gesture.x=points[0].x;gesture.y=points[0].y;render();}
  else if(gesture?.kind==='pinch'&&points.length===2){const [a,b]=points,d=Math.max(1,Math.hypot(a.x-b.x,a.y-b.y)),mx=(a.x+b.x)/2,my=(a.y+b.y)/2,rect=view.getBoundingClientRect(),ax=gesture.midX-rect.left-width/2,ay=gesture.midY-rect.top-height/2,old=scale;scale=Math.max(minScale,Math.min(12,scale*d/gesture.distance));pan[0]=(pan[0]-ax)*scale/old+ax+(mx-gesture.midX);pan[1]=(pan[1]-ay)*scale/old+ay+(my-gesture.midY);gesture={kind:'pinch',distance:d,midX:mx,midY:my};render();}
 });
 const endPointer=e=>{touches.delete(e.pointerId);snapshotGesture()};view.addEventListener('pointerup',endPointer);view.addEventListener('pointercancel',endPointer);
 view.addEventListener('wheel',e=>{e.preventDefault();scale=Math.max(minScale,Math.min(12,scale*(e.deltaY<0?1.12:1/1.12)));render()},{passive:false});window.addEventListener('resize',resize);resize();
})().catch(error=>{document.querySelector('header p').textContent='样板数据加载失败：'+error.message});
