/* Visual-only facades from existing ground footprints; no change to collision or road data. */
window.CountyStreetFacades={
 draw(ctx,obj,api){
  const pts=obj.footprint;if(!pts||pts.length<3)return;const {screen,polygon,textured,scale,facadeImages}=api,h=Math.max(3,Math.min(25,obj.heightMetres||9));
  const ring=pts.length>1&&pts[0][0]===pts[pts.length-1][0]&&pts[0][1]===pts[pts.length-1][1]?pts.slice(0,-1):pts.slice();if(ring.length<3)return;
  const area=ring.reduce((sum,p,i)=>{const q=ring[(i+1)%ring.length];return sum+p[0]*q[1]-q[0]*p[1]},0),winding=area>=0?1:-1;
  const faceRect=(a,b,t0,t1,z0,z1,fill,stroke)=>{const p=(t,z)=>screen([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t],z),v=[p(t0,z0),p(t1,z0),p(t1,z1),p(t0,z1)];ctx.beginPath();ctx.moveTo(...v[0]);for(const q of v.slice(1))ctx.lineTo(...q);ctx.closePath();ctx.fillStyle=fill;ctx.fill();if(stroke){ctx.strokeStyle=stroke;ctx.lineWidth=Math.max(.5,scale*.10);ctx.stroke();}};
  const bayImage=(a,b,t0,t1,z0,z1,image)=>{
   if(!image)return;const at=(t,z)=>screen([a[0]+(b[0]-a[0])*t,a[1]+(b[1]-a[1])*t],z),tl=at(t0,z1),tr=at(t1,z1),bl=at(t0,z0),br=at(t1,z0);
   ctx.save();ctx.beginPath();ctx.moveTo(...tl);ctx.lineTo(...tr);ctx.lineTo(...br);ctx.lineTo(...bl);ctx.closePath();ctx.clip();
   ctx.transform((tr[0]-tl[0])/image.naturalWidth,(tr[1]-tl[1])/image.naturalWidth,(bl[0]-tl[0])/image.naturalHeight,(bl[1]-tl[1])/image.naturalHeight,tl[0],tl[1]);
   ctx.drawImage(image,0,0);ctx.restore();
  };
  const shadow=ring.map(p=>[p[0]+1.5,p[1]-2.8]);polygon(shadow,'#53657535');
  for(let i=0;i<ring.length;i++){
   const a=ring[i],b=ring[(i+1)%ring.length],dx=b[0]-a[0],dy=b[1]-a[1],length=Math.hypot(dx,dy);if(length<.1)continue;
   // Viewer is on the screen-bottom side of the ground plane; omit rear-facing walls.
   const facing=winding*(dx-dy);if(facing<=0)continue;
   const warm=(dx-dy)*winding>0&&dx*winding>0;
   faceRect(a,b,0,1,0,h,warm?'#f4e9d8':'#dce3e3','#bac4c3');
   if(scale<1||length<4)continue;
   const hint=obj.streetFacingHint?.normalToStreet,normalX=winding*dy/length,normalY=-winding*dx/length;
   const facesStreet=!hint||(normalX*hint[0]+normalY*hint[1])>.3;
   const storefront=facesStreet&&h>=6&&length>=9,groundTop=Math.min(h*.38,3.4),bayCount=Math.min(18,Math.max(1,Math.round(length/3.6)));
   if(storefront){
    for(let k=0;k<bayCount;k++){const l=(k+.08)/bayCount,r=(k+.92)/bayCount;
     faceRect(a,b,l,r,.25,groundTop-.18,k%3===0?'#324e56':'#507582','#304d55');
     if(k===Math.floor(bayCount/2)&&facadeImages.store)bayImage(a,b,l,r,.25,groundTop-.18,facadeImages.store);
     if(k!==Math.floor(bayCount/2)||!facadeImages.store)faceRect(a,b,l+.05/bayCount,r-.05/bayCount,.35,Math.min(groundTop-0.35,1.3),k%3===1?'#d1a76d':'#789b9f');
     faceRect(a,b,(l+r)/2-.015/bayCount,(l+r)/2+.015/bayCount,.25,groundTop-.18,'#e8dfca');
    }
    if((Math.abs(Math.floor(a[0]*11+a[1]*7))+i)%3===0){
     faceRect(a,b,.08,.92,groundTop-.05,groundTop+.5,'#e98232','#ba5c2b');
     faceRect(a,b,.08,.92,groundTop+.5,groundTop+.7,'#f5a451');
    }
   }
   const first=storefront?groundTop+.5:.8,floorHeight=3,rows=Math.max(0,Math.floor((h-first)/floorHeight));
   for(let row=0;row<rows;row++){
    const base=first+row*floorHeight,top=Math.min(h-.4,base+2.35);if(top<=base)continue;
    faceRect(a,b,0,1,Math.max(0,base-.16),base,'#b7c7ca');
    for(let k=0;k<bayCount;k++){const l=(k+.14)/bayCount,r=(k+.86)/bayCount;
     faceRect(a,b,l,r,base+.2,top,'#6f989e','#eaf1ec');
     if(facadeImages.upper)bayImage(a,b,l,r,base+.2,top,facadeImages.upper);
     faceRect(a,b,l+.04/bayCount,r-.04/bayCount,base+.25,base+.38,'#bed1ca');
     if(k%3===0)faceRect(a,b,(k+.03)/bayCount,(k+.09)/bayCount,base,top+.1,'#f8f2e6');
    }
   }
  }
  polygon(ring,'#e7e9e4','#aab7b5',h);textured([ring],'roof',.18,h);
  // Parapet edges are anchored to the original footprint and never alter its data.
  for(let i=0;i<ring.length;i++){
   const a=ring[i],b=ring[(i+1)%ring.length],dx=b[0]-a[0],dy=b[1]-a[1];if(winding*(dx-dy)<=0)continue;
   faceRect(a,b,0,1,h,h+.65,'#f9f6ee','#c2ccca');
  }
  // Rooftop accessories must fit entirely within the original footprint.
  const xs=ring.map(p=>p[0]),ys=ring.map(p=>p[1]),cx=(Math.min(...xs)+Math.max(...xs))/2,cy=(Math.min(...ys)+Math.max(...ys))/2;
  const inside=p=>{let result=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[i],b=ring[j];if((a[1]>p[1])!==(b[1]>p[1])&&p[0]<(b[0]-a[0])*(p[1]-a[1])/(b[1]-a[1])+a[0])result=!result;}return result;};
  const distance=(p,a,b)=>{const dx=b[0]-a[0],dy=b[1]-a[1],d=dx*dx+dy*dy,t=d?Math.max(0,Math.min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/d)):0;return Math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)};
  const equipment=[[cx-1.1,cy-.9],[cx+1.1,cy-.9],[cx+1.1,cy+.9],[cx-1.1,cy+.9]];
  const cross=(a,b,c)=>(b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0]);
  const intersects=(a,b,c,d)=>cross(a,b,c)*cross(a,b,d)<=0&&cross(c,d,a)*cross(c,d,b)<=0;
  const edgesClear=equipment.every((a,i)=>ring.every((b,j)=>!intersects(a,equipment[(i+1)%4],b,ring[(j+1)%ring.length])));
  if(scale>=1.5&&edgesClear&&equipment.every(p=>inside(p)&&ring.every((a,i)=>distance(p,a,ring[(i+1)%ring.length])>.8))){
   polygon(equipment,'#a6b4b6',null,h+.15);const top=equipment.map(p=>screen(p,h+1.3)),base=equipment.map(p=>screen(p,h));
   for(let i=0;i<4;i++){ctx.beginPath();ctx.moveTo(...base[i]);ctx.lineTo(...base[(i+1)%4]);ctx.lineTo(...top[(i+1)%4]);ctx.lineTo(...top[i]);ctx.closePath();ctx.fillStyle=i%2?'#b6c5c6':'#d8e0dd';ctx.fill();}
   polygon(equipment,'#f9f8f1','#bbc8c8',h+1.3);
  }
 }
};
