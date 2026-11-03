/* World-space index for the independent sample viewer; no gameplay data is modified. */
class CountySceneIndex {
 constructor(scene,cellSize=256){
  this.size=cellSize;this.cells=new Map();
  const index=scene.tileIndex;this.native=index&&index.tileSizeMetres>0&&Array.isArray(index.objects)&&index.tiles?{size:index.tileSizeMetres,origin:index.origin||[0,0],tiles:index.tiles,objects:new Map(index.objects.map(entry=>[entry.key,entry])),scene}:null;
  const add=(kind,value,points,padding=0)=>{
   if(!points?.length)return;let l=Infinity,b=Infinity,r=-Infinity,t=-Infinity;
   for(const p of points){if(!Array.isArray(p)||!Number.isFinite(p[0])||!Number.isFinite(p[1]))continue;l=Math.min(l,p[0]);r=Math.max(r,p[0]);b=Math.min(b,p[1]);t=Math.max(t,p[1]);}
   if(!Number.isFinite(l))return;const entry={kind,value,l:l-padding,b:b-padding,r:r+padding,t:t+padding};
   for(let x=Math.floor(entry.l/this.size);x<=Math.floor(entry.r/this.size);x++)for(let y=Math.floor(entry.b/this.size);y<=Math.floor(entry.t/this.size);y++){
    const key=x+','+y,cell=this.cells.get(key);if(cell)cell.push(entry);else this.cells.set(key,[entry]);
   }
  };
  if(!this.native){
   for(const value of scene.parcels||[])if(value.renderGround!==false)add('parcel',value,(value.rings||[]).flat());
   for(const value of scene.sourceWaterPolygons||[])add('water',value,value.points||value);
  }
  for(const value of scene.sourceWaterways||[])for(let i=1;i<value.length;i++)add('stream',[value[i-1],value[i]],[value[i-1],value[i]],12);
  for(const value of scene.sourceRoads||[])for(let i=1;i<value.points.length;i++)add('road',{width:value.width,bridge:value.bridge,nodeA:value.nodes?.[i-1],nodeB:value.nodes?.[i],points:[value.points[i-1],value.points[i]]},[value.points[i-1],value.points[i]],(value.width||0)/2+3);
  if(!this.native){
   for(const value of scene.sourceBuildings||[])add('building',value,value.footprint,2);
   for(const value of scene.addedBuildings||[])add('building',value,value.footprint,2);
   for(const value of scene.trees||[])add('tree',value,[value.groundAnchor],(value.crownDiameterMetres||6)/2);
   for(const value of scene.sceneFeatures||[])add('feature',value,value.points||value.bounds||[],(value.widthMetres||0)/2);
  }
 }
 query(bounds){
  const found=new Set();for(let x=Math.floor(bounds.l/this.size);x<=Math.floor(bounds.r/this.size);x++)for(let y=Math.floor(bounds.b/this.size);y<=Math.floor(bounds.t/this.size);y++)for(const e of this.cells.get(x+','+y)||[])if(e.r>=bounds.l&&e.l<=bounds.r&&e.t>=bounds.b&&e.b<=bounds.t)found.add(e);
  const groups={parcel:[],water:[],stream:[],road:[],building:[],tree:[],feature:[]};for(const entry of found)groups[entry.kind].push(entry.value);
  if(this.native){
   const n=this.native,keys=new Set(),mapping={parcels:'parcel',sourceWaterPolygons:'water',sourceBuildings:'building',addedBuildings:'building',trees:'tree',sceneFeatures:'feature'};
   for(let x=Math.floor((bounds.l-n.origin[0])/n.size);x<=Math.floor((bounds.r-n.origin[0])/n.size);x++)for(let y=Math.floor((bounds.b-n.origin[1])/n.size);y<=Math.floor((bounds.t-n.origin[1])/n.size);y++){
    const tile=n.tiles[x+':'+y];if(!tile)continue;for(const collection of Object.keys(mapping))for(const key of tile[collection]||[])keys.add(key);
   }
   for(const key of keys){const record=n.objects.get(key);if(!record||record.excludedFromProduction||!mapping[record.collection])continue;const b=record.bounds;
    if(b&&(b.maxX<bounds.l||b.minX>bounds.r||b.maxY<bounds.b||b.minY>bounds.t))continue;
    const value=n.scene[record.collection]?.[record.index];if(value&&!value.excludedFromProduction&&!(record.collection==='parcels'&&value.renderGround===false))groups[mapping[record.collection]].push(value);
   }
  }return groups;
 }
}
window.CountySceneIndex=CountySceneIndex;
