const p=await browser.getPage('main');
const checks=[];
function need(name,ok,details){checks.push({name,passed:!!ok,details});if(!ok)throw new Error(name+': '+JSON.stringify(details));}
async function click(label){const snapshot=await p.snapshot();const line=snapshot.split('\n').find(l=>l.includes('button "'+label+'"'));const match=line&&line.match(/\[ref=(e\d+)\]/);if(!match)throw new Error('Missing button '+label);await p.click('ref/'+match[1]);}
async function state(){return p.evaluate(()=>({
 trace:getComputedStyle(document.getElementById('traceLayer')).display,
 blocks:getComputedStyle(document.getElementById('blockLayer')).display,
 main:getComputedStyle(document.getElementById('mainPath')).display,
 alternative:getComputedStyle(document.getElementById('alternativePath')).display,
 inference:getComputedStyle(document.getElementById('inferenceLayer')).display,
 inferredRoads:document.getElementById('inferenceLayer').children.length,
 inferredAllowed:[...document.querySelectorAll('#inferenceLayer path')].map(e=>e.getAttribute('data-navigation-allowed')),
 mainD:document.getElementById('mainPath').getAttribute('d'),alternativeD:document.getElementById('alternativePath').getAttribute('d'),
 roads:document.getElementById('traceLayer').children.length,
 newRoads:[...document.querySelectorAll('#traceLayer path')].filter(e=>e.getAttribute('stroke')==='#00d8ff').length,
 faces:document.querySelectorAll('#blockLayer path').length,
 width:document.getElementById('map').getBoundingClientRect().width,
 pageWidth:document.documentElement.scrollWidth,clientWidth:document.documentElement.clientWidth,viewport:innerWidth,
 rows:document.querySelectorAll('#objectsTable tr').length,
 objects005:document.querySelectorAll('#objects005 rect').length,
 objects004:document.querySelectorAll('#objects004 rect').length,
 objectsDisplay:getComputedStyle(document.getElementById('objects005')).display,
 text:document.getElementById('geometry').textContent,
 ownership:document.getElementById('ownershipStatus').textContent,
}));}
await p.setViewport({width:1100,height:900});
await p.goto('http://127.0.0.1:4199/organic-adjacent-005/revision-002/');
const sizes=await p.evaluate(async()=>{const result=[];for(const path of['../native.png','../../organic-layout-004/native.png']){const image=new Image();image.src=path;await image.decode();result.push([image.naturalWidth,image.naturalHeight])}return result});
let s=await state();
need('both original native images decode',JSON.stringify(sizes)==='[[1671,941],[1672,941]]',sizes);
need('default unobstructed005 image with 31 permitted edges and hidden inference',s.trace==='none'&&s.blocks==='none'&&s.main==='none'&&s.alternative==='none'&&s.inference==='none'&&s.roads===31&&s.newRoads===5&&s.inferredRoads===1&&s.pageWidth<=s.viewport,s);
need('shared fifth enclosure inference and island disclosed',s.faces===6&&s.text.includes('一处共享结构围合（含推定边界）')&&s.text.includes('一处导流岛'),s.text);
need('eight approximate object records and unresolved seam visible',s.rows===8&&s.objects005===8&&s.objects004===8&&s.ownership.includes('实际裁界未完成'),s);
await p.shot({type:'jpeg',maxEdge:760,quality:45});
await click('可见道路描线');s=await state();need('visible trace excludes roof and sidewalk-adjacent inference',s.trace!=='none'&&s.roads===31&&s.newRoads===5&&s.inference==='none',s);
await click('围合分类');s=await state();need('classification overlay independently visible',s.blocks!=='none',s);
await click('单图主路径');s=await state();need('single-native main path visible',s.main!=='none',s);
await click('单图绕行');s=await state();need('single-native alternative path visible',s.alternative!=='none',s);
const beforeInference={main:s.mainD,alternative:s.alternativeD};
await click('遮挡推定（禁导航）');s=await state();need('inference display is separately forbidden and leaves routes unchanged',s.inference!=='none'&&s.inferredRoads===1&&JSON.stringify(s.inferredAllowed)==='["false"]'&&s.mainD===beforeInference.main&&s.alternativeD===beforeInference.alternative,s);
await p.shot({type:'jpeg',maxEdge:760,quality:45});
await click('遮挡推定（禁导航）');s=await state();need('inference hidden again independently of visible roads',s.inference==='none'&&s.trace!=='none',s);
await click('原生大小');s=await state();need('native CSS scale scrolls within page',s.width===1671&&s.pageWidth<=s.viewport,s);
await click('原生大小');
await p.evaluate(()=>document.querySelector('.compare').scrollIntoView({block:'start'}));
await p.shot({type:'jpeg',maxEdge:760,quality:45});
await click('对象范围');s=await state();need('object inspection boxes can be hidden',s.objectsDisplay==='none'&&s.rows===8,s);
await click('对象范围');
for(const label of['可见道路描线','围合分类','单图主路径','单图绕行'])await click(label);
await p.setViewport({width:375,height:850});await p.evaluate(()=>scrollTo(0,0));s=await state();need('375px mobile fits and restores original artwork',s.width===s.clientWidth-22&&s.pageWidth<=s.viewport&&s.trace==='none'&&s.blocks==='none',s);
await p.shot({type:'jpeg',maxEdge:560,quality:45});
console.log('MAP005_R2_DISPLAY_CHECKS='+JSON.stringify({status:'passed',checks,formalGameTestsPerformed:false,wholeSeamReady:false,meaning:'standalone SVG display and interaction only; no source artwork modification or game/DPR certification'}));
