const p=await browser.getPage('main');
const result=await p.evaluate(async()=>{
 const profile=globalThis.__lightProfile,r=profile.runtime;profile.running=false;profile.observer.disconnect();
 const snapshot=r.snapshot,e=snapshot.economy.state,ledger=e.ledger;
 const raw=localStorage.getItem('delivery-county-single-slot-v1'),{V2GameSession}=await System.import('chunks:///_virtual/V2GameSession.ts');
 V2GameSession.restore(r.ports.city,raw,{preserveClock:true});
 return {lastError:r.lastError,route:{tripId:r.routeMotion.tripId,phase:r.routeMotion.phase,cursor:r.routeMotion.cursor,serviceCharged:r.routeMotion.serviceCharged,serviceSeconds:r.routeMotion.serviceSeconds,position:r.routeMotion.position},follow:profile.ui.map.isFollowing,
 heroCompletedOrders:e.heroCompletedOrders,npcCompletedOrders:e.npcCompletedOrders,cashCents:e.cashCents,ledgerCashCents:ledger.entries.reduce((sum,x)=>sum+x.amountCents,ledger.opening.balanceCents),ledgerIdsUnique:new Set(ledger.entries.map(x=>x.id)).size===ledger.entries.length,settledIdsUnique:new Set(e.settledOrderIds).size===e.settledOrderIds.length,slotMatchesLastPublished:raw===r.committed,fullCurrentSlotRestore:true};
});
JSON.stringify({result,errorCount:p.__profileErrors?.length??0,errorHead:(p.__profileErrors||[]).slice(0,3).map(x=>x.slice(0,400))});
