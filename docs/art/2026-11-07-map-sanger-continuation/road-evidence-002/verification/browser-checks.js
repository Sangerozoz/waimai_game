const p = await browser.getPage('main');
const records = [];
function requireTrue(label, condition, details) {
  if (!condition) throw new Error(label + ': ' + JSON.stringify(details));
  records.push({label, passed: true, details});
}
async function clickButton(label) {
  const snapshot = await p.snapshot();
  const line = snapshot.split('\n').find(line => line.includes('button "' + label + '"'));
  const ref = line && line.match(/\[ref=(e\d+)\]/);
  if (!ref) throw new Error('No fresh button ref: ' + label);
  await p.click('ref/' + ref[1]);
}
await p.goto('file:///Users/sanger/Documents/ChatGPT/taptap%202/docs/art/2026-11-07-map-sanger-continuation/road-evidence-002/index.html');
await p.setViewport({width: 960, height: 900});
const native = await p.evaluate(async () => {
  const im = new Image(); im.src = document.querySelector('#actualSvg image').getAttribute('href');
  await im.decode(); return [im.naturalWidth, im.naturalHeight];
});
requireTrue('native image decoded without resizing the file', native[0] === 1672 && native[1] === 941, native);
const initial = await p.evaluate(() => ({roads:document.querySelectorAll('#roads polyline').length, actual:document.querySelectorAll('#cells polygon').length, planning:document.querySelectorAll('#planCells polygon').length, main:document.getElementById('routeInfo').textContent}));
requireTrue('rendered graph and block counts', initial.roads === 38 && initial.actual === 8 && initial.planning === 64, initial);
await clickButton('单边排除后替代路径');
const alternative = await p.evaluate(() => ({text:document.getElementById('routeInfo').textContent, ids:window.activeRouteIds}));
requireTrue('alternative route excludes h-0-1', alternative.text.includes('1714.2') && !alternative.ids.includes('h-0-1'), alternative);
await p.shot({type:'jpeg', maxEdge:960, quality:65});
await clickButton('道路中心线');
const hidden = await p.evaluate(() => ({pressed:document.getElementById('toggleRoads').getAttribute('aria-pressed'), display:getComputedStyle(document.getElementById('roads')).display}));
requireTrue('roads toggle hides overlay', hidden.pressed === 'false' && hidden.display === 'none', hidden);
await clickButton('道路中心线');
await clickButton('原生 1:1 检视');
const oneToOne = await p.evaluate(() => {
  const v=document.getElementById('nativeViewport'); v.scrollLeft=600; v.scrollTop=180;
  return {svgWidth:document.getElementById('actualSvg').getBoundingClientRect().width, scrollWidth:v.scrollWidth, scrollLeft:v.scrollLeft, viewportWidth:innerWidth, bodyWidth:document.documentElement.scrollWidth};
});
requireTrue('native view uses 1672 CSS pixels with internal scrolling', oneToOne.svgWidth === 1672 && oneToOne.scrollLeft === 600 && oneToOne.bodyWidth <= oneToOne.viewportWidth, oneToOne);
await p.shot({type:'jpeg', maxEdge:960, quality:65});
await clickButton('原生 1:1 检视');
await clickButton('几何主路径');
await p.setViewport({width:375, height:900});
const actualSelection = await p.evaluate(() => {
  document.querySelector('#cells polygon[data-block="B-04-06"]').dispatchEvent(new MouseEvent('click',{bubbles:true}));
  return {block:window.selectedActualBlock, label:document.getElementById('actualInfo').textContent, route:document.getElementById('routeInfo').textContent, viewportWidth:innerWidth, bodyWidth:document.documentElement.scrollWidth};
});
requireTrue('actual block DOM click and 375px main route display', actualSelection.block === 'B-04-06' && actualSelection.label.includes('住宅') && actualSelection.route.includes('1705.3') && actualSelection.bodyWidth <= 375, actualSelection);
await p.shot({type:'jpeg', maxEdge:960, quality:65});
await clickButton('整城规划／净地账');
const planSelection = await p.evaluate(() => {
  document.querySelector('#planCells polygon[data-block="B-05-05"]').dispatchEvent(new MouseEvent('click',{bubbles:true}));
  return {block:window.selectedPlanBlock,label:document.getElementById('planInfo').textContent,share:document.getElementById('resShare').textContent,rows:document.querySelectorAll('#landRows tr').length,actualHidden:document.getElementById('actualPanel').classList.contains('hidden'),planHidden:document.getElementById('planPanel').classList.contains('hidden'),viewportWidth:innerWidth,bodyWidth:document.documentElement.scrollWidth};
});
requireTrue('planning tab selection, denominator display and contained table', planSelection.block === 'B-05-05' && planSelection.share === '50.10%' && planSelection.rows === 5 && planSelection.actualHidden && !planSelection.planHidden && planSelection.bodyWidth <= 375, planSelection);
await p.shot({type:'jpeg', maxEdge:960, quality:65});
console.log('BROWSER_CHECKS=' + JSON.stringify({status:'passed',checks:records,formalGameTestsPerformed:false,blockSelectionMethod:'DOM MouseEvent handlers; buttons clicked through fresh snapshot refs',nativeOneToOneMeaning:'one source pixel per CSS pixel; no DPR/game acceptance'}));
