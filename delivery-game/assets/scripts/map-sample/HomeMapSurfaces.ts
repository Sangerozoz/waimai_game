import { Color, Graphics, isValid, Mask, Node, resources, Sprite, SpriteFrame, Texture2D, UITransform } from 'cc';
import { HomeMapArt, Polygon, Segment } from './HomeMapArt';
import { item } from './SampleUI';

const BLOCK=96;
const cache=new Map<string,Promise<SpriteFrame>>();
function texture(name:string):Promise<SpriteFrame>{
 const found=cache.get(name);if(found)return found;
 const pending=new Promise<SpriteFrame>((resolve,reject)=>resources.load('map-sample/anime/home-map-20261101/'+name+'/texture',Texture2D,(error,asset)=>{
  if(error){reject(error);return;}const frame=new SpriteFrame();frame.texture=asset;frame.addRef();resolve(frame);
 }));
 cache.set(name,pending);pending.catch(()=>{if(cache.get(name)===pending)cache.delete(name);});return pending;
}
/** World-aligned blocks use tiled frame UVs, avoiding NPOT texture wrap. */
export class HomeMapSurfaces {
 readonly ground:Node;
 readonly roofs:Node;
 readonly node:Node;
 private readonly blocks=new Map<string,Node[]>();
 constructor(parent:Node,private readonly art:HomeMapArt){
  this.ground=item(parent,'GroundMaterials');this.roofs=item(parent,'RoofMaterials');this.node=item(parent,'StreetMaterials');
 }
 sync(left:number,bottom:number,right:number,top:number,scale:number):void{
  const wanted=new Set<string>();
  if(scale>=.8){
   const pad=20;
   for(let x=Math.floor((left-pad)/BLOCK);x<=Math.floor((right+pad)/BLOCK);x++)for(let y=Math.floor((bottom-pad)/BLOCK);y<=Math.floor((top+pad)/BLOCK);y++){
    const key=x+'/'+y;wanted.add(key);if(this.blocks.has(key))continue;
    const cx=(x+.5)*BLOCK,cy=(y+.5)*BLOCK,l=x*BLOCK,b=y*BLOCK,r=l+BLOCK,t=b+BLOCK;
    const roads=this.art.roadSegments(l,b,r,t),area=this.art.areaGeometry(l,b,r,t),parts:Node[]=[];
    if(area.grass.length||area.water.length||area.streams.length){
     const block=item(this.ground,'Ground-'+key,cx,cy,BLOCK,BLOCK);parts.push(block);
     if(area.grass.length)this.layer(block,[],area.grass,cx,cy,'HG03-grass',8,0,new Color(200,207,173,255));
     if(area.water.length||area.streams.length)this.layer(block,area.streams,area.water,cx,cy,'HG04-water',16,0,new Color(205,221,218,255));
    }
    // Keep existing roof appearance for a deterministic share; enrich the rest with a common flat-roof material.
    const roofs=area.buildings.filter(p=>Math.abs(Math.floor(p.minX*13)+Math.floor(p.minY*7))%3!==0);
    if(roofs.length){const block=item(this.roofs,'Roofs-'+key,cx,cy,BLOCK,BLOCK);parts.push(block);this.layer(block,[],roofs,cx,cy,'HB01-flat-roof',8,0);}
    if(roads.length){
     const block=item(this.node,'Street-'+key,cx,cy,BLOCK,BLOCK);parts.push(block);
     this.layer(block,roads,[],cx,cy,'HG02-sidewalk',6,5);
     this.layer(block,roads,[],cx,cy,'HG01-asphalt',12,0);
    }
    this.blocks.set(key,parts);
   }
  }
  for(const [key,nodes] of this.blocks)if(!wanted.has(key)){for(const node of nodes){node.active=false;node.destroy();}this.blocks.delete(key);}
 }
 private layer(parent:Node,segments:Segment[],polygons:Polygon[],cx:number,cy:number,name:string,metres:number,extra:number,tint?:Color):void{
  const maskNode=item(parent,name+'Mask',0,0,BLOCK,BLOCK),mask=maskNode.addComponent(Mask);mask.type=Mask.Type.GRAPHICS_STENCIL;
  const g=maskNode.getComponent(Graphics)!;g.clear();g.strokeColor=Color.WHITE;g.fillColor=Color.WHITE;g.lineJoin=Graphics.LineJoin.ROUND;g.lineCap=Graphics.LineCap.ROUND;
  for(const poly of polygons){if(poly.p.length<3)continue;g.moveTo(poly.p[0][0]-cx,poly.p[0][1]-cy);for(const p of poly.p.slice(1))g.lineTo(p[0]-cx,p[1]-cy);g.close();g.fill();}
  for(const road of segments){g.lineWidth=road.width+extra;g.moveTo(road.a[0]-cx,road.a[1]-cy);g.lineTo(road.b[0]-cx,road.b[1]-cy);g.stroke();}
  const tile=item(maskNode,'Repeat');const sprite=tile.addComponent(Sprite);sprite.type=Sprite.Type.TILED;sprite.sizeMode=Sprite.SizeMode.CUSTOM;if(tint)sprite.color=tint;
  texture(name).then(frame=>{
   if(!isValid(maskNode,true)||!isValid(tile,true))return;
   const pixelScale=metres/frame.rect.width;tile.setScale(pixelScale,pixelScale,1);
   tile.getComponent(UITransform)!.setContentSize(BLOCK/pixelScale,BLOCK/pixelScale);sprite.spriteFrame=frame;
  },()=>{/* Original Graphics remains visible on load failure. */});
 }
}
