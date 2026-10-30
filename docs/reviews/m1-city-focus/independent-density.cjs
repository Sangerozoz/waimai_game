// Isolated review runner: production sources and developer tests are read only.
const fs=require('node:fs'),path=require('node:path'),os=require('node:os'),Module=require('node:module');
const root=path.resolve(__dirname,'../../../delivery-game');
const ts=require('/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/app.asar.unpacked/node_modules/typescript');
const out=fs.mkdtempSync(path.join(os.tmpdir(),'m1-independent-'));
process.on('exit',()=>fs.rmSync(out,{recursive:true,force:true}));
const names=['MapTypes','CityExtent','SafeAreaLayout','PlaceCatalog','FoodCatalog','RoadRouter','DeliveryClock','CountyRules','OrderBook','ReceiptPresentation','BillingPresentation'];
const program=ts.createProgram(names.map(n=>path.join(root,'assets/scripts/map-sample',n+'.ts')),{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS,strict:true,noEmitOnError:true,rootDir:path.join(root,'assets/scripts'),outDir:out,skipLibCheck:true,types:[]});
const emitted=program.emit();if(ts.getPreEmitDiagnostics(program).length||emitted.emitSkipped)throw Error('Review fixture compilation failed');
process.env.MAP_ROUTER_MODULE=path.join(out,'map-sample/RoadRouter.js');

const {test}=require('node:test'),assert=require('node:assert/strict'),vm=require('node:vm');
const dir=path.join(out,'map-sample'),places=require(path.join(dir,'PlaceCatalog.js')),{OrderBook}=require(path.join(dir,'OrderBook.js')),{countyMapId}=require(path.join(dir,'CountySnapshot.js')),{RoadRouter}=require(path.join(dir,'RoadRouter.js'));
const raw=require(path.join(root,'assets/resources/map-sample/city.json'));
const before=path.resolve(root,'../docs/reviews/m1-city-focus/before/delivery-game/assets/scripts/map-sample/PlaceCatalog.ts');
let code=fs.readFileSync(before,'utf8').replace('function legacyCity','export function legacyCity').replace('function localityCity','export function localityCity');const scope={exports:{},require:id=>require(path.join(dir,id+'.js'))};vm.runInNewContext(ts.transpileModule(code,{compilerOptions:{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS}}).outputText,scope);
const v1=scope.exports.legacyCity(raw),v2=scope.exports.localityCity(raw),v3=scope.exports.prepareCity(raw),v4=places.prepareCity(raw),oldIds=[raw,v1,v2,v3].map(countyMapId);
function rng(){let n=17;return()=>((n=(n*1664525+1013904223)>>>0)/4294967296);}const day=()=> '2026-10-29';
test('independent density: full 385 prefix, all direct historic inputs, idempotency, graph rejection',()=>{
 assert.equal(v3.pois.length,385);assert.equal(v4.placeCatalogVersion,4);assert.equal(JSON.stringify(v4.pois.slice(0,385)),JSON.stringify(v3.pois));
 for(const historical of [raw,v1,v2,v3]){const upgraded=places.prepareCity(historical);assert.equal(JSON.stringify(upgraded.pois),JSON.stringify(v4.pois));assert.deepEqual(upgraded.operatingPOIs,v4.operatingPOIs);assert.ok(v4.legacyMapIds.includes(countyMapId(historical)));}
 assert.equal(places.prepareCity(v4),v4);assert.equal(countyMapId(places.prepareCity(JSON.parse(JSON.stringify(v4)))),countyMapId(v4));
 const saved=new OrderBook(v3,rng(),day).serialize();const changed=places.prepareCity({...raw,nodes:raw.nodes.map((n,i)=>i?n:{...n,x:n.x+1})});assert.throws(()=>OrderBook.restore(changed,saved,rng(),day),/路网/);
});
test('independent density: quotas, east-west, pair distances, 450m, bidirectional reach and additions usable',()=>{
 const nodes=new Map(v4.nodes.map(n=>[n.id,n])),pool=v4.operatingPOIs.map(i=>({i,p:v4.pois[i]})),counts={},urban=pool.filter(v=>v4.dispatchAreas[v.p.node]==='urban');let min=Infinity,merchantMin=Infinity,east=[0,0],west=[0,0];const router=new RoadRouter({...v4,nodes:v4.nodes.filter(n=>n.x>=v4.playBounds.minX&&n.x<=v4.playBounds.maxX&&n.y>=v4.playBounds.minY&&n.y<=v4.playBounds.maxY)});
 for(const {p,i} of pool){const a=v4.dispatchAreas[p.node],m=p.kind==='restaurant'?0:1;(counts[a]??=[0,0])[m]++;const n=nodes.get(p.node);assert.ok(n.x>=v4.dispatchBounds.minX&&n.x<=v4.dispatchBounds.maxX&&n.y>=v4.dispatchBounds.minY&&n.y<=v4.dispatchBounds.maxY);assert.ok(router.find(v4.pois[0].node,p.node,'fast'));assert.ok(router.find(p.node,v4.pois[0].node,'fast'));if(a==='urban')(n.x>=-2100?east:west)[m]++;}
 assert.deepEqual(counts,{urban:[60,180],suburb:[12,36],remote:[8,24]});assert.deepEqual(east,[42,126]);assert.deepEqual(west,[18,54]);
 for(let a=0;a<urban.length;a++)for(let b=a+1;b<urban.length;b++){const p=nodes.get(urban[a].p.node),q=nodes.get(urban[b].p.node),d=Math.hypot(p.x-q.x,p.y-q.y);min=Math.min(min,d);assert.ok(d>=35);if(urban[a].p.kind==='restaurant'&&urban[b].p.kind==='restaurant'){merchantMin=Math.min(merchantMin,d);assert.ok(d>=70);}}
 assert.deepEqual([v4.dispatchBounds.minX-v4.playBounds.minX,v4.playBounds.maxX-v4.dispatchBounds.maxX,v4.dispatchBounds.minY-v4.playBounds.minY,v4.playBounds.maxY-v4.dispatchBounds.maxY],[450,450,450,450]);
 const book=new OrderBook(v4,rng(),day),seenM=new Set(),seenC=new Set();for(let i=0;i<70;i++){for(const row of book.list()){const o=row.offer;assert.ok(v4.operatingPOIs.includes(o.from)&&v4.operatingPOIs.includes(o.to));if(o.from>=385)seenM.add(o.from);if(o.to>=385)seenC.add(o.to);}book.offers.splice(0);book.offers.push(...book.nearbyOffers([]));}
 assert.ok(seenM.size>0&&seenC.size>0);console.log('DENSITY',JSON.stringify({counts,east,west,min,merchantMin,newMerchantSample:seenM.size,newCustomerSample:seenC.size,pois:v4.pois.length,oldIds}));
});
test('independent density: active snapshots keep endpoints routes progress ledger location and finish once',()=>{
 for(const state of ['routes','running','paused','arrived','done']){
  const b=new OrderBook(v3,rng(),day);b.refreshFree();b.accept((b.list().find(r=>r.offer.demand==='door')||b.list()[0]).offer.id);if(state!=='routes')b.depart();if(state==='running'||state==='paused')b.advance(2.4);if(state==='arrived'||state==='done')b.advance(999);if(state==='done'&&b.mode==='arrived')b.settle(true);
  console.log('ACTIVE',state,b.mode,'outsideNewPool',!v4.operatingPOIs.includes(b.active.offer.from)||!v4.operatingPOIs.includes(b.active.offer.to));assert.equal(b.mode,state==='paused'?'running':state);const snapshot=JSON.parse(b.serialize());if(state==='paused')snapshot.active.mode='paused';const before=JSON.stringify(snapshot.active),restored=OrderBook.restore(v4,JSON.stringify(snapshot),rng(),day),active=JSON.parse(JSON.stringify(restored.active));if(state==='paused')active.mode='paused';assert.equal(JSON.stringify(active),before);assert.deepEqual(restored.player,b.player);assert.deepEqual(restored.billing,b.billing);assert.equal(restored.refreshesLeft,b.refreshesLeft);assert.ok(restored.riderPose.point.every((v,i)=>Math.abs(v-b.riderPose.point[i])<1e-8));
  if(restored.mode==='routes')restored.depart();if(restored.mode==='running')restored.advance(999);if(restored.mode==='arrived')restored.settle(true);assert.equal(restored.mode,'done');const cash=restored.player.cashCents,ledger=JSON.stringify(restored.billing);restored.finish();restored.finish();assert.equal(restored.mode,'idle');assert.equal(restored.player.cashCents,cash);assert.equal(JSON.stringify(restored.billing),ledger);
 }
 for(const mapId of oldIds){const b=new OrderBook(v3,rng(),day),s=JSON.parse(b.serialize());s.mapId=mapId;const r=OrderBook.restore(v4,JSON.stringify(s),rng(),day);assert.deepEqual(r.player,b.player);assert.equal(r.refreshesLeft,b.refreshesLeft);}
});
