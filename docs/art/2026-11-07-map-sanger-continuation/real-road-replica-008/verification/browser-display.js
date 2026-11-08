const p=await browser.getPage('main'),checks=[];
function need(name,ok,detail){checks.push({name,passed:!!ok,detail});if(!ok)throw new Error(name+': '+JSON.stringify(detail))}
async function click(label){const s=await p.snapshot(),line=s.split('\n').find(l=>l.includes('button "'+label+'"')),m=line&&line.match(/\[ref=(e\d+)\]/);if(!m)throw new Error('Missing '+label);await p.click('ref/'+m[1])}
async function state(){return p.evaluate(()=>({view:document.querySelector('#map').getAttribute('viewBox').split(' ').map(Number),
 total:document.querySelectorAll('.road').length,categories:[...document.querySelectorAll('[data-category]')].map(g=>({kind:g.dataset.category,display:g.getAttribute('display'),parts:g.children.length})),
 buildingsPressed:document.querySelector('#buildings').getAttribute('aria-pressed'),joinsPressed:document.querySelector('#junctions').getAttribute('aria-pressed'),
 width:document.documentElement.scrollWidth,viewport:innerWidth,clip:document.querySelector('#source-window rect').getAttribute('width'),
 info:document.querySelector('#info').textContent,scale:document.querySelector('#scale span').textContent}))}
await p.setViewport({width:1100,height:1080});await p.goto('http://127.0.0.1:4199/real-road-replica-008/');let s=await state();
need('default complete source window and nonvehicle layer hidden',s.total===1218&&s.categories.find(g=>g.kind==='nonvehicle').display==='none'&&Math.abs(s.view[2]-1661.74)<1e-8,s);
const exact=await p.evaluate(()=>{const displayed=[...document.querySelectorAll('.road')];return D.network.parts.every(part=>{const way=D.network.ways[part.wayId],paths=displayed.filter(p=>p.dataset.way===part.wayId),wanted=part.nodes.map(id=>{const a=D.network.nodes[id].xy;return [a[0]-box[0],box[3]-a[1]].join(',')}).join(' ');return paths.some(p=>p.getAttribute('points')===wanted)})});
need('all displayed road vertices equal source data after translation and Y reflection',exact,{parts:1218});
need('context and road scene clipped to source reference bounds',Math.abs(Number(s.clip)-1661.74)<1e-8,s.clip);
await p.shot({type:'jpeg',maxEdge:900,quality:55});
await click('步行／骑行线');s=await state();need('nonvehicle lines can be shown without altering source parts',s.categories.find(g=>g.kind==='nonvehicle').display==='inline'&&s.total===1218,s.categories);
await click('已有建筑轮廓');await click('原节点交会');s=await state();need('source context and identity-based intersections toggle',s.buildingsPressed==='true'&&s.joinsPressed==='true'&&s.total===1218,s);
await click('看局部');s=await state();need('local view magnifies source coordinates and updates scale',s.view[2]===420&&s.scale.includes('50 m')&&s.total===1218,s.view);
const clicked=await p.evaluate(()=>{const road=document.querySelector('[data-category="major"] .road');road.dispatchEvent(new MouseEvent('click',{bubbles:true}));return {id:road.dataset.way,text:document.querySelector('#info').textContent,href:document.querySelector('#info a').getAttribute('href')}});
need('browser DOM road-click handler reports source way and link',clicked.text.includes(clicked.id)&&clicked.href==='https://www.openstreetmap.org/way/'+clicked.id,clicked);
await p.shot({type:'jpeg',maxEdge:900,quality:55});
await click('放大');s=await state();need('zoom control changes view without geometry mutation',s.view[2]===273&&s.total===1218,s.view);
await click('缩小');s=await state();need('reverse zoom returns local source span',Math.abs(s.view[2]-420)<1e-8,s.view);
await click('完整选区');await click('步行／骑行线');await click('已有建筑轮廓');await click('原节点交会');
await p.setViewport({width:375,height:1050});s=await state();need('mobile page fits and source geometry remains intact',s.width<=375&&s.total===1218&&s.categories.find(g=>g.kind==='nonvehicle').display==='none',s);
await p.shot({type:'jpeg',maxEdge:650,quality:55});
console.log('REAL_ROAD008_DISPLAY_CHECKS='+JSON.stringify({status:'passed',checks,sourceReferenceOnly:true,physicalRoadPointerClickTested:false,roadClickTest:'browser DOM synthetic event',formalGameTests:false}));
