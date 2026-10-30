import { CityData, MapNode, MapPOI } from './MapTypes';
import { contains } from './CityExtent';

/** Rebuild only the operating urban pool; historical POI indices remain immutable. */
export function denseUrbanCatalog(previous:CityData,component:Set<string>):{pois:MapPOI[];operatingPOIs:number[]} {
 const pois=previous.pois.slice(),points=new Map(previous.nodes.map(n=>[n.id,n]));
 const cells=new Map<string,{weight:number;x:number;y:number;nodes:MapNode[]}>();
 const key=(x:number,y:number)=>`${Math.floor(x/300)}/${Math.floor(y/300)}`;
 for(const polygon of previous.buildings){if(!polygon.length)continue;const x=polygon.reduce((s,p)=>s+p[0],0)/polygon.length,y=polygon.reduce((s,p)=>s+p[1],0)/polygon.length,k=key(x,y);const c=cells.get(k)||{weight:0,x:0,y:0,nodes:[]};c.weight++;c.x+=x;c.y+=y;cells.set(k,c);}
 for(const n of previous.nodes)if(component.has(n.id)&&contains(previous.dispatchBounds!,[n.x,n.y])&&previous.dispatchAreas![n.id]==='urban'&&n.y>=-900&&n.y<=600){const c=cells.get(key(n.x,n.y));if(c)c.nodes.push(n);}
 const selected:MapNode[]=[],merchants:MapNode[]=[],urban:number[]=[];
 const oldByNode=new Map<string,number>();pois.forEach((p,i)=>{if(!oldByNode.has(p.node))oldByNode.set(p.node,i);});
 const distance=(a:MapNode,b:MapNode)=>Math.hypot(a.x-b.x,a.y-b.y);
 for(const east of [true,false]){
  const groups=Array.from(cells.entries()).map(([id,c])=>({id,...c,nodes:c.nodes.filter(n=>east?n.x>=-2100&&n.x<=-1020:n.x>=-4080&&n.x< -2100)})).filter(c=>c.nodes.length).sort((a,b)=>a.id.localeCompare(b.id));
  // Four-neighbour street blocks receive largest-remainder shares by building weight.
  const blocks:typeof groups[]=[];const seen=new Set<string>();
  for(const seed of groups){if(seen.has(seed.id))continue;const block=[seed];seen.add(seed.id);for(let i=0;i<block.length;i++){const [x,y]=block[i].id.split('/').map(Number);for(const k of [`${x-1}/${y}`,`${x+1}/${y}`,`${x}/${y-1}`,`${x}/${y+1}`]){const c=groups.find(v=>v.id===k);if(c&&!seen.has(k)){seen.add(k);block.push(c);}}}blocks.push(block);}
  const shares=(weights:number[],total:number)=>{const sum=weights.reduce((a,b)=>a+b,0),raw=weights.map(w=>w/sum*total),out=raw.map(Math.floor);const order=raw.map((v,i)=>({i,f:v-out[i]})).sort((a,b)=>b.f-a.f||a.i-b.i);for(let left=total-out.reduce((a,b)=>a+b,0),i=0;left>0;left--,i++)out[order[i].i]++;return out;};
  for(const merchant of [true,false]){
   const target=east?(merchant?42:126):(merchant?18:54),blockShares=shares(blocks.map(b=>b.reduce((s,c)=>s+c.weight,0)),target);let count=0;
   const pick=(c:typeof groups[number]):boolean=>{
    const eligible=c.nodes.filter(n=>!selected.some(p=>distance(n,p)<35)&&(!merchant||!merchants.some(p=>distance(n,p)<70))).filter(n=>{const old=oldByNode.get(n.id);return old===undefined||(pois[old].kind==='restaurant')===merchant;});
    if(!eligible.length)return false;
    const used=selected.filter(n=>key(n.x,n.y)===c.id),cx=c.x/c.weight,cy=c.y/c.weight;
    eligible.sort((a,b)=>{const score=(n:MapNode)=>used.length?Math.min(...used.map(p=>distance(n,p))):-Math.hypot(n.x-cx,n.y-cy);return score(b)-score(a)||a.x-b.x||a.y-b.y||a.id.localeCompare(b.id);});
    const n=eligible[0];selected.push(n);if(merchant)merchants.push(n);let index=oldByNode.get(n.id);
    if(index===undefined){index=pois.length;pois.push({node:n.id,kind:merchant?'restaurant':'home',name:`${east?'东城':'西街'}${merchant?'食铺':'住址'}·${index+1}`,address:`${east?'东城':'西街'}密集街区${index+1}号`});oldByNode.set(n.id,index);}
    urban.push(index);count++;return true;
   };
   blocks.forEach((block,i)=>{const quotas=shares(block.map(c=>c.weight),blockShares[i]);block.forEach((c,j)=>{for(let k=0;k<quotas[j];k++)if(!pick(c))break;});while(count<blockShares.slice(0,i+1).reduce((a,b)=>a+b,0)){let added=false;for(const c of block.slice().sort((a,b)=>b.weight-a.weight||a.id.localeCompare(b.id))){if(pick(c)){added=true;break;}}if(!added)break;}});
   while(count<target){let added=false;for(const c of groups.slice().sort((a,b)=>b.weight-a.weight||a.id.localeCompare(b.id))){if(pick(c)){added=true;break;}}if(!added)throw new Error(`Dense catalog capacity insufficient: ${east?'east':'west'} ${merchant?'merchant':'customer'} ${count}/${target}`);}
  }
 }
 const nonurban=(previous.operatingPOIs||[]).filter(i=>previous.dispatchAreas![pois[i].node]!=='urban');
 return {pois,operatingPOIs:urban.concat(nonurban)};
}
