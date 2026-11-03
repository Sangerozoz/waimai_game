import type { DeliveryOffer } from './OrderBook';

// Source is an attribute of a newly issued local offer; no extra RNG draw.
export function newOfferSource(id:string):'direct'|'transfer' {
 if(id==='CC-1')return 'direct';
 let hash=2166136261;for(let i=0;i<id.length;i++)hash=Math.imul(hash^id.charCodeAt(i),16777619);
 return (hash>>>0)%5===0?'transfer':'direct';
}
export function offerQuantity(offer:DeliveryOffer):number|null {
 if(offer.quantity!==undefined)return offer.quantity;
 const match=/^.+\s*·\s*([1-9]\d*)份$/.exec(offer.food);
 return match&&Number.isSafeInteger(Number(match[1]))?Number(match[1]):null;
}
export function foodDescription(offer:DeliveryOffer):string {
 const quantity=offerQuantity(offer);
 if(quantity===null)return offer.food+' · 份数未提供';
 return offer.food.replace(/\s*·\s*[1-9]\d*份$/,'')+` · ${quantity}份`;
}
export function buyerRemark(offer:DeliveryOffer):string {
 return offer.buyerNote?.trim()||(offer.demand==='door'?'放门口，别敲门':'');
}
export function orderCautions(offer:DeliveryOffer):string {
 return [offer.type==='urgent'?'加急':'',offer.fragility==='fragile'?'怕洒':offer.fragility==='durable'?'耐放':'普通餐品'].filter(Boolean).join(' · ');
}
export function deadlineText(seconds:number):string{return `${Math.ceil(Math.max(0,seconds)/60)}分钟内送达`;}
