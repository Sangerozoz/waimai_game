const p=await browser.getPage('main');const checks=[];
function need(label,ok,details){checks.push({label,passed:!!ok,details});if(!ok)throw new Error(label+': '+JSON.stringify(details));}
async function click(label){const snap=await p.snapshot();const line=snap.split('\n').find(x=>x.includes('button "'+label+'"'));const ref=line&&line.match(/\[ref=(e\d+)\]/);if(!ref)throw Error('No button '+label);await p.click('ref/'+ref[1]);}
await p.goto('file:///Users/sanger/Documents/ChatGPT/taptap%202/docs/art/2026-11-07-map-sanger-continuation/adjacent-pair-003/index.html');await p.setViewport({width:375,height:900});
const fit=await p.evaluate(()=>({body:document.documentElement.scrollWidth,width:innerWidth,map:document.getElementById('pairSvg').getBoundingClientRect().width,images:[...document.querySelectorAll('.raws img')].map(x=>[x.complete,x.naturalWidth,x.naturalHeight])}));
need('375 CSS viewport fit without full-page horizontal overflow',fit.body<=375&&fit.map<=375&&fit.images.every(x=>x[0]&&x[1]===1672&&x[2]===941),fit);
await click('跨区主路径');await p.shot({type:'jpeg',maxEdge:900,quality:60});
await click('查看接缝近景');
const close=await p.evaluate(()=>({body:document.documentElement.scrollWidth,width:innerWidth,map:document.getElementById('pairSvg').getBoundingClientRect().width,scroll:document.getElementById('pairViewport').scrollLeft}));
need('375 CSS native seam inspection scrolls inside image viewport',close.body<=375&&close.map===3248&&close.scroll>1300,close);
await p.shot({type:'jpeg',maxEdge:900,quality:60});
console.log('PAIR_MOBILE_CHECKS='+JSON.stringify({status:'passed',checks,formalGameTestsPerformed:false,userDeviceOrDPRNotAssumed:true}));
