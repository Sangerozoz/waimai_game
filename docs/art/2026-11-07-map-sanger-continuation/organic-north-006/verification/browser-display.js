const p=await browser.getPage('main');const checks=[];
function need(name,ok,details){checks.push({name,passed:!!ok,details});if(!ok)throw new Error(name+': '+JSON.stringify(details));}
async function click(label){const snap=await p.snapshot(),line=snap.split('\n').find(l=>l.includes('button "'+label+'"')),m=line&&line.match(/\[ref=(e\d+)\]/);if(!m)throw new Error('Missing button '+label);await p.click('ref/'+m[1]);}
async function state(){return p.evaluate(async()=>{const im=document.getElementById('art');await im.decode();return{src:im.getAttribute('src'),size:[im.naturalWidth,im.naturalHeight],width:im.getBoundingClientRect().width,viewport:innerWidth,clientWidth:document.documentElement.clientWidth,pageWidth:document.documentElement.scrollWidth,caption:document.getElementById('caption').textContent,notice:document.querySelector('.notice').textContent,comparison:document.getElementById('comparison').textContent,scroll:document.querySelector('.viewport').scrollLeft,buttons:[...document.querySelectorAll('button')].map(b=>b.textContent)}});}
await p.setViewport({width:1100,height:900});await p.goto('http://127.0.0.1:4199/organic-north-006/');
let s=await state();need('006 actual native1672x941 default decoded',s.src==='native.png'&&JSON.stringify(s.size)==='[1672,941]'&&s.pageWidth<=s.viewport,s);
need('art review, seam and absent navigation disclosed',s.notice.includes('尚未拼接就绪')&&s.notice.includes('实际路网尚未描线')&&s.buttons.length===3,s.notice);
await p.shot({type:'jpeg',maxEdge:760,quality:45});
const sizes=await p.evaluate(async()=>{const out=[];for(const src of['inspection/006-shared-band.png','inspection/approved-shared-band.png','../organic-adjacent-005/seam-003/assembly/pair-native.png']){const im=new Image();im.src=src;await im.decode();out.push([im.naturalWidth,im.naturalHeight]);}return out;});
need('two source bands and approved pair decode at native sizes',JSON.stringify(sizes)==='[[1672,240],[1672,240],[3192,941]]',sizes);
need('shared residual accurate and limits visible',s.comparison.includes('401,280')&&s.comparison.includes('25像素')&&s.comparison.includes('56.860')&&s.comparison.includes('不证明全部无法拼接'),s.comparison);
await click('设计底稿（非导航）');s=await state();need('design clearly labelled and does not create routes',s.src==='structure-input.png'&&s.caption.includes('5个设计围合')&&s.caption.includes('不是返回图实际街坊数'),s);
await click('006原图');await click('原生大小');await p.evaluate(()=>{document.querySelector('.viewport').scrollLeft=500;document.querySelector('.viewport').scrollIntoView({block:'start'});});s=await state();need('unscaled native image uses contained scrolling',s.src==='native.png'&&s.width===1672&&s.scroll===500&&s.pageWidth<=s.viewport,s);
await p.shot({type:'jpeg',maxEdge:760,quality:45});
await click('原生大小');await p.setViewport({width:375,height:850});await p.evaluate(()=>scrollTo(0,0));s=await state();need('375CSSpx page fits and shows actual candidate',s.width===s.clientWidth-22&&s.pageWidth<=375&&s.src==='native.png',s);
await p.shot({type:'jpeg',maxEdge:560,quality:45});
console.log('MAP006_DISPLAY_CHECKS='+JSON.stringify({status:'passed',checks,userArtApproved:false,wholeSeamReady:false,actualNavigationReady:false,formalGameTestsPerformed:false,meaning:'standalone candidate display only; no game or device/DPR acceptance'}));
