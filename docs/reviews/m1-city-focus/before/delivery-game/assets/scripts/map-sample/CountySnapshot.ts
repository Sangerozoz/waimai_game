import type { AcceptedDelivery, CountySnapshot, DeliveryOffer } from './OrderBook';
import { CityData } from './MapTypes';
import { getExperienceLevel, Player } from '../domain/GameConfig';
import { countyDamageChance, countySettlement, legacyCountySettlement } from './CountyRules';
import { COUNTY_VEHICLES, countyExperienceLevel } from './CountyConfig';
import { deliveryTiming, legacyDeliveryTiming, PICKUP_STOP_SECONDS } from './DeliveryClock';
import { validateBillingSnapshot } from './DeliveryLedger';

export function countyMapId(data:CityData):string {
  let hash=2166136261;
  const add=(s:string)=>{for(let i=0;i<s.length;i++)hash=Math.imul(hash^s.charCodeAt(i),16777619);};
  for(const n of data.nodes)add(`${n.id}:${n.x}:${n.y};`);
  for(const r of data.roads)add(`${r.id}:${r.direction}:${r.speed}:${r.nodes.join(',')};`);
  for(const p of data.pois)add(`${p.node}:${p.kind};`);
  if(data.placeCatalogVersion===3)add(`dispatch-v3:${JSON.stringify(data.dispatchBounds)}:${(data.operatingPOIs||[]).join(',')};`);
  return (hash>>>0).toString(16);
}
function valid(value:unknown,detail:string):asserts value{if(!value)throw new Error('存档校验失败：'+detail);}
function object(value:unknown):value is Record<string,unknown>{return value!==null&&typeof value==='object'&&!Array.isArray(value);}
function number(value:unknown,min:number,max=Number.MAX_SAFE_INTEGER):value is number{return typeof value==='number'&&Number.isFinite(value)&&value>=min&&value<=max;}
function integer(value:unknown,min:number,max=Number.MAX_SAFE_INTEGER):value is number{return number(value,min,max)&&Number.isSafeInteger(value);}
function player(value:unknown,legacy:boolean):asserts value is Player {
  valid(object(value),'玩家');valid(integer(value.cashCents,0),'金额');valid(integer(value.rating,20,100),'评价');
  valid(integer(value.completedOrders,0)&&integer(value.experience,0)&&value.experience===value.completedOrders*10,'经验与单数');
  valid(value.level===(legacy?getExperienceLevel:countyExperienceLevel)(value.experience),'经验等级');valid(value.vehicleTier===1||value.vehicleTier===2,'县城车辆档位');valid(value.stationLevel===1,'站点');
}
function offer(value:unknown,data:CityData):asserts value is DeliveryOffer {
  valid(object(value),'订单');valid(typeof value.id==='string'&&/^CC-[1-9]\d*$/.test(value.id),'订单编号');
  valid(integer(value.from,0,data.pois.length-1)&&data.pois[value.from].kind==='restaurant','商家');
  valid(integer(value.to,0,data.pois.length-1)&&data.pois[value.to].kind!=='restaurant','顾客');
  valid(value.from!==value.to,'配送地点');valid(typeof value.food==='string'&&value.food.length>0&&typeof value.tag==='string','餐品');
  valid(integer(value.feeCents,1500,2500),'县城基础价');valid(number(value.weightKg,.5,80)&&Number.isInteger(value.weightKg*2),'重量');
  valid(value.type==='normal'||value.type==='urgent','订单类型');valid(['normal','durable','fragile'].indexOf(value.fragility as string)>=0,'易损类型');
  valid(value.demand==='none'||value.demand==='door','顾客需求');
}
export function validateCountySnapshot(data:CityData,value:unknown):asserts value is CountySnapshot {
  valid(object(value)&&(value.version===1||value.version===2||value.version===3),'版本');valid(value.mapId===countyMapId(data)||(data.legacyMapIds||[]).indexOf(value.mapId as string)>=0,'路网已变化');
  player(value.player,value.version!==3);valid(integer(value.sequence,1),'订单序号');valid(typeof value.tutorialComplete==='boolean'&&value.tutorialComplete===(value.player.completedOrders>0),'引导标记');
  if(value.billing!==undefined)validateBillingSnapshot(value.billing,value.player.completedOrders);
  const nodes=new Map(data.nodes.map(n=>[n.id,n]));valid(typeof value.currentNode==='string'&&nodes.has(value.currentNode),'骑手位置');
  valid(Array.isArray(value.offers)&&value.offers.length===(value.version===1?30:10),'候选订单数量');value.offers.forEach(o=>offer(o,data));
  const offers=value.offers as DeliveryOffer[],ids=offers.map(o=>o.id);valid(new Set(ids).size===ids.length,'重复订单');
  valid(Array.isArray(value.recent)&&value.recent.length<=20&&value.recent.every(i=>integer(i,0,data.pois.length-1)),'近期地点');
  if(value.lobbyHistory!==undefined)valid(Array.isArray(value.lobbyHistory)&&value.lobbyHistory.length<=20&&value.lobbyHistory.every(i=>integer(i,0,data.pois.length-1)),'大厅地点轮换');
  valid(object(value.daily)&&typeof value.daily.day==='string'&&/^\d{4}-\d{1,2}-\d{1,2}$/.test(value.daily.day)&&integer(value.daily.used,0,2),'刷新次数');
  const capacity=COUNTY_VEHICLES[value.player.vehicleTier-1].capacityKg;
  for(let i=0;i<offers.length;i+=5)valid(offers.slice(i,i+5).filter(o=>o.weightKg<=capacity).length>=3,'可接单容量保证');
  if(value.active!==null){
    valid(object(value.active),'当前订单');const raw=value.active;offer(raw.offer,data);
    valid(value.version!==3||raw.ruleVersion===1||raw.ruleVersion===2,'履约规则版本');
    const legacy=value.version!==3||raw.ruleVersion===1;player(raw.playerBefore,legacy);
    valid(['routes','running','paused','arrived','done'].indexOf(raw.mode as string)>=0,'配送状态');
    valid(Array.isArray(raw.routes)&&raw.routes.length>=1&&raw.routes.length<=3,'路线候选');
    valid(integer(raw.selected,0,raw.routes.length-1)&&number(raw.elapsed,0)&&number(raw.deadlineSeconds,1),'当前进度');
    const active=raw as unknown as AcceptedDelivery;
    valid(active.offer.weightKg<=capacity,'当前订单超载');
    const roads=new Map(data.roads.map(r=>[r.id,r])),edges=new Set<string>();
    for(const r of data.roads)for(let i=1;i<r.nodes.length;i++){
      if(r.direction!==-1)edges.add(`${r.id}/${r.nodes[i-1]}/${r.nodes[i]}`);
      if(r.direction!==1)edges.add(`${r.id}/${r.nodes[i]}/${r.nodes[i-1]}`);
    }
    for(const route of active.routes){
      valid(object(route)&&['fast','main','smooth'].indexOf(route.preference)>=0,'路线偏好');
      valid(Array.isArray(route.nodes)&&Array.isArray(route.points)&&Array.isArray(route.segments)&&route.segments.length>0,'路径数据');
      valid(route.nodes.length===route.points.length&&route.nodes.length===route.segments.length+1,'路径点数');
      valid(integer(route.pickupIndex,0,route.nodes.length-1)&&route.nodes[route.pickupIndex]===data.pois[active.offer.from].node,'取餐途经点');
      valid(route.nodes[route.nodes.length-1]===data.pois[active.offer.to].node,'送达终点');
      let metres=0,seconds=0;
      for(let i=0;i<route.nodes.length;i++){
        const n=nodes.get(route.nodes[i]),point=route.points[i];
        valid(n&&Array.isArray(point)&&point.length===2&&point[0]===n.x&&point[1]===n.y,'道路坐标');
        if(i===0)continue;
        const a=nodes.get(route.nodes[i-1])!,s=route.segments[i-1];valid(object(s),'分段');
        const road=roads.get(s.road),distance=Math.hypot(n.x-a.x,n.y-a.y);
        valid(road&&s.from===a.id&&s.to===n.id&&edges.has(`${s.road}/${s.from}/${s.to}`),'道路连接方向');
        valid(number(s.metres,Number.MIN_VALUE)&&number(s.seconds,Number.MIN_VALUE)&&Math.abs(s.metres-distance)<1e-6&&Math.abs(s.seconds-distance/road.speed)<1e-6&&s.roughness===road.roughness,'道路时间');
        metres+=s.metres;seconds+=s.seconds;
      }
      valid(Math.abs(route.metres-metres)<1e-5&&Math.abs(route.seconds-seconds)<1e-5,'路线合计');
      valid(route.risk===countyDamageChance(route.preference,active.offer.fragility),'餐损概率');
      valid(route.nodes[0]===active.routes[0].nodes[0],'路线起点');
    }
    const vehicle=COUNTY_VEHICLES[active.playerBefore.vehicleTier-1];
    const timingFor=(route:typeof active.routes[number])=>legacy?legacyDeliveryTiming(route.seconds,vehicle.speedMultiplier):deliveryTiming(route.metres,vehicle.speedKph);
    const timing=timingFor(active.routes[active.selected]);
    if(active.damageNoticeShown!==undefined){
      valid(typeof active.damageNoticeShown==='boolean','餐损提示状态');
      if(active.damageNoticeShown)valid(active.mode!=='routes'&&active.damage!==null&&active.damage!=='none','餐损提示结果');
    }
    if(active.pickupWaitElapsed!==undefined){
      valid(!legacy&&number(active.pickupWaitElapsed,0,PICKUP_STOP_SECONDS),'取餐停顿');
      const route=active.routes[active.selected],pickup=route.segments.slice(0,route.pickupIndex||0).reduce((n,s)=>n+s.metres,0),at=timing.animationSeconds*pickup/route.metres;
      if(active.elapsed<at-1e-8)valid(active.pickupWaitElapsed===0,'提前取餐');
      if(active.elapsed>at+1e-8||active.mode==='arrived'||active.mode==='done')valid(active.pickupWaitElapsed===PICKUP_STOP_SECONDS,'取餐尚未完成');
      if(active.mode==='routes')valid(active.pickupWaitElapsed===0,'未出发取餐');
    }
    const fastest=Math.min(...active.routes.map(r=>timingFor(r).displaySeconds));
    valid(active.deadlineSeconds===fastest+(active.offer.type==='urgent'?0:300),'时限');
    valid(active.elapsed<=timing.animationSeconds,'动画进度');
    valid(active.playerBefore.vehicleTier===value.player.vehicleTier,'配送中车辆变化');
    if(active.mode==='routes')valid(active.elapsed===0&&active.damage===null&&active.receipt===null,'未出发状态');
    else{
      valid(['none','minor','moderate','severe'].indexOf(active.damage as string)>=0,'出发固定餐损');
      if(active.mode==='running'||active.mode==='paused')valid(active.elapsed<timing.animationSeconds&&active.receipt===null,'途中状态');
      else valid(active.elapsed===timing.animationSeconds,'到达状态');
    }
    if(active.mode==='done'){
      valid(ids.indexOf(active.offer.id)<0&&object(active.receipt)&&object(active.receipt.outcome),'回执');
      const outcome=active.receipt.outcome;
      valid((outcome.doorAnswer===null||typeof outcome.doorAnswer==='boolean')&&outcome.displaySeconds===timing.displaySeconds&&outcome.deadlineSeconds===active.deadlineSeconds&&outcome.damage===active.damage,'回执的固定结果');
      const expected=(legacy?legacyCountySettlement:countySettlement)(active.playerBefore,active.offer,{displaySeconds:timing.displaySeconds,deadlineSeconds:active.deadlineSeconds,damage:active.damage!,doorAnswer:active.receipt.outcome.doorAnswer});
      const expectedPlayer=value.version===3?{...expected.player,level:countyExperienceLevel(expected.player.experience)}:expected.player;
      valid(JSON.stringify(expectedPlayer)===JSON.stringify(value.player),'回执玩家状态');
      for(const key of ['incomeCents','basePriceCents','ratingBefore','ratingDelta','ratingAfter','experienceGained','levelBefore','levelAfter','lateSeconds','damage','newCashCents','completedOrders','orderId'] as const)valid(active.receipt[key]===expected.receipt[key],'回执结算');
      valid(JSON.stringify(active.receipt.playerBefore)===JSON.stringify(active.playerBefore)&&Array.isArray(active.receipt.summary)&&active.receipt.summary.every(s=>typeof s==='string'),'回执说明');
    }else{
      const expectedBefore=value.version===3?{...active.playerBefore,level:countyExperienceLevel(active.playerBefore.experience)}:active.playerBefore;
      valid(JSON.stringify(expectedBefore)===JSON.stringify(value.player)&&active.receipt===null,'未结算金额');
      const pending=offers.find(o=>o.id===active.offer.id);valid(pending&&JSON.stringify(pending)===JSON.stringify(active.offer),'待接列表中的当前单');
    }
    valid(value.currentNode===(active.mode==='arrived'||active.mode==='done'?data.pois[active.offer.to].node:active.routes[0].nodes[0]),'骑手进度位置');
    ids.push(active.offer.id);
  }
  for(const id of ids)valid(Number(id.slice(3))<value.sequence,'订单序号落后');
}
