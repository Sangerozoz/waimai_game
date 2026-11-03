import { isValid, Layers, Node, Rect, resources, Size, Sprite, SpriteFrame, Texture2D, UITransform } from 'cc';

type Crop={resource:string;rect:[number,number,number,number]};
const crops:Record<string,Crop>={};
function register(resource:string,keys:string[],rectangles:number[][],width=1280,height=1280):void {
 keys.forEach((key,i)=>{const r=rectangles[i];crops[key]={resource:'map-sample/cartoon/'+resource,rect:[r[0]/width,r[1]/height,r[2]/width,r[3]/height]};});
}
register('ui-icons',["avatar","recruit","vehicle","map","bills","station","coin","star","bag","close","target","confirm"],[[2.0415,120.4466,326.6348,343.9872],[328.6762,120.4466,312.3445,343.9872],[641.0207,120.4466,314.386,343.9872],[955.4067,120.4466,322.5518,343.9872],[4.0829,484.8485,321.5311,333.7799],[325.614,484.8485,320.5104,333.7799],[645.1037,510.3668,307.2408,316.4274],[960.5104,510.3668,306.2201,300.0957],[8.1659,832.9187,319.4896,347.0494],[323.5726,847.2089,322.5518,329.697],[644.0829,847.2089,319.4896,329.697],[961.5311,847.2089,318.4689,329.697]]);
register('vehicle-sheet',["side-d","side-d-plus","top-d","top-d-plus"],[[16,64,608,520],[628,60,636,520],[144,632,380,608],[760,632,380,608]]);
const foodKeys=['chicken-rice','beef-rice','pork-rice','tofu-rice','soup-noodles','mixed-noodles','wonton','hotpot','dumplings','buns','pizza','burger','salad','sushi','cake','milk-tea'];
register('food-sheet',foodKeys,[[12.2488,28.5805,311.3238,301.1164],[332.7592,59.2026,306.2201,269.4737],[641.0207,48.9952,315.4067,281.7225],[966.6348,63.2855,302.1372,264.37],[10.2073,347.0494,316.4274,277.6396],[329.697,347.0494,309.2823,275.5981],[640.0,352.1531,310.303,275.5981],[944.1786,341.9458,333.7799,283.764],[10.2073,655.311,321.5311,264.37],[335.8214,632.8549,302.1372,302.1372],[638.9793,645.1037,328.6762,278.6603],[969.697,633.8756,298.0542,293.9713],[12.2488,952.3445,311.3238,285.8054],[316.4274,956.4274,336.8421,283.764],[649.1866,921.7225,334.8006,320.5104],[1015.63,918.6603,226.6029,336.8421]]);
register('ui-chrome',["panel-blue","panel-violet","button-yellow","button-blue"],[[10.2073,179.6491,630.8134,606.3158],[637.9585,179.6491,630.8134,606.3158],[12.2488,828.8357,628.7719,277.6396],[637.9585,828.8357,630.8134,277.6396]]);
// AU01 user-delivered originals: use engine rectangles, never repaint the accepted face.
// Source coordinates are top-left pixels in the unchanged 1024 x 1536 master.
crops.avatar={resource:'map-sample/anime/au01/rider-master-original',rect:[340/1024,0,360/1024,360/1536]};
// Keep the entire alpha canvas, including warm translucent edge pixels. North-facing art
// continues through MapVehicle's existing -90 degree correction and road rotation.
crops['side-d']={resource:'map-sample/anime/au02/vehicle-d-three-quarter-original',rect:[0,0,1,1]};
crops['top-d']={resource:'map-sample/anime/au01/vehicle-top-original',rect:[0,0,1,1]};
// Temporary D+ art sharing: preserve tier mechanics, but avoid old-style atlas frames.
// These aliases are not independently delivered D+ artwork and apply no recoloring.
crops['top-d-plus']=crops['top-d'];
crops['side-d-plus']=crops['side-d'];
// AU03 hand-framed silhouettes: the vehicle front wheel extends beyond x=512.
crops['coin']={resource:'map-sample/anime/au03/ui-icons-six-original',rect:[56/1536,72/1024,420/1536,424/1024]};
crops['heart']={resource:'map-sample/anime/au03/ui-icons-six-original',rect:[540/1536,92/1024,456/1536,400/1024]};
crops['station']={resource:'map-sample/anime/au03/ui-icons-six-original',rect:[1008/1536,50/1024,516/1536,456/1024]};
crops['vehicle']={resource:'map-sample/anime/au03/ui-icons-six-original',rect:[8/1536,500/1024,528/1536,500/1024]};
crops['bills']={resource:'map-sample/anime/au03/ui-icons-six-original',rect:[538/1536,516/1024,448/1536,480/1024]};
crops['map']={resource:'map-sample/anime/au03/ui-icons-six-original',rect:[990/1536,548/1024,534/1536,432/1024]};
const atlases=new Map<string,Promise<Texture2D>>(),frames=new Map<string,SpriteFrame>();
function loadAtlas(resource:string):Promise<Texture2D> {
 const cached=atlases.get(resource);if(cached)return cached;
 const pending=new Promise<Texture2D>((resolve,reject)=>resources.load(resource+'/texture',Texture2D,(error,texture)=>{
  if(error){reject(error);return;}texture.addRef();resolve(texture);
 }));
 atlases.set(resource,pending);pending.catch(()=>{if(atlases.get(resource)===pending)atlases.delete(resource);});return pending;
}
// Immutable frames and their textures are retained once for the lifetime of the game.
export function loadCartoonFrame(key:string):Promise<SpriteFrame> {
 const crop=crops[key];if(!crop)return Promise.reject(new Error('Unknown cartoon art: '+key));
 const cached=frames.get(key);if(cached)return Promise.resolve(cached);
 return loadAtlas(crop.resource).then(texture=>{
  const existing=frames.get(key);if(existing)return existing;
  const [left,top,width,height]=crop.rect,x=Math.round(left*texture.width),y=Math.round(top*texture.height);
  const w=Math.round((left+width)*texture.width)-x,h=Math.round((top+height)*texture.height)-y;
  const frame=new SpriteFrame();frame.texture=texture;frame.rect=new Rect(x,y,w,h);frame.originalSize=new Size(w,h);frame.addRef();frames.set(key,frame);return frame;
 });
}
export function cartoonArt(parent:Node,key:string,x:number,y:number,width:number,height:number,fallback?:Node):Node {
 const picture=new Node('CartoonArt-'+key);picture.layer=Layers.Enum.UI_2D;parent.addChild(picture);picture.setPosition(x,y);
 const transform=picture.addComponent(UITransform);transform.setContentSize(width,height);picture.active=false;
 const sprite=picture.addComponent(Sprite);sprite.sizeMode=Sprite.SizeMode.CUSTOM;
 loadCartoonFrame(key).then(frame=>{
  if(!isValid(parent,true)||!isValid(picture,true)||parent.activeInHierarchy===false)return;
  const scale=Math.min(width/frame.originalSize.width,height/frame.originalSize.height);
  transform.setContentSize(frame.originalSize.width*scale,frame.originalSize.height*scale);
  sprite.spriteFrame=frame;picture.active=true;if(fallback&&isValid(fallback,true))fallback.active=false;
 },()=>{/* Retain the native fallback; the next opening may retry. */});return picture;
}
export function cartoonFoodKey(index:number):string|null{return foodKeys[index]||null;}

