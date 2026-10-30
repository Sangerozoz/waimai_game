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
 sample.book.playerState.cashCents=new URLSearchParams(location.search).has('long')?12345678900:10000;
 if(new URLSearchParams(location.search).has('safe'))sample.readSafeInsets=()=>({top:36,bottom:28,left:10,right:10});
 sample.rebuildLayout();
 const page=new URLSearchParams(location.search).get('page')||'home';
 if(page==='garage')sample.openGarage();if(page==='maps')sample.openMaps();if(page==='bills')sample.openBills();if(page==='phone')sample.openPhone();
 if(page==='buttons'){
  const ui=await System.import('chunks:///_virtual/SampleUI.ts');
  for(const [i,w]of [90,174,320,620].entries())ui.button(sample.root,'抢单',0,300-i*150,w,80,()=>{});
 }
 window.uiFixture.sample=sample;window.uiFixture.ready=true;
}
