import { Bounds, contains, expandBounds } from './CityExtent';
import { CityData, MapPOI } from './MapTypes';
import { countyMapId } from './CountySnapshot';
import { denseUrbanCatalog } from './UrbanCatalog';
import { buildDispatchAreas, PlaceArea } from './DispatchAreas';

const prepared=new WeakMap<CityData,CityData>();
/** Select the dense connected building cluster nearest the initial restaurant. */
function cityCore(data:CityData):Bounds {
  const start=data.nodes.find(n=>n.id===data.pois.find(p=>p.kind==='restaurant')?.node)||data.nodes[0];
  const cells=new Map<string,number>();
  for(const polygon of data.buildings){
    if(!polygon.length)continue;
    const x=Math.floor(polygon.reduce((s,p)=>s+p[0],0)/polygon.length/300),y=Math.floor(polygon.reduce((s,p)=>s+p[1],0)/polygon.length/300),key=`${x}/${y}`;
    cells.set(key,(cells.get(key)||0)+1);
  }
  const dense=Array.from(cells.keys()).filter(key=>cells.get(key)!>=10).map(key=>key.split('/').map(Number));
  if(!dense.length||!start){
    return {minX:Math.min(...data.nodes.map(n=>n.x)),maxX:Math.max(...data.nodes.map(n=>n.x)),minY:Math.min(...data.nodes.map(n=>n.y)),maxY:Math.max(...data.nodes.map(n=>n.y))};
  }
  dense.sort((a,b)=>Math.hypot((a[0]+.5)*300-start.x,(a[1]+.5)*300-start.y)-Math.hypot((b[0]+.5)*300-start.x,(b[1]+.5)*300-start.y));
  const todo=[dense[0]],seen=new Set([dense[0].join('/')]);
  for(let i=0;i<todo.length;i++){
    const [x,y]=todo[i];
    for(const p of [[x-1,y],[x+1,y],[x,y-1],[x,y+1]]){const key=p.join('/');if(!seen.has(key)&&(cells.get(key)||0)>=10){seen.add(key);todo.push(p);}}
  }
  const minX=Math.min(...todo.map(p=>p[0]))*300,maxX=(Math.max(...todo.map(p=>p[0]))+1)*300;
  let minY=Math.min(...todo.map(p=>p[1]))*300,maxY=(Math.max(...todo.map(p=>p[1]))+1)*300;
  // Include the immediate urban approaches, so tall phone viewports still fit at 100 m.
  const extra=Math.max(0,2100-(maxY-minY))/2;minY-=extra;maxY+=extra;
  return {minX,maxX,minY,maxY};
}
/** Nodes reachable both ways from the initial restaurant on roads inside the core. */
function cityComponent(data:CityData,bounds:Bounds):Set<string> {
  const allowed=new Set(data.nodes.filter(n=>contains(bounds,[n.x,n.y])).map(n=>n.id));
  const forward=new Map<string,string[]>(),reverse=new Map<string,string[]>();
  const edge=(a:string,b:string)=>{if(!forward.has(a))forward.set(a,[]);forward.get(a)!.push(b);if(!reverse.has(b))reverse.set(b,[]);reverse.get(b)!.push(a);};
  for(const r of data.roads)if(r.speed>0)for(let i=1;i<r.nodes.length;i++){
    const a=r.nodes[i-1],b=r.nodes[i];if(!allowed.has(a)||!allowed.has(b))continue;
    if(r.direction!==-1)edge(a,b);if(r.direction!==1)edge(b,a);
  }
  const start=data.pois.find(p=>p.kind==='restaurant')?.node;
  const visit=(graph:Map<string,string[]>):Set<string>=>{const seen=new Set<string>(),todo=start&&allowed.has(start)?[start]:[];for(let i=0;i<todo.length;i++){const n=todo[i];if(seen.has(n))continue;seen.add(n);todo.push(...(graph.get(n)||[]).filter(v=>!seen.has(v)));}return seen;};
  const a=visit(forward),b=visit(reverse);return new Set(Array.from(a).filter(id=>b.has(id)));
}
function legacyCity(data:CityData):CityData {
  const playBounds=expandBounds(cityCore(data),.1),component=cityComponent(data,playBounds);
  const points=new Map(data.nodes.map(n=>[n.id,n])),pois:MapPOI[]=data.pois.map((p,i)=>({...p,address:p.address||`旧街${i+1}号`})),occupied=new Set(pois.map(p=>p.node)),names=new Set(pois.map(p=>p.name));
  const eligible=data.nodes.filter(n=>component.has(n.id)&&!occupied.has(n.id));
  // Round-robin 300m cells spreads addresses across the actual built-up roads.
  const cells=new Map<string,typeof eligible>();
  for(const n of eligible){const key=`${Math.floor(n.x/300)}/${Math.floor(n.y/300)}`;if(!cells.has(key))cells.set(key,[]);cells.get(key)!.push(n);}
  const ordered=Array.from(cells.entries()).sort((a,b)=>a[0].localeCompare(b[0])).map(([,nodes])=>nodes.sort((a,b)=>a.id.localeCompare(b.id)));
  const pool:typeof eligible=[];for(let i=0;ordered.some(nodes=>i<nodes.length);i++)for(const nodes of ordered)if(nodes[i])pool.push(nodes[i]);
  const cityPOIs=pois.filter(p=>{const n=points.get(p.node);return n&&contains(playBounds,[n.x,n.y])&&component.has(p.node);});
  let merchants=cityPOIs.filter(p=>p.kind==='restaurant').length,customers=cityPOIs.length-merchants,cursor=0;
  const streets=['榕荫路','晴川街','文昌巷','青禾路','云桥街','杏花巷','书院街','春和路'];
  const shops=['饭铺','面馆','饺子馆','茶点铺','小灶','轻食屋','寿司店','烘焙坊'];
  while(cursor<pool.length&&(merchants<40||customers<120)){
    const n=pool[cursor++],merchant=merchants<40&&(customers>=120||cursor%4===1),serial=merchant?++merchants:++customers;
    const street=streets[(cursor-1)%streets.length],address=`${street}${100+cursor}号`,base=merchant?`${street}${shops[(serial-1)%shops.length]}·${serial}店`:`${street}邻里·${serial}号楼`;
    let name=base;while(names.has(name))name+='新';names.add(name);
    pois.push({name,node:n.id,kind:merchant?'restaurant':serial%5===0?'office':'home',address});
  }
  const result:CityData={...data,pois,playBounds,legacyMapIds:[countyMapId(data)],placeCatalogVersion:1};
  return result;
}

function localityCity(data:CityData):CityData {
  if(data.placeCatalogVersion===2)return data;
  // Rebuild the previous catalog first: its indices and map identity are saved in v3 games.
  const previous=data.placeCatalogVersion===1?data:legacyCity(data),playBounds=previous.playBounds!;
  const margin=Math.min(150,(playBounds.maxX-playBounds.minX)/4,(playBounds.maxY-playBounds.minY)/4);
  const dispatchBounds={minX:playBounds.minX+margin,maxX:playBounds.maxX-margin,minY:playBounds.minY+margin,maxY:playBounds.maxY-margin};
  const component=cityComponent(previous,playBounds),points=new Map(previous.nodes.map(n=>[n.id,n]));
  const pois=previous.pois.slice(),occupied=new Set(pois.map(p=>p.node)),names=new Set(pois.map(p=>p.name));
  const operating=pois.filter(p=>{const n=points.get(p.node)!;return component.has(p.node)&&contains(dispatchBounds,[n.x,n.y]);});
  let merchants=operating.filter(p=>p.kind==='restaurant').length,customers=operating.length-merchants;
  const cells=new Map<string,typeof previous.nodes>();
  for(const n of previous.nodes)if(component.has(n.id)&&!occupied.has(n.id)&&contains(dispatchBounds,[n.x,n.y])){
    const key=`${Math.floor(n.x/300)}/${Math.floor(n.y/300)}`;if(!cells.has(key))cells.set(key,[]);cells.get(key)!.push(n);
  }
  const ordered=Array.from(cells.entries()).sort((a,b)=>a[0].localeCompare(b[0])).map(([,nodes])=>nodes.sort((a,b)=>a.id.localeCompare(b.id)));
  const pool:typeof previous.nodes=[];for(let i=0;ordered.some(nodes=>i<nodes.length);i++)for(const nodes of ordered)if(nodes[i])pool.push(nodes[i]);
  let cursor=0;
  while(cursor<pool.length&&(merchants<40||customers<120)){
    const n=pool[cursor++],merchant=merchants<40&&(customers>=120||cursor%4===1),serial=merchant?++merchants:++customers;
    let name=merchant?`城中饭铺·${serial}店`:`城中邻里·${serial}号楼`;while(names.has(name))name+='新';names.add(name);
    pois.push({name,node:n.id,kind:merchant?'restaurant':serial%5===0?'office':'home',address:`城中街${500+cursor}号`});
  }
  const result:CityData={...previous,pois,dispatchBounds,placeCatalogVersion:2,legacyMapIds:[...(previous.legacyMapIds||[]),countyMapId(previous)]};
  return result;
}

export function preparePreviousCity(data:CityData):CityData {
  if(data.placeCatalogVersion===3)return data;
  const cached=prepared.get(data);if(cached)return cached;
  const previous=localityCity(data),playBounds=previous.playBounds!;
  const margin=Math.min(450,(playBounds.maxX-playBounds.minX)/4,(playBounds.maxY-playBounds.minY)/4);
  const dispatchBounds={minX:playBounds.minX+margin,maxX:playBounds.maxX-margin,minY:playBounds.minY+margin,maxY:playBounds.maxY-margin};
  const {zones:dispatchAreas,urbanBounds}=buildDispatchAreas({...previous,dispatchBounds});
  const component=cityComponent(previous,playBounds),points=new Map(previous.nodes.map(n=>[n.id,n]));
  const pois=previous.pois.slice(),occupied=new Set(pois.map(p=>p.node)),names=new Set(pois.map(p=>p.name)),operatingPOIs:number[]=[];
  const safe=(node:string)=>{const n=points.get(node)!;return component.has(node)&&contains(dispatchBounds,[n.x,n.y]);};
  const areas:PlaceArea[]=['urban','suburb','remote'];
  for(const area of areas){
    const targets=area==='urban'?[20,60]:area==='suburb'?[12,36]:[8,24];
    const eligible=previous.nodes.filter(n=>safe(n.id)&&dispatchAreas[n.id]===area&&!occupied.has(n.id));
    const cells=new Map<string,typeof eligible>();
    for(const n of eligible){const key=`${Math.floor(n.x/300)}/${Math.floor(n.y/300)}`;if(!cells.has(key))cells.set(key,[]);cells.get(key)!.push(n);}
    const ordered=Array.from(cells.entries()).sort((a,b)=>a[0].localeCompare(b[0])).map(([,nodes])=>nodes.sort((a,b)=>a.id.localeCompare(b.id)));
    const pool:typeof eligible=[];for(let i=0;ordered.some(nodes=>i<nodes.length);i++)for(const nodes of ordered)if(nodes[i])pool.push(nodes[i]);
    let cursor=0;
    for(const merchant of [true,false]){
      const wanted=targets[merchant?0:1],existing=pois.map((p,i)=>({p,i})).filter(v=>(v.p.kind==='restaurant')===merchant&&safe(v.p.node)&&dispatchAreas[v.p.node]===area).map(v=>v.i);
      operatingPOIs.push(...existing.slice(0,wanted));
      for(let count=Math.min(existing.length,wanted);count<wanted&&cursor<pool.length;count++){
        const n=pool[cursor++],prefix=area==='urban'?'城区':area==='suburb'?'城郊':'远郊';
        let name=merchant?`${prefix}小店·${pois.length+1}`:`${prefix}住址·${pois.length+1}`;while(names.has(name))name+='新';names.add(name);
        operatingPOIs.push(pois.length);pois.push({name,node:n.id,kind:merchant?'restaurant':'home',address:`${prefix}街${1000+pois.length}号`});occupied.add(n.id);
      }
    }
  }
  const result:CityData={...previous,pois,dispatchBounds,dispatchAreas,urbanBounds,operatingPOIs,placeCatalogVersion:3,legacyMapIds:[...(previous.legacyMapIds||[]),countyMapId(previous)]};
  prepared.set(data,result);return result;
}

const focused=new WeakMap<CityData,CityData>();
export function prepareCity(data:CityData):CityData {
 if(data.placeCatalogVersion===4)return data;const cached=focused.get(data);if(cached)return cached;
 const previous=preparePreviousCity(data),pool=denseUrbanCatalog(previous,cityComponent(previous,previous.playBounds!));
 const result:CityData={...previous,...pool,placeCatalogVersion:4,legacyMapIds:[...(previous.legacyMapIds||[]),countyMapId(previous)]};focused.set(data,result);return result;
}
