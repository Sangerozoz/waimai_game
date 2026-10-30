async(page)=>{
 const evidence=[],out='docs/reviews/m1-order-experience/screenshots/';
 async function boot(suffix=''){await page.goto('http://127.0.0.1:4190/?'+suffix);await page.waitForFunction(()=>window.uiFixture?.ready);await page.waitForTimeout(300);}
 async function act(operation){return page.evaluate(async operation=>{const cc=await System.import('cc'),s=window.uiFixture.sample,walk=n=>[n,...n.children.flatMap(walk)],find=name=>walk(s.root).find(n=>n.name===name),click=n=>{if(!n)throw Error('Missing click node');const e={getID:()=>1,getUILocation:()=>({x:0,y:0})};n.emit(cc.Node.EventType.TOUCH_START,e);n.emit(cc.Node.EventType.TOUCH_END,e);};
 if(operation==='transfer'||operation==='door'){
  click(find('Nav-orders'));const offer=s.book.list().find(p=>operation==='transfer'?p.offer.source==='transfer':p.offer.demand==='door').offer,card=walk(s.phone.node).find(n=>n.name==='Offer-'+offer.id),scroll=card.parent.parent.getComponent(cc.ScrollView);scroll.scrollToOffset(new cc.Vec2(0,Math.min(scroll.getMaxScrollOffset().y,-card.position.y-card.getComponent(cc.UITransform).height/2)),0);window.uiFixture.target=offer.id;return {id:offer.id,source:offer.source,demand:offer.demand};
 }
 if(operation==='show-button'){
  const card=find('Offer-'+window.uiFixture.target),scroll=card.parent.parent.getComponent(cc.ScrollView);scroll.scrollToOffset(new cc.Vec2(0,Math.min(scroll.getMaxScrollOffset().y,-card.position.y+card.getComponent(cc.UITransform).height/2-scroll.node.getComponent(cc.UITransform).height)),0);
 }
 if(operation==='accept'){
  const card=find('Offer-'+window.uiFixture.target),button=card.children.find(n=>n.name.startsWith('Button-'));
  const before=s.book.serialize(),start={getID:()=>1,getUILocation:()=>({x:0,y:0})},moved={getID:()=>1,getUILocation:()=>({x:0,y:20})};button.emit(cc.Node.EventType.TOUCH_START,start);button.emit(cc.Node.EventType.TOUCH_MOVE,moved);button.emit(cc.Node.EventType.TOUCH_END,moved);if(s.book.serialize()!==before)throw Error('scroll accidentally accepted');
  click(button);if(s.book.active?.offer.id!==window.uiFixture.target)throw Error('accepted wrong order');click(button);if(s.book.active?.offer.id!==window.uiFixture.target)throw Error('double accept changed order');if(!s.city.routeOverview)throw Error('real accept did not fit');
 }
 if(operation==='close-reopen'){
  const before=s.book.serialize(),selected=s.book.active.selected;click(find('DeliverySheet').getChildByName('CloseButton'));if(find('DeliverySheet'))throw Error('sheet failed to close');if(s.book.serialize()!==before)throw Error('close changed business');click(find('Nav-orders'));if(!find('DeliverySheet')||s.book.active.selected!==selected||s.book.serialize()!==before)throw Error('order failed to reopen');
 }
 if(operation==='popups'){
  const before=s.book.serialize(),pose=JSON.stringify(s.book.riderPose),scale=s.city.scale;
  for(const key of ['vehicle','map','bills']){click(find('Nav-'+key));if(!s.modal)throw Error('missing popup '+key);s.dismissDialog();if(!find('DeliverySheet')||s.book.serialize()!==before||JSON.stringify(s.book.riderPose)!==pose||s.city.scale!==scale)throw Error('popup changed order/view '+key);}
 }
 if(operation==='manual-pan'){
  const before=s.book.serialize(),n=s.city.viewport,e=(x,y)=>({getID:()=>1,getUILocation:()=>({x,y})});n.emit(cc.Node.EventType.TOUCH_START,e(360,900));n.emit(cc.Node.EventType.TOUCH_MOVE,e(420,920));n.emit(cc.Node.EventType.TOUCH_END,e(420,920));const state=s.city.captureView();if(state.autoFit)throw Error('manual drag retained autoFit');window.uiFixture.panState=state;window.uiFixture.panBook=before;
  click(find('DeliverySheet').getChildByName('CloseButton'));click(find('Nav-orders'));const after=s.city.captureView();if(after.scale!==state.scale||JSON.stringify(after.offset)!==JSON.stringify(state.offset)||s.book.serialize()!==before)throw Error('reopen lost manual camera');return {operation,state,after};
 }
 if(operation==='check-pan'){const a=s.city.captureView(),b=window.uiFixture.panState;if(a.scale!==b.scale||JSON.stringify(a.offset)!==JSON.stringify(b.offset)||s.book.serialize()!==window.uiFixture.panBook)throw Error('resize lost pan');return {operation,view:a};}
 if(operation==='locate-pan'){const c=s.city,start=c.project(c.riderPoint),frames=[];c.locateAnimated();for(let i=1;i<=4;i++){c.advanceLocate(.15);const t=i*.25,e=t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2,p=c.project(c.riderPoint);for(let k=0;k<2;k++)if(Math.abs(p[k]-start[k]*(1-e))>1e-6)throw Error('low-scale locate convergence changed');frames.push({time:i*.15,scale:c.scale,project:p});}if(c.scale!==2||!c.isFollowing)throw Error('locate did not reach 30m');return {operation,frames};}
 if(operation==='depart'){click(find('Button-去取餐'));if(s.book.mode!=='running')throw Error('depart failed');s.book.advance(.5);s.city.setRider(s.book.riderPose.point,s.book.riderPose.angle);s.renderPanel();}
 if(operation==='bill-arrival'){
  click(find('Nav-bills'));s.book.advance(99);s.city.setRider(s.book.riderPose.point,s.book.riderPose.angle);s.renderPanel();if(s.modalKind!=='bills')throw Error('arrival replaced bill');
 }
 if(operation==='return-arrival'){s.dismissDialog();if(s.book.mode==='arrived'&&s.modalKind!=='demand')throw Error('arrival demand unreachable');}
 if(operation==='settle'){if(s.book.mode==='arrived')click(find('Button-按要求放门口'));else s.openReceipt();if(s.book.mode!=='done'||s.modalKind!=='receipt')throw Error('receipt missing');}
 if(operation==='finish'){const cash=s.book.player.cashCents,completed=s.book.completed;click(s.modal.getChildByName('DialogCard').getChildByName('CloseButton'));if(s.book.mode!=='idle'||find('DeliverySheet')||s.book.player.cashCents!==cash||s.book.completed!==completed)throw Error('receipt X did not cleanly finish');}
 return {operation,mode:s.book.mode,modal:s.modalKind,selected:s.book.active?.selected,scale:s.city.scale,follow:s.city.isFollowing,storage:window.uiFixture.storageAttempts.map(x=>({method:x.method,key:x.key}))};
 },operation);}
 for(const [width,height,safe]of [[720,1280,false],[360,560,true]]){
  await page.setViewportSize({width,height});const suffix=width+(safe?'-safe':'');await boot(safe?'safe':'');evidence.push(await act('transfer'));await page.waitForTimeout(100);await page.screenshot({path:out+'transfer-tag-'+suffix+'.png'});await act('show-button');await page.waitForTimeout(100);await page.screenshot({path:out+'transfer-button-'+suffix+'.png'});evidence.push(await act('accept'));await page.waitForTimeout(100);await page.screenshot({path:out+'transfer-accepted-'+suffix+'.png'});evidence.push(await act('close-reopen'));evidence.push(await act('popups'));await page.screenshot({path:out+'popup-return-'+suffix+'.png'});evidence.push(await act('manual-pan'));await page.setViewportSize({width:width+10,height});await page.waitForTimeout(250);evidence.push(await act('check-pan'));await page.setViewportSize({width,height});await page.waitForTimeout(250);evidence.push(await act('check-pan'));await page.screenshot({path:out+'manual-pan-restored-'+suffix+'.png'});evidence.push(await act('locate-pan'));
  await boot(safe?'safe':'');await act('door');await act('accept');evidence.push(await act('depart'));await page.screenshot({path:out+'running-'+suffix+'.png'});evidence.push(await act('bill-arrival'));await page.screenshot({path:out+'arrival-bill-'+suffix+'.png'});evidence.push(await act('return-arrival'));await page.screenshot({path:out+'arrived-'+suffix+'.png'});evidence.push(await act('settle'));await page.screenshot({path:out+'receipt-'+suffix+'.png'});evidence.push(await act('finish'));await page.screenshot({path:out+'receipt-closed-'+suffix+'.png'});
 }
 return evidence;
}
