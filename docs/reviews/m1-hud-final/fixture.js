// Isolated render fixture: intercept component start before any save-store creation.
window.uiFixture={ready:false,storageAccess:0,storageAttempts:[]};
for(const method of ['getItem','setItem','removeItem','clear'])Storage.prototype[method]=function(...args){window.uiFixture.storageAccess++;window.uiFixture.storageAttempts.push({method,key:args[0],stack:new Error().stack});throw Error('Storage forbidden in UI fixture');};
const register=System.register;
System.register=function(name,deps,declare){
 if(typeof name==='string'&&name.endsWith('/MapSample.ts')){
  const original=declare;
  declare=function(exportFn,context){return original(function(key,value){
   if(key==='MapSample'){
    value.prototype.start=function(){fixtureStart(this).catch(e=>{console.error(e);window.uiFixture.error=String(e);});};
    value.prototype.update=function(){};value.prototype.save=function(){};
   }
   return exportFn(key,value);
  },context);};
 }
 return register.call(this,name,deps,declare);
};
async function fixtureStart(sample){
 const cc=await System.import('cc');
 const {OrderBook}=await System.import('chunks:///_virtual/OrderBook.ts');
 const {prepareCity}=await System.import('chunks:///_virtual/PlaceCatalog.ts');
 const asset=await new Promise((resolve,reject)=>cc.resources.load('map-sample/city',cc.JsonAsset,(e,a)=>e?reject(e):resolve(a)));
 sample.book=new OrderBook(prepareCity(asset.json));sample.store={available:true,save(){throw Error('No fixture saves');}};
 sample.book.playerState.cashCents=Number(new URLSearchParams(location.search).get('cents')||10000);
 if(new URLSearchParams(location.search).has('safe'))sample.readSafeInsets=()=>({top:36,bottom:28,left:10,right:10});
 if(new URLSearchParams(location.search).has('fail')||new URLSearchParams(location.search).has('loading')){const load=cc.resources.load.bind(cc.resources);cc.resources.load=(url,type,cb)=>url.includes('vehicle-sheet')?(new URLSearchParams(location.search).has('fail')?cb(new Error('fixture failure')):undefined):load(url,type,cb);}
 if(new URLSearchParams(location.search).has('avatarfail')){const load=cc.resources.load.bind(cc.resources);cc.resources.load=(url,type,cb)=>url.includes('ui-icons')?cb(new Error('isolated icons failure')):load(url,type,cb);}
 sample.rebuildLayout();
 
 const page=new URLSearchParams(location.search).get('page')||'home';
 if(page.startsWith('receipt')){sample.book.accept(sample.book.list()[0].offer.id);sample.book.depart();sample.book.advance(99);if(sample.book.mode==='arrived')sample.book.settle(true);sample.rebuildLayout();sample.openReceipt();}
 if(page.startsWith('vehicle')){sample.book.playerState.vehicleTier=page.includes('plus')?2:1;sample.city.setVehicle(sample.book.player.vehicleTier);sample.city.setRider(sample.book.riderPose.point,page.includes('north')?90:0);}
 if(page==='garage')sample.openGarage();if(page==='maps')sample.openMaps();if(page==='bills')sample.openBills();if(page==='phone')sample.openPhone();
 if(page==='buttons'){
  const ui=await System.import('chunks:///_virtual/SampleUI.ts');
  for(const [i,w]of [90,174,320,620].entries())ui.button(sample.root,'抢单',0,300-i*150,w,80,()=>{});
 }
 window.uiFixture.sample=sample;window.uiFixture.ready=true;
}
