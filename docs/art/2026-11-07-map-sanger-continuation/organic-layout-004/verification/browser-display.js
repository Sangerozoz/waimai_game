const p=await browser.getPage('main');
const checks=[];
function need(label,ok,details){checks.push({label,passed:!!ok,details});if(!ok)throw new Error(label+': '+JSON.stringify(details));}
async function click(label){const s=await p.snapshot();const line=s.split('\n').find(x=>x.includes('button "'+label+'"'));const m=line&&line.match(/\[ref=(e\d+)\]/);if(!m)throw new Error('Missing button '+label);await p.click('ref/'+m[1]);}
await p.setViewport({width:1000,height:880});
await p.goto('file:///Users/sanger/Documents/ChatGPT/taptap%202/docs/art/2026-11-07-map-sanger-continuation/organic-layout-004/index.html');
const native=await p.evaluate(async()=>{const im=document.getElementById('art');await im.decode();return{size:[im.naturalWidth,im.naturalHeight],active:window.artViewerState.active,pageWidth:document.documentElement.scrollWidth,viewport:innerWidth};});
need('new native decoded in comparison page',JSON.stringify(native.size)==='[1672,941]'&&native.active==='native'&&native.pageWidth<=native.viewport,native);
await p.shot({type:'jpeg',maxEdge:900,quality:66});
await click('结构底稿');
const guide=await p.evaluate(async()=>{const im=document.getElementById('art');await im.decode();return{size:[im.naturalWidth,im.naturalHeight],active:window.artViewerState.active,caption:document.getElementById('caption').textContent};});
need('guide clearly distinguished from actual tracing',JSON.stringify(guide.size)==='[1672,941]'&&guide.active==='guide'&&guide.caption.includes('不等于实际道路描线'),guide);
await click('旧25图总览参考');
const legacy=await p.evaluate(async()=>{const im=document.getElementById('art');await im.decode();return{size:[im.naturalWidth,im.naturalHeight],active:window.artViewerState.active,caption:document.getElementById('caption').textContent};});
need('legacy overview decoded and nominal placement qualified',JSON.stringify(legacy.size)==='[1152,1200]'&&legacy.active==='legacy'&&legacy.caption.includes('不作为实测配准'),legacy);
await click('新原生图');await click('原生大小');
const one=await p.evaluate(async()=>{await document.getElementById('art').decode();const box=document.getElementById('viewport');box.scrollLeft=670;return{imageCSSWidth:document.getElementById('art').getBoundingClientRect().width,scroll:box.scrollLeft,state:window.artViewerState,pageWidth:document.documentElement.scrollWidth,viewport:innerWidth};});
need('native viewed at one source pixel per CSS pixel with internal horizontal scrolling',one.imageCSSWidth===1672&&one.scroll>600&&one.pageWidth<=one.viewport,one);
await p.shot({type:'jpeg',maxEdge:900,quality:66});
await click('适应宽度');await p.setViewport({width:375,height:850});
const mobile=await p.evaluate(()=>({imageCSSWidth:document.getElementById('art').getBoundingClientRect().width,pageWidth:document.documentElement.scrollWidth,viewport:innerWidth}));
need('375 CSS pixel layout fits without page overflow',mobile.imageCSSWidth===375&&mobile.pageWidth<=mobile.viewport,mobile);
await p.shot({type:'jpeg',maxEdge:600,quality:66});
console.log('ORGANIC_DISPLAY_CHECKS='+JSON.stringify({status:'passed',checks,meaning:'standalone comparison display; one-to-one means source pixel per CSS pixel, not DPR or game/device approval',formalGameTestsPerformed:false}));
