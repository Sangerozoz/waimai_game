const p=await browser.getPage('main'),checks=[];
function need(name,ok,details){checks.push({name,passed:!!ok,details});if(!ok)throw new Error(name+': '+JSON.stringify(details));}
async function click(label){const snapshot=await p.snapshot(),line=snapshot.split('\n').find(l=>l.includes('button "'+label+'"')),match=line&&line.match(/\[ref=(e\d+)\]/);if(!match)throw new Error('Missing '+label);await p.click('ref/'+match[1]);}
async function state(){return p.evaluate(()=>({...window.roadTopologyView,
 renderedEdges:[...document.querySelectorAll('#map .road')].map(e=>({id:e.dataset.edgeId,from:e.dataset.from,to:e.dataset.to,points:e.getAttribute('points'),start:e.getAttribute('marker-start'),end:e.getAttribute('marker-end')})),
 renderedJunctions:[...document.querySelectorAll('#map .junction')].map(e=>({id:e.dataset.nodeId,degree:Number(e.dataset.degree)})),
 caption:document.getElementById('caption').textContent,selection:document.getElementById('selection').textContent,
 pageWidth:document.documentElement.scrollWidth,viewport:innerWidth,svgWidth:document.getElementById('map').getBoundingClientRect().width,
 frameWidth:document.querySelector('.frame').getBoundingClientRect().width}));}
await p.setViewport({width:1100,height:1000});await p.goto('http://127.0.0.1:4199/topology-rework-007/');
let s=await state();need('default new design clearly not actual map acceptance',s.active==='new'&&s.edgeCount===37&&s.nodeCount===32&&s.designOnly===true&&s.userApproved===false&&s.actualNavigationReady===false,s);
need('five-way and ordinary/skew junctions match displayed graph',s.renderedJunctions.find(j=>j.id==='J5').degree===5&&s.renderedJunctions.find(j=>j.id==='X').degree===4&&s.renderedJunctions.find(j=>j.id==='C').degree===4&&s.renderedJunctions.find(j=>j.id==='LN').degree===3&&s.renderedJunctions.find(j=>j.id==='K').degree===3,s.renderedJunctions);
need('ten outward continuation markers distinct from internal short ends',s.renderedEdges.reduce((sum,e)=>sum+Number(!!e.start)+Number(!!e.end),0)===10,s.renderedEdges.filter(e=>e.start||e.end).map(e=>e.id));
await p.shot({type:'jpeg',maxEdge:900,quality:55});
const signature=JSON.stringify(s.adjacency);await click('去掉中间折点');s=await state();need('straightening preserves every adjacency and edge ID',s.straight&&JSON.stringify(s.adjacency)===signature&&s.renderedEdges.length===37&&s.renderedEdges.every(e=>e.points.split(' ').length===2),s.caption);
await click('J5，5向连接');s=await state();need('junction details explain five connections and unverified traffic',s.selection.includes('五条不同方向')&&s.selection.includes('尚未设计')&&s.selection.includes('不是实际导航'),s.selection);
await click('006原骨架');s=await state();need('old006 view retains its21nodes25edges',s.active==='old'&&s.edgeCount===25&&s.nodeCount===21&&s.renderedEdges.length===25&&s.caption.includes('三条长横向走廊'),s);
await p.shot({type:'jpeg',maxEdge:900,quality:55});
await click('新骨架草案');s=await state();need('restoring proposal preserves all connections',s.active==='new'&&JSON.stringify(s.adjacency)===signature,s);
await click('路口标注');s=await state();need('junction labels can be hidden without editing graph',s.junctions===false&&s.renderedJunctions.length===0&&s.edgeCount===37,s);
await click('路口标注');await click('放大');s=await state();need('large diagram scrolls inside its frame',s.svgWidth===1200&&s.pageWidth<=s.viewport,s);
await click('放大');await click('去掉中间折点');await p.setViewport({width:375,height:850});s=await state();need('375CSSpx fits without altering graph',s.active==='new'&&!s.straight&&s.pageWidth<=375&&s.edgeCount===37,s);
await p.shot({type:'jpeg',maxEdge:560,quality:55});
console.log('TOPOLOGY007_DISPLAY_CHECKS='+JSON.stringify({status:'passed',checks,designOnly:true,userApproved:false,newImageRequests:0,actualMapWritten:false,formalGameTestsPerformed:false}));
