const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto');
const ts=require('/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/app.asar.unpacked/node_modules/typescript');
const root=process.cwd(),cache=new Map();
function load(file){file=path.resolve(file);if(cache.has(file))return cache.get(file).exports;const m={exports:{}};cache.set(file,m);const js=ts.transpileModule(fs.readFileSync(file,'utf8'),{compilerOptions:{target:ts.ScriptTarget.ES2020,module:ts.ModuleKind.CommonJS}}).outputText;const req=id=>id.startsWith('.')?load(path.resolve(path.dirname(file),id+'.ts')):require(id);new Function('require','module','exports',js)(req,m,m.exports);return m.exports;}
const sorted=x=>Array.isArray(x)?x.map(sorted):x&&typeof x==='object'?Object.fromEntries(Object.keys(x).sort().map(k=>[k,sorted(x[k])])):x;
const digest=x=>crypto.createHash('sha256').update(JSON.stringify(sorted(x))).digest('hex');
const raw=JSON.parse(fs.readFileSync('delivery-game/assets/resources/map-sample/city.json','utf8'));
const {prepareCity}=load('delivery-game/assets/scripts/map-sample/PlaceCatalog.ts'),{V2RouteSession}=load('delivery-game/assets/scripts/map-sample/V2RouteSession.ts');
const city=prepareCity(raw),arrays=Object.fromEntries(['nodes','roads','pois'].map(k=>[k,{count:city[k].length,sortedSHA:digest(city[k])}]));
const bounds=city.dispatchBounds||city.playBounds,nodes=city.nodes.filter(n=>!bounds||n.x>=bounds.minX&&n.x<=bounds.maxX&&n.y>=bounds.minY&&n.y<=bounds.maxY),allowed=new Set(nodes.map(n=>n.id)),roads=[];
for(const road of city.roads){let run=[],part=0;const flush=()=>{if(run.length>1)roads.push({...road,id:road.id+':v2:'+part++,nodes:run});run=[];};for(const id of road.nodes){if(allowed.has(id))run.push(id);else flush();}flush();}
const places=city.pois.filter((p,i)=>allowed.has(p.node)&&(!city.operatingPOIs||city.operatingPOIs.includes(i)));
const receipt={sourceMapKey:new V2RouteSession(city).snapshot().mapKey,arrays,rawCitySortedSHA256:digest(raw),routingGeometrySortedSHA256:digest([nodes,roads,places]),cityPreparedSortedSHA256:digest(city),sourceUnchanged:true};
fs.writeFileSync(path.join(__dirname,'source-map-identity.json'),JSON.stringify(receipt,null,2)+'\n');console.log(JSON.stringify(receipt,null,2));
