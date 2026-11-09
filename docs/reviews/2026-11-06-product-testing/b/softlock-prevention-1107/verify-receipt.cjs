// Read-only audit of the isolated candidate and the retained RED/GREEN evidence.
'use strict';
const fs=require('node:fs'),path=require('node:path'),crypto=require('node:crypto'),assert=require('node:assert/strict');
const HERE=__dirname,ROOT=path.resolve(HERE,'../../../../..');
const json=name=>JSON.parse(fs.readFileSync(path.join(HERE,name),'utf8'));
const sha=file=>crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');
const receipt=json('receipt.json'),green=json('green-root-fix-receipt.json'),originalGreen=json('green-receipt.json'),first=json('red-receipt.json'),boundaries=json('red-boundaries-receipt.json');
for(const [file,hash] of Object.entries(receipt.artifactFiles))assert.equal(sha(path.join(HERE,file)),hash,file);
assert.deepEqual(first.protectedBefore,green.protectedBefore,'First RED and GREEN production baselines');
assert.equal(Object.keys(green.protectedBefore).length,292);
for(const [file,hash] of Object.entries(green.protectedBefore))assert.equal(sha(path.join(ROOT,file)),hash,file);
assert.equal(Object.keys(green.a36Before).length,36);
assert.deepEqual(green.a36Before,green.a36After);
for(const [file,hash] of Object.entries(green.a36Before))assert.equal(sha(path.join(ROOT,file)),hash,file);
for(const name of ['red-receipt.json','red-boundaries-receipt.json','capture-history-receipt.json','green-receipt.json','green-root-fix-receipt.json']){
 const run=json(name);
 assert.equal(run.compilerExit,0,name);assert.equal(run.scratchRemoved,true,name);
 assert.equal(fs.existsSync(run.scratch),false,name);assert.deepEqual(run.protectedDrift,[],name);assert.deepEqual(run.a36Drift,[],name);
 if(run.counts){
  const log=fs.readFileSync(path.join(HERE,(run.tag||run.mode)+'.log'),'utf8');
  for(const [key,value] of Object.entries(run.counts))assert.equal(Number(new RegExp('^# '+key+' (\\d+)$','m').exec(log)?.[1]),value,name+': '+key);
 }
}
assert.equal(first.exitCode,1);assert.deepEqual(first.counts,{tests:1,pass:0,fail:1,cancelled:0,skipped:0});
assert.equal(boundaries.exitCode,1);assert.deepEqual(boundaries.counts,{tests:18,pass:1,fail:17,cancelled:0,skipped:0});
assert.equal(green.exitCode,0);assert.deepEqual(green.counts,{tests:71,pass:71,fail:0,cancelled:0,skipped:0});
assert.equal(sha(path.join(HERE,'run-stage.cjs')),green.runnerSHA256);
assert.equal(sha(path.join(HERE,'runner-red-baseline.cjs')),first.runnerSHA256);
for(const [file,hash] of Object.entries(green.overlays))assert.equal(sha(path.join(HERE,'stage/domain',file)),hash,file);
for(const [file,hash] of Object.entries(green.testFiles))assert.equal(sha(path.join(ROOT,file)),hash,file);
const test=path.relative(ROOT,path.join(HERE,'stage/tests/hero-car-reserve.test.cjs'));
assert.equal(boundaries.testFiles[test],originalGreen.testFiles[test],'Unchanged original 18-case RED/GREEN test source');
const currentTest=fs.readFileSync(path.join(ROOT,test),'utf8');
const newRoot="const ROOT=process.env.HERO_CAR_RESERVE_ROOT||path.resolve(__dirname,'../../..');";
const oldRoot="const ROOT=process.env.HERO_CAR_RESERVE_ROOT||path.resolve(__dirname,'../..');";
assert.equal(currentTest.split(newRoot).length,2,'Exactly one final default ROOT expression');
assert.equal(crypto.createHash('sha256').update(currentTest.replace(newRoot,oldRoot)).digest('hex'),originalGreen.testFiles[test],'Only the authorized ROOT line changed after original GREEN');
assert.deepEqual(green.overlays,originalGreen.overlays,'Both TS candidates unchanged');
assert.equal(path.resolve(path.dirname(path.join(ROOT,receipt.integration.testTarget)),'../../..'),ROOT,'Default ROOT at the integration target');
assert.equal(sha(path.join(ROOT,receipt.integration.requiredRunnerChange.path)),receipt.integration.requiredRunnerChange.beforeSHA256,'Production run-v2 remains unchanged by this author');
assert.equal(sha(path.join(HERE,'historical-fixtures.json')),json('capture-history-receipt.json').fixtureSHA256);
assert.equal(receipt.status,'PASS_ISOLATED_CANDIDATE_PENDING_PM_REVIEW');
console.log(JSON.stringify({status:'PASS',artifactFiles:Object.keys(receipt.artifactFiles).length,protectedLiveMatch:292,a36LiveMatch:36,allFiveScratchesAbsent:true,originalRedGreenBoundaryTestSHAEqual:true,finalTestOnlyRootLineChanged:true,defaultRootAtIntegrationTarget:true,greenTests:71,greenPass:71,greenFail:0,productionIntegration:'PENDING_PM'}));
