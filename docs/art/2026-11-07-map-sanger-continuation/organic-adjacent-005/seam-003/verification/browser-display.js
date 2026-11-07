const p=await browser.getPage('main');
const checks=[];
function need(name,ok,details){checks.push({name,passed:!!ok,details});if(!ok)throw new Error(name+': '+JSON.stringify(details));}
async function click(label){const snapshot=await p.snapshot();const line=snapshot.split('\n').find(l=>l.includes('button "'+label+'"'));const match=line&&line.match(/\[ref=(e\d+)\]/);if(!match)throw new Error('Missing '+label);await p.click('ref/'+match[1]);}
async function state(){return p.evaluate(()=>({
 width:document.getElementById('map').getBoundingClientRect().width,clientWidth:document.documentElement.clientWidth,pageWidth:document.documentElement.scrollWidth,viewport:innerWidth,
 cut:getComputedStyle(document.getElementById('cutPath')).display,objects:getComputedStyle(document.getElementById('objectLayer')).display,
 roads:getComputedStyle(document.getElementById('roadLayer')).display,roadCount:document.getElementById('roadLayer').children.length,
 main:getComputedStyle(document.getElementById('mainPath')).display,alternative:getComputedStyle(document.getElementById('alternativePath')).display,
 inference:getComputedStyle(document.getElementById('inferencePath')).display,inferenceAllowed:document.getElementById('inferencePath').getAttribute('data-navigation-allowed'),
 mainD:document.getElementById('mainPath').getAttribute('d'),alternativeD:document.getElementById('alternativePath').getAttribute('d'),
 cutD:document.getElementById('cutPath').getAttribute('d'),labels:document.getElementById('objectLayer').children.length,rows:document.querySelectorAll('#ownershipRows tr').length,
 caption:document.getElementById('graphCaption').textContent,note:document.querySelector('.note').textContent,
 imageHref:document.querySelector('#map image').getAttribute('href')
}));}
await p.setViewport({width:1100,height:900});
await p.goto('http://127.0.0.1:4199/organic-adjacent-005/seam-003/');
const size=await p.evaluate(async()=>{const im=new Image();im.src='assembly/pair-native.png';await im.decode();return[im.naturalWidth,im.naturalHeight]});
let s=await state();need('native candidate3192x941 decodes',JSON.stringify(size)==='[3192,941]'&&s.imageHref==='assembly/pair-native.png',size);
need('default image unobstructed and candidate status visible',s.cut==='none'&&s.objects==='none'&&s.roads==='none'&&s.main==='none'&&s.alternative==='none'&&s.inference==='none'&&s.note.includes('尚未获拼接画面验收'),s);
need('nine object sources rendered including inherited clipping',s.rows===9&&s.labels===9,s);
need('bounded26node30edge graph and new route lengths shown',s.roadCount===30&&s.caption.includes('26节点／30边')&&s.caption.includes('3104.67px')&&s.caption.includes('3605.87px'),s.caption);
await p.shot({type:'jpeg',maxEdge:760,quality:45});
await click('显示裁界');s=await state();need('editable cut overlay shown independently',s.cut!=='none'&&s.cutD.startsWith('M1630 0'),s.cutD);
await click('楼体来源');s=await state();need('source labels separately shown',s.objects!=='none'&&s.labels===9,s);
await click('部分可见路网');s=await state();need('actual partial road layer30 edges',s.roads!=='none'&&s.roadCount===30,s);
await click('跨区主路径');s=await state();need('fresh cross-region main route visible',s.main!=='none',s);
await click('断边绕行');s=await state();need('blocked-edge reroute independently visible',s.alternative!=='none',s);
const before={main:s.mainD,alternative:s.alternativeD};await click('遮挡推定（禁导航）');s=await state();need('forbidden inference toggle leaves both routes unchanged',s.inference!=='none'&&s.inferenceAllowed==='false'&&s.mainD===before.main&&s.alternativeD===before.alternative,s);
await click('遮挡推定（禁导航）');
await p.shot({type:'jpeg',maxEdge:760,quality:45});
await click('原生大小');await p.evaluate(()=>{document.querySelector('.canvas').scrollLeft=1380;document.querySelector('.canvas').scrollIntoView({block:'start'})});s=await state();need('native CSS width3192 with contained scroll',s.width===3192&&s.pageWidth<=s.viewport,s);
await p.shot({type:'jpeg',maxEdge:760,quality:45});
await click('原生大小');for(const label of['显示裁界','楼体来源','部分可见路网','跨区主路径','断边绕行'])await click(label);
await p.setViewport({width:375,height:850});await p.evaluate(()=>scrollTo(0,0));s=await state();need('375px mobile fits original candidate without overlays',s.width===s.clientWidth-22&&s.pageWidth<=s.viewport&&s.cut==='none'&&s.roads==='none'&&s.main==='none'&&s.alternative==='none'&&s.inference==='none',s);
await p.shot({type:'jpeg',maxEdge:560,quality:45});
console.log('SEAM003_DISPLAY_CHECKS='+JSON.stringify({status:'passed',checks,formalGameTestsPerformed:false,userCompositeApproved:false,wholeSeamReady:false,meaning:'map-only candidate display and interactions; source-pixel CSS width is not user-device/DPR or game acceptance'}));
