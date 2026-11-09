const p=await browser.getPage('main');
const data=await p.evaluate(()=>globalThis.__lightProfile.windows[0]);
JSON.stringify(data);
