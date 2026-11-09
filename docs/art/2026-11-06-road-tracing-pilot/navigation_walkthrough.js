const p = await browser.getPage('main');
async function clickPixel(x, y) {
  const q = await p.evaluate(([x, y]) => {
    const svg = document.getElementById('map');
    const point = svg.createSVGPoint(); point.x = x; point.y = y;
    const screen = point.matrixTransform(svg.getScreenCTM());
    return {x: screen.x, y: screen.y};
  }, [x, y]);
  await p.mouse.click(q.x, q.y);
}
async function state() { return await p.evaluate(() => globalThis.__navDemo.getState()); }
await p.click('#demo');
await p.click('#play');
const before = await state();
await new Promise(resolve => setTimeout(resolve, 1000));
const after = await state();
await p.click('#play');
// Exercise actual mouse input and the app's screen-to-image transform.
await clickPixel(650, 303);
await clickPixel(875, 940);
const custom = await state();
await clickPixel(270, 795);
const rejectedLane = await state();
await clickPixel(400, 571);
await clickPixel(600, 591);
const sameEdge = await state();
await clickPixel(600, 591);
await clickPixel(400, 571);
const reverseSameEdge = await state();
console.log(JSON.stringify({before, after, custom, rejectedLane, sameEdge, reverseSameEdge}));
await p.click('#demo');
await p.click('#play');
await new Promise(resolve => setTimeout(resolve, 1600));
await p.shot({type: 'jpeg', maxEdge: 1280, quality: 80});
undefined;
