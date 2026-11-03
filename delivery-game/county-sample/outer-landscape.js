/* County outer scenery only; all geometry is clipped outside the business bounds. */
class CountyOuterLandscape {
 constructor(data){
  this.data=data;this.tiles=new Map(data.tiles.map(tile=>[tile.key,tile]));this.waterCells=new Map();this.size=data.tileSizeMetres;
  const add=(kind,points,pad)=>{
   if(!points?.length)return;let l=Infinity,b=Infinity,r=-Infinity,t=-Infinity;
   for(const p of points){l=Math.min(l,p[0]);r=Math.max(r,p[0]);b=Math.min(b,p[1]);t=Math.max(t,p[1]);}
   const entry={kind,points,l:l-pad,b:b-pad,r:r+pad,t:t+pad};
   for(let x=Math.floor(entry.l/this.size);x<=Math.floor(entry.r/this.size);x++)for(let y=Math.floor(entry.b/this.size);y<=Math.floor(entry.t/this.size);y++){
    const key=x+':'+y,cell=this.waterCells.get(key);if(cell)cell.push(entry);else this.waterCells.set(key,[entry]);
   }
  };
  for(const p of data.sourceWaterPolygons)add('water',p,0);
  for(const p of data.sourceWaterSegments)add('stream',p,data.waterVisualWidthMetres/2);
 }
 query(bounds){
  const tiles=[],water=new Set();for(let x=Math.floor(bounds.l/this.size);x<=Math.floor(bounds.r/this.size);x++)for(let y=Math.floor(bounds.b/this.size);y<=Math.floor(bounds.t/this.size);y++){
   const key=x+':'+y,tile=this.tiles.get(key);if(tile)tiles.push(tile);
   for(const e of this.waterCells.get(key)||[])if(e.r>=bounds.l&&e.l<=bounds.r&&e.t>=bounds.b&&e.b<=bounds.t)water.add(e);
  }return {tiles,water:Array.from(water)};
 }
 draw(ctx,visible,api){
  const {screen,polygon,textured,road,tree,scale}=api,{displayBounds:red,businessBounds:blue}=this.data;
  const rectangle=b=>[[b.minX,b.minY],[b.maxX,b.minY],[b.maxX,b.maxY],[b.minX,b.maxY]];
  ctx.save();ctx.beginPath();for(const ring of [rectangle(red),rectangle(blue)]){ring.forEach((p,i)=>{const q=screen(p);if(i)ctx.lineTo(...q);else ctx.moveTo(...q)});ctx.closePath();}ctx.clip('evenodd');
  const colors={north:'#b6c9a4',east:'#c1d0ad',west:'#c9d7b6',south:'#d6ddbd'};
  for(const tile of visible.tiles){
   const b=tile.bounds,shape=rectangle(b);polygon(shape,colors[tile.zone]);textured([shape],'grass',.22);
   // Gentle, fixed world-space meadow bands provide terrain structure without new paths.
   const dx=b.maxX-b.minX,dy=b.maxY-b.minY,seed=tile.groundPatternSeed%19/100;
   polygon([[b.minX+dx*.08,b.minY+dy*(.24+seed)],[b.minX+dx*.65,b.minY+dy*(.18+seed)],[b.minX+dx*.94,b.minY+dy*(.32+seed)],[b.minX+dx*.36,b.minY+dy*(.38+seed)]],tile.zone==='south'?'#ccd7b1':'#b7caa7');
  }
  for(const tile of visible.tiles)for(const hill of tile.hills){
   const [x,y]=hill.center,r=hill.radiusMetres,h=hill.heightMetres,base=[[x-r,y-r*.45],[x-r*.5,y+r*.45],[x+r*.4,y+r*.5],[x+r,y-r*.3]],peak=screen([x,y],h),a=screen(base[0]),b=screen(base[1]),c=screen(base[2]),d=screen(base[3]);
   ctx.beginPath();ctx.moveTo(...a);ctx.quadraticCurveTo((a[0]+peak[0])/2,peak[1]+h*scale*.3,...peak);ctx.quadraticCurveTo((c[0]+peak[0])/2,peak[1]+h*scale*.28,...c);ctx.lineTo(...d);ctx.closePath();ctx.fillStyle='#9eb797';ctx.fill();
   ctx.beginPath();ctx.moveTo(...a);ctx.lineTo(...b);ctx.lineTo(...peak);ctx.lineTo(...d);ctx.closePath();ctx.fillStyle='#b6c9a6';ctx.fill();
  }
  for(const entry of visible.water){if(entry.kind==='water'){polygon(entry.points,'#8dbfbe');textured([entry.points],'water',.36);}else road(entry.points,this.data.waterVisualWidthMetres,'#8dbfbe','water');}
  if(scale>=.28){const trees=visible.tiles.flatMap(tile=>tile.trees);trees.sort((a,b)=>screen(a.groundAnchor)[1]-screen(b.groundAnchor)[1]);for(const value of trees)tree(value);}
  ctx.restore();
 }
}
window.CountyOuterLandscape=CountyOuterLandscape;
