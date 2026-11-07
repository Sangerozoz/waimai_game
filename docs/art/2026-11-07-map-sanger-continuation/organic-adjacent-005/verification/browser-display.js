const p=await browser.getPage('main');
const checks=[];
function need(label,ok,details){checks.push({label,passed:!!ok,details});if(!ok)throw new Error(label+': '+JSON.stringify(details));}
async function click(label){const s=await p.snapshot();const line=s.split('\n').find(x=>x.includes('button "'+label+'"'));const m=line&&line.match(/\[ref=(e\d+)\]/);if(!m)throw new Error('Missing button '+label);await p.click('ref/'+m[1]);}
async function state(){return p.evaluate(async()=>{const im=document.getElementById('art');await im.decode();return{...window.map005ViewerState,naturalSize:[im.naturalWidth,im.naturalHeight],imageCSSWidth:im.getBoundingClientRect().width,pageWidth:document.documentElement.scrollWidth,viewport:innerWidth,polylines:document.getElementById('overlay').children.length,caption:document.getElementById('caption').textContent,diagnosticVisible:!document.getElementById('diagnostic').hidden};});}
await p.setViewport({width:1100,height:900});
await p.goto('http://127.0.0.1:4199/organic-adjacent-005/');
let s=await state();need('005 native decoded with overlays initially off',s.active==='005'&&JSON.stringify(s.naturalSize)==='[1671,941]'&&s.polylines===0&&s.route===null&&s.pageWidth<=s.viewport,s);
await p.shot({type:'jpeg',maxEdge:760,quality:45});
await click('实际描线');s=await state();need('005 partial graph has26 edges',s.renderedRoadEdges===26&&s.polylines===26,s);
await click('主路径');s=await state();need('005 main route separate overlay',s.route==='main'&&s.polylines===28&&s.routeLengthPixels>1500,s);
await click('绕行路径');s=await state();need('005 exclusion reroute shown',s.route==='alternative'&&s.routeLengthPixels>2000,s);
await click('005结构底稿');s=await state();need('design distinguished and navigation disabled',s.active==='guide'&&s.polylines===0&&s.route===null&&s.caption.includes('不是原图实际街坊数'),s);
need('design route controls disabled',await p.evaluate(()=>[...document.querySelectorAll('[data-route]')].every(b=>b.disabled)&&document.getElementById('roads').disabled));
await click('004已认可');s=await state();need('004 source exact size and partial scope',s.active==='004'&&JSON.stringify(s.naturalSize)==='[1672,941]'&&s.renderedRoadEdges===4&&s.route===null&&s.caption.includes('部分主路'),s);
await click('接续诊断');s=await state();need('pair is visibly diagnostic with30 partial edges',s.active==='pair'&&JSON.stringify(s.naturalSize)==='[3192,941]'&&s.diagnosticVisible&&s.wholeSeamReady===false&&s.renderedRoadEdges===30,s);
need('pair alternative has expected geometric length',s.route==='alternative'&&Math.abs(s.routeLengthPixels-3605.3342561521013)<1e-8,s);
await p.shot({type:'jpeg',maxEdge:760,quality:45});
await click('主路径');s=await state();need('pair main has expected geometric length',s.route==='main'&&Math.abs(s.routeLengthPixels-3104.134459187516)<1e-8,s);
await click('005新原图');await click('原生大小');
const one=await p.evaluate(async()=>{await document.getElementById('art').decode();const box=document.getElementById('viewport');box.scrollLeft=820;return{width:document.getElementById('art').getBoundingClientRect().width,scroll:box.scrollLeft,pageWidth:document.documentElement.scrollWidth,viewport:innerWidth};});
need('one source pixel per CSS pixel with internal scrolling',one.width===1671&&one.scroll>500&&one.pageWidth<=one.viewport,one);
await p.shot({type:'jpeg',maxEdge:760,quality:45});
await click('适应宽度');await click('实际描线');await click('主路径');
await p.setViewport({width:375,height:850});s=await state();need('mobile fits and restores unobstructed artwork',s.active==='005'&&s.polylines===0&&s.imageCSSWidth===343&&s.pageWidth<=375,s);
await p.shot({type:'jpeg',maxEdge:560,quality:45});
console.log('MAP005_DISPLAY_CHECKS='+JSON.stringify({status:'passed',checks,meaning:'standalone map display only; CSS pixel scale is not device/DPR or game approval',formalGameTestsPerformed:false}));
