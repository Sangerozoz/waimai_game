import { isValid, Layers, Node, Rect, resources, Size, Sprite, SpriteFrame, Texture2D, UITransform } from 'cc';

type Crop={resource:string;rect:[number,number,number,number]};
const crops:Record<string,Crop>={};
function register(resource:string,keys:string[],rectangles:number[][],width=1280,height=1280):void {
 keys.forEach((key,i)=>{const r=rectangles[i];crops[key]={resource:'map-sample/cartoon/'+resource,rect:[r[0]/width,r[1]/height,r[2]/width,r[3]/height]};});
}
register('ui-icons',["avatar","recruit","vehicle","map","bills","station","coin","star","bag","close","target","confirm"],[[2.0415,120.4466,326.6348,343.9872],[328.6762,120.4466,312.3445,343.9872],[641.0207,120.4466,314.386,343.9872],[955.4067,120.4466,322.5518,343.9872],[4.0829,484.8485,321.5311,333.7799],[325.614,484.8485,320.5104,333.7799],[645.1037,510.3668,307.2408,316.4274],[960.5104,510.3668,306.2201,300.0957],[8.1659,832.9187,319.4896,347.0494],[323.5726,847.2089,322.5518,329.697],[644.0829,847.2089,319.4896,329.697],[961.5311,847.2089,318.4689,329.697]]);
register('vehicle-sheet',["side-d","side-d-plus","top-d","top-d-plus"],[[16,64,608,520],[628,60,636,520],[144,632,380,608],[760,632,380,608]]);
// AU04: each frame references unchanged user original, in top-left source pixels.
const foodKeys=["chicken-rice","beef-rice","pork-rice","tofu-rice","soup-noodles","mixed-noodles","wonton","hotpot","dumplings","buns","pizza","burger","salad","sushi","cake","milk-tea","curry-chicken-rice","eel-rice","tomato-egg-rice","braised-chicken-rice","roast-duck-rice","pork-cutlet-rice","shrimp-fried-rice","sausage-claypot-rice","seafood-fried-rice","mushroom-chicken-rice","beef-noodle-soup","spicy-rice-noodles","snail-rice-noodles","rice-noodle-soup","spicy-mixed-noodles","cold-noodles","fried-noodles","spaghetti","steamed-rice-rolls","steamed-shrimp-dumplings","pan-fried-buns","spring-rolls","fried-chicken","fries","chicken-wrap","sandwich","grilled-skewers","fruit-cup","egg-tarts","pudding","ice-cream","coffee","lemon-tea","orange-juice"];
crops['chicken-rice']={resource:'map-sample/anime/au04/food-batch-01-regenerated-v2',rect:[15/1983,58/793,392/1983,337/793]};
crops['beef-rice']={resource:'map-sample/anime/au04/food-batch-01-regenerated-v2',rect:[408/1983,68/793,387/1983,324/793]};
crops['pork-rice']={resource:'map-sample/anime/au04/food-batch-01-regenerated-v2',rect:[795/1983,68/793,397/1983,320/793]};
crops['tofu-rice']={resource:'map-sample/anime/au04/food-batch-01-regenerated-v2',rect:[1190/1983,60/793,400/1983,330/793]};
crops['soup-noodles']={resource:'map-sample/anime/au04/food-batch-01-regenerated-v2',rect:[1577/1983,55/793,400/1983,334/793]};
crops['mixed-noodles']={resource:'map-sample/anime/au04/food-batch-01-regenerated-v2',rect:[12/1983,401/793,398/1983,345/793]};
crops['wonton']={resource:'map-sample/anime/au04/food-batch-01-regenerated-v2',rect:[406/1983,397/793,395/1983,345/793]};
crops['hotpot']={resource:'map-sample/anime/au04/food-batch-01-regenerated-v2',rect:[798/1983,374/793,399/1983,387/793]};
crops['dumplings']={resource:'map-sample/anime/au04/food-batch-01-regenerated-v2',rect:[1193/1983,412/793,390/1983,320/793]};
crops['buns']={resource:'map-sample/anime/au04/food-batch-01-regenerated-v2',rect:[1594/1983,397/793,378/1983,356/793]};
crops['pizza']={resource:'map-sample/anime/au04/food-batch-02-regenerated-v2',rect:[14/1983,70/793,391/1983,321/793]};
crops['burger']={resource:'map-sample/anime/au04/food-batch-02-regenerated-v2',rect:[407/1983,50/793,383/1983,351/793]};
crops['salad']={resource:'map-sample/anime/au04/food-batch-02-regenerated-v2',rect:[793/1983,55/793,392/1983,351/793]};
crops['sushi']={resource:'map-sample/anime/au04/food-batch-02-regenerated-v2',rect:[1190/1983,45/793,426/1983,368/793]};
crops['cake']={resource:'map-sample/anime/au04/food-batch-02-regenerated-v2',rect:[1610/1983,58/793,352/1983,352/793]};
crops['milk-tea']={resource:'map-sample/anime/au04/food-batch-02-regenerated-v2',rect:[64/1983,388/793,258/1983,366/793]};
crops['curry-chicken-rice']={resource:'map-sample/anime/au04/food-batch-02-regenerated-v2',rect:[385/1983,425/793,396/1983,333/793]};
crops['eel-rice']={resource:'map-sample/anime/au04/food-batch-02-regenerated-v2',rect:[797/1983,417/793,383/1983,344/793]};
crops['tomato-egg-rice']={resource:'map-sample/anime/au04/food-batch-02-regenerated-v2',rect:[1192/1983,424/793,388/1983,330/793]};
crops['braised-chicken-rice']={resource:'map-sample/anime/au04/food-batch-02-regenerated-v2',rect:[1578/1983,428/793,394/1983,326/793]};
crops['roast-duck-rice']={resource:'map-sample/anime/au04/food-batch-03-original',rect:[5/1983,49/793,402/1983,344/793]};
crops['pork-cutlet-rice']={resource:'map-sample/anime/au04/food-batch-03-original',rect:[410/1983,50/793,389/1983,345/793]};
crops['shrimp-fried-rice']={resource:'map-sample/anime/au04/food-batch-03-original',rect:[800/1983,48/793,386/1983,335/793]};
crops['sausage-claypot-rice']={resource:'map-sample/anime/au04/food-batch-03-original',rect:[1182/1983,49/793,406/1983,326/793]};
crops['seafood-fried-rice']={resource:'map-sample/anime/au04/food-batch-03-original',rect:[1581/1983,47/793,397/1983,335/793]};
crops['mushroom-chicken-rice']={resource:'map-sample/anime/au04/food-batch-03-original',rect:[6/1983,419/793,401/1983,329/793]};
crops['beef-noodle-soup']={resource:'map-sample/anime/au04/food-batch-03-original',rect:[406/1983,397/793,390/1983,347/793]};
crops['spicy-rice-noodles']={resource:'map-sample/anime/au04/food-batch-03-original',rect:[794/1983,395/793,395/1983,353/793]};
crops['snail-rice-noodles']={resource:'map-sample/anime/au04/food-batch-03-original',rect:[1190/1983,409/793,393/1983,338/793]};
crops['rice-noodle-soup']={resource:'map-sample/anime/au04/food-batch-03-original',rect:[1581/1983,412/793,396/1983,338/793]};
crops['spicy-mixed-noodles']={resource:'map-sample/anime/au04/food-batch-04-original',rect:[5/1983,55/793,399/1983,337/793]};
crops['cold-noodles']={resource:'map-sample/anime/au04/food-batch-04-original',rect:[408/1983,58/793,384/1983,330/793]};
crops['fried-noodles']={resource:'map-sample/anime/au04/food-batch-04-original',rect:[798/1983,58/793,393/1983,332/793]};
crops['spaghetti']={resource:'map-sample/anime/au04/food-batch-04-original',rect:[1193/1983,64/793,410/1983,327/793]};
crops['steamed-rice-rolls']={resource:'map-sample/anime/au04/food-batch-04-original',rect:[1591/1983,60/793,389/1983,332/793]};
crops['steamed-shrimp-dumplings']={resource:'map-sample/anime/au04/food-batch-04-original',rect:[6/1983,388/793,394/1983,370/793]};
crops['pan-fried-buns']={resource:'map-sample/anime/au04/food-batch-04-original',rect:[399/1983,401/793,404/1983,333/793]};
crops['spring-rolls']={resource:'map-sample/anime/au04/food-batch-04-original',rect:[798/1983,393/793,402/1983,345/793]};
crops['fried-chicken']={resource:'map-sample/anime/au04/food-batch-04-original',rect:[1192/1983,376/793,434/1983,388/793]};
crops['fries']={resource:'map-sample/anime/au04/food-batch-04-original',rect:[1643/1983,376/793,330/1983,381/793]};
crops['chicken-wrap']={resource:'map-sample/anime/au04/food-batch-05-original',rect:[14/1983,43/793,387/1983,318/793]};
crops['sandwich']={resource:'map-sample/anime/au04/food-batch-05-original',rect:[418/1983,33/793,390/1983,335/793]};
crops['grilled-skewers']={resource:'map-sample/anime/au04/food-batch-05-original',rect:[804/1983,12/793,426/1983,369/793]};
crops['fruit-cup']={resource:'map-sample/anime/au04/food-batch-05-original',rect:[1234/1983,11/793,331/1983,373/793]};
crops['egg-tarts']={resource:'map-sample/anime/au04/food-batch-05-original',rect:[1600/1983,70/793,377/1983,287/793]};
crops['pudding']={resource:'map-sample/anime/au04/food-batch-05-original',rect:[46/1983,421/793,331/1983,337/793]};
crops['ice-cream']={resource:'map-sample/anime/au04/food-batch-05-original',rect:[465/1983,373/793,333/1983,400/793]};
crops['coffee']={resource:'map-sample/anime/au04/food-batch-05-original',rect:[862/1983,363/793,300/1983,409/793]};
crops['lemon-tea']={resource:'map-sample/anime/au04/food-batch-05-original',rect:[1264/1983,362/793,283/1983,410/793]};
crops['orange-juice']={resource:'map-sample/anime/au04/food-batch-05-original',rect:[1646/1983,360/793,290/1983,412/793]};
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
// AU05 supplementary function icons, isolated rectangles with silhouette margins.
crops['recruit']={resource:'map-sample/anime/au05/supplementary-icons-v2-original',rect:[55/1536,73/1024,472/1536,430/1024]};
crops['bag']={resource:'map-sample/anime/au05/supplementary-icons-v2-original',rect:[598/1536,81/1024,390/1536,425/1024]};
crops['target']={resource:'map-sample/anime/au05/supplementary-icons-v2-original',rect:[1083/1536,86/1024,400/1536,398/1024]};
crops['confirm']={resource:'map-sample/anime/au05/supplementary-icons-v2-original',rect:[78/1536,568/1024,386/1536,382/1024]};
crops['close']={resource:'map-sample/anime/au05/supplementary-icons-v2-original',rect:[593/1536,607/1024,348/1536,338/1024]};
crops['pause']={resource:'map-sample/anime/au05/supplementary-icons-v2-original',rect:[1133/1536,566/1024,292/1536,383/1024]};
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

