const p=await browser.getPage('main');
const data=await p.evaluate(()=>globalThis.__lightProfile.windows[2]);
JSON.stringify(data);
