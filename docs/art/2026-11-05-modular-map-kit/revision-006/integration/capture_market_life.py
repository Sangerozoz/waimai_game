#!/usr/bin/env python3
"""Only the authorized local map preview: compact real readback and one market view and optional useful detail."""
import sys
sys.dont_write_bytecode=True
import json,subprocess,shutil
from pathlib import Path
B=Path(__file__).parent/'market-life'
session=sys.argv[1];view=sys.argv[2];name=sys.argv[3]
url='http://127.0.0.1:4186/revision-006/viewer/?view='+view+'&embed=1'
script='''const p=await browser.getPage("main"); await p.goto(URL);
console.log(JSON.stringify(await p.evaluate(async()=>{
 for(let j=0;j<100&&!globalThis.__mapUIDimensions;j++)await new Promise(r=>setTimeout(r,100));
 if(!globalThis.__mapUIDimensions)throw Error("Cocos node readback not ready");
 return {url:location.href,columns:{order:["id","editorOrder","siblingIndex","x","y"],ui:["id","width","height","scaleX","scaleY","worldWidth","worldHeight"],frames:["assetId","file","frameIndex"]},
 order:globalThis.__mapPreviewOrder.map(i=>[i.persistentId||i.name,i.editorOrder,i.siblingIndex,i.x,i.y]),
 ui:globalThis.__mapUIDimensions.map(i=>[i.persistentId,i.uiWidth,i.uiHeight,i.nodeScaleX,i.nodeScaleY,...i.worldFrameUnits]),
 frames:globalThis.__mapFrameSharing.map(i=>[i.assetId,i.file,i.frameIndex]),textures:globalThis.__mapTextureStats,ground:globalThis.__mapGroundStats,active:globalThis.__mapActiveGroundRegionIds,
 canvas:Array.from(document.querySelectorAll("canvas")).map(c=>[c.width,c.height]),errors:document.body.innerText.includes("素材加载失败")};
}))); await p.shot({type:"jpeg",maxEdge:1600,quality:88}); undefined'''.replace('URL',json.dumps(url))
run=subprocess.run(['bb','browser-automation','run',session,'--script',script,'--json'],capture_output=True,text=True,check=True)
record=json.loads(run.stdout);assert record['exitCode']==0,record
data=json.loads(record['text']);assert not data['errors'] and len(data['ui'])==161
(B/(name+'-browser.cli.json')).write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
(B/(name+'-runtime.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
assert len(record['images'])==1
shutil.copyfile(record['images'][0]['path'],B/('cocos-'+name+'.jpg'))
print(json.dumps({'view':view,'screenshot':str(B/('cocos-'+name+'.jpg')),'actualStaticNodes':len(data['ui']),'textures':data['textures'],'activeGround':data['ground']},ensure_ascii=False))
