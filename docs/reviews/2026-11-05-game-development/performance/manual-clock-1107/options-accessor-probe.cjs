'use strict';
const fs=require('node:fs'),path=require('node:path'),Module=require('node:module'),assert=require('node:assert/strict'),crypto=require('node:crypto');
const root=path.resolve(__dirname,'../../../../..'),scripts=path.join(root,'delivery-game/assets/scripts'),ts=require('/Applications/Cocos/Creator/3.8.8/CocosCreator.app/Contents/Resources/app.asar.unpacked/node_modules/typescript'),sha=x=>crypto.createHash('sha256').update(x).digest('hex');
const originals=new Map(['V2EconomySession.ts','V2FleetSession.ts','V2DispatchSession.ts'].map(name=>[path.join(scripts,'domain',name),fs.readFileSync(path.join(__dirname,'source-before',name),'utf8')]));
function variant(name,useBefore){
 const cache=new Map(),loaded=[];
 function load(file){
  file=path.resolve(file);assert.ok(file.startsWith(scripts+path.sep));
  if(cache.has(file))return cache.get(file).exports;
  const m=new Module(file,module);cache.set(file,m);m.filename=file;
  m.require=id=>{assert.ok(id.startsWith('.'),`unexpected source dependency ${id}`);return load(path.resolve(path.dirname(file),id+'.ts'));};
  const source=useBefore&&originals.has(file)?originals.get(file):fs.readFileSync(file,'utf8');
  loaded.push({path:path.relative(root,file),sha256:sha(source)});
  const code=ts.transpileModule(source,{compilerOptions:{module:ts.ModuleKind.CommonJS,target:ts.ScriptTarget.ES2020}}).outputText;
  m._compile(code,file);return m.exports;
 }
 const {V2GameSession:Game}=load(path.join(scripts,'map-sample/V2GameSession.ts'));
 const {prepareCity}=load(path.join(scripts,'map-sample/PlaceCatalog.ts'));
 const city=prepareCity(JSON.parse(fs.readFileSync(path.join(root,'delivery-game/assets/resources/map-sample/city.json'),'utf8')));
 return {name,Game,city,loaded,Dispatch:load(path.join(scripts,'domain/V2DispatchSession.ts')).V2DispatchSession,Economy:load(path.join(scripts,'domain/V2EconomySession.ts')).V2EconomySession};
}

const rows=[];for(const v of [variant('before',true),variant('candidate',false)]){let reads=0;const d=new v.Dispatch({verifyArrival:()=>true},0,'slots-v1'),options={get deferAuto(){reads++;return true;},deferFleet:true};const result=d.tick(1,1,true,false,options);rows.push({variant:v.name,externalDeferAutoGetterReads:reads,result,stateSHA256:sha(d.serialize())});}process.stdout.write(JSON.stringify({scope:'read-only source probe; frozen source and test files unchanged',rows},null,2)+'\n');
