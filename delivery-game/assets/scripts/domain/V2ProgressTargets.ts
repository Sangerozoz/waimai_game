import { cheapestUnhiredRider } from './V2RiderEconomy';
import { V2EconomyState } from './V2EconomySession';
import { V2_CONFIG as C } from './V2EconomyConfig';
export interface V2ProgressTarget { id:string;label:string;completed:boolean;priceCents:number|null;shortfallCents:number;canGo:boolean;destination:'vehicles'|'riders'|'maps';progress:number;target:number;hint:string }
/** Recommendations only: no purchase, qualification, reward or mandatory spending order. */
export function queryProgressTargets(s:Readonly<V2EconomyState>):V2ProgressTarget[] {
 const result:V2ProgressTarget[]=[];
 const add=(id:string,label:string,progress:number,target:number,priceCents:number|null,destination:V2ProgressTarget['destination'],hint:string)=>{
  const completed=progress>=target;result.push({id,label,progress:Math.min(progress,target),target,priceCents,completed,shortfallCents:completed||priceCents===null?0:Math.max(0,priceCents-s.cashCents),canGo:!completed&&(priceCents===null||s.cashCents>=priceCents),destination,hint});
 };
 const nextHire=cheapestUnhiredRider(s.riders)?.priceCents??null;
 const paidModels=new Set(s.vehicles.filter(v=>typeof v.modelId==='number').map(v=>v.modelId));
 add('first-car','首辆新车',paidModels.size?1:0,1,C.vehicles[0].price*100,'vehicles','推荐街行300金币；约10单是引导目标，金币足够可随时购买。');
 add('first-npc','首位NPC',s.hireCount,1,nextHire,'riders','最便宜未招募人物报价，旧车可复用；人物按固定身份定价。');
 // The free initial map never satisfies the first purchased-map milestone.
 const paidMaps=C.maps.filter(m=>m.id!==C.maps[0].id&&m.price>0);
 const ownsPaidMap=paidMaps.some(m=>s.ownedMapIds.includes(m.id));
 const unownedPaidMaps=paidMaps.filter(m=>!s.ownedMapIds.includes(m.id));
 const nextPaidMapPrice=unownedPaidMaps.length?Math.min(...unownedPaidMaps.map(m=>m.price))*100:null;
 add('first-paid-map','首张付费地图',ownsPaidMap?1:0,1,nextPaidMapPrice,'maps','按实际拥有的付费地图判断完成；展示最便宜未购付费地图报价，可忽略，不强制消费。');
 const equipped=s.riders.filter(r=>r.id!=='hero'&&r.vehicleId!==null).length;
 add('first-squad','建立3名NPC配车小队',equipped,3,s.hireCount<3?nextHire:null,'riders','20分钟是推荐操作路径的设计目标；招募后需配车，不强制购买顺序。');
 add('four-maps','拥有至少4张地图',s.ownedMapIds.length,4,s.ownedMapIds.length<4?Math.min(...C.maps.filter(m=>!s.ownedMapIds.includes(m.id)).map(m=>m.price))*100:null,'maps','数量目标4/5；可自由选择先购买任意地图。');
 add('twenty-four-npc','招募24名NPC',s.hireCount,24,s.hireCount<24?nextHire:null,'riders','前段80%数量目标，展示最低未招募人物固定报价；不增加资格门槛。');
 add('eight-models','拥有前8款车型',C.vehicles.slice(0,8).filter(v=>paidModels.has(v.id)).length,8,C.vehicles.slice(0,8).find(v=>!paidModels.has(v.id))?.price!==undefined?C.vehicles.slice(0,8).find(v=>!paidModels.has(v.id))!.price*100:null,'vehicles','前段车型数量目标，重复车辆仍保留；消费由玩家确认。');
 add('full-team','招募30名NPC',s.hireCount,30,s.hireCount<30?nextHire:null,'riders','后段长期目标，不阻止继续配送、购车、买图或升级。');
 return result;
}
