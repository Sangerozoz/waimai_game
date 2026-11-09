# 开发A：已确认剩余项收口与本批增量

线程 `thr_j9izunn7qx`，父PM `thr_axf6i4e89t`。宿主断连只中断了上轮只读回报，不是源码失败。沿用已读证据，没有重做全库审计。**当前状态：PM以 `ETA-DTO-APPROVED-1106` 冻结接口后，已实际修改Route/Game两源，完成逐单ETA/迟到只读DTO；未改UI。仅做文本diff/哈希/静态公式核对，未测试、未构建、未自判独立PASS。交回即释放本批写lease，不自行修改模式。**

下文“已实现对账”和原缺口链的行号以本批修改前SHA为准；新增实现现位于 `V2RouteSession.ts:119-132`、`V2GameSession.ts:34-50`。

## 已实现对账（3组，不重复施工）

1. 同店合并、ready/主动继续及P0运动/跟随：`V2RouteSession.ts:72-83,127-158`，`V2GameSession.ts:35-37,91`；既有 `V2GameUI.ts:603-630` 每帧motion在HUD节流之前，路线键含tripId/phase/cursor。运行案例仍deferred，不因未测改称源码缺失。
2. NPC帧内时点及双时钟快路：`V2GameSession.ts:52-98` 按wallStart+offset+elapsed推进，finish补齐NPC帧尾；`V2DispatchSession.ts:97-110,120-136` 保留clockProgress+heroCompletionEventCount双门禁、事件账目作用域及旧tick行为；`V2FleetSession.ts:29-31,62-95` 保留游标/逐笔workAt。未重复实现。
3. U22：`V2GameSession.ts:23-32,122`，`V2EconomySession.ts:9-65,177-185`，`V2DispatchSession.ts:83-94,143` 已有可信heldMetres、独立metadata、双分支及历史合同校验。价格/旧已签合同不动。

纠正映射：旧 `logic/remaining.md:14-15,40` 的NPC/分组/ready“未实施”已陈旧；`features/core-loop/remaining.md:7` 的Game3/Route1中间态陈述也已陈旧。请求的 `features/feature-matrix.md` 不存在，实际为 `feature-matrix.json`；其orders/ledger“源码已接”不代表ETA或整批UI消费链已完整。`progress-current.md:12,18,21,28` 已正确区分新源码和未测行为。本批不改这些公共文件。

## 已确认剩余（最多3项）

### 1. 本批已实施：逐单ETA/迟到只读数据（原首选缺口）

依据：正式V1 `docs/product/2026-11-02-delivery-game-product-v1.md:47-49,57,151`。修改前链：`V2GameUI.orders:518,529-535 → Runtime.routeChoices:142 → Game.routeChoices:34 → Route.choices:119-121 → makeLegs:102`。Route原来只给总路程/现实秒数；Game原来每单只给deadline，不含预计到达/迟到数据。原静态反例：不同dropoff次序的两单只有同一个全批总秒数，消费者无法得到每单实际送达顺序对应ETA；这不是某个未执行测试的失败结论。

实际最小写集为Route/Game两源及本报告；不改UI、Runtime、推进/价格/存档。以下为PM批准后实际加入的契约，不再是待实施方案：

- `Route.choices()` 每方案追加 `arrivals:{id:string;roadSeconds:number;serviceSeconds:number}[]`；按本次原有 `makeLegs(p)` 的权威legs与原Stop顺序累计到各dropoff，首腿只减一次origin.elapsed，同店pickup仅计2现实服务秒，每dropoff计1秒并包含该单自身交付服务。每个方案/估算均新建对象/数组，只含标量，不返回可变内态/几何引用。Route校验dropoff估算与本批订单ID一一对应；已存在的相同segments别名直接复用本次局部规范方案的同一份估算，不增加路由计算。
- `Game.routeChoices().orders[]` 保留id/deadline，追加 `etaRealSeconds=roadSeconds*roadTimeFactor/(40*speedRelativeToStarter)+serviceSeconds`、`etaGameSeconds=roadSeconds*roadTimeFactor+serviceSeconds*30`、`lateGameSeconds=safe?0:Math.max(0,current trip.gameSeconds+etaGameSeconds-deadlineGameSeconds)`。**etaGameSeconds是预计剩余游戏时长，不是绝对时刻，也不再除车辆speed**；只有迟到计算加当前trip.gameSeconds。Game再次校验估算与Trip订单双向完备/唯一，缺失或重复抛错，不把缺失默置0。明确为planned已知天气下连续行驶/服务的条件估计，不含玩家取餐/ready等待、未完成或未来补给、未实现随机事件、体力中途停顿，不虚报餐损概率。
- 现Runtime直接透传；当前UI不消费新字段，本批只交真实领域只读增量，不称界面已显示。只在规划查询计算，不进逐帧路径；既有合法方案去重、起步体力门禁与原时限不改。不新增持久字段或迁移/重价旧合同。

### 2. 出发前补给与期限锚点的静态缺口

依据：正式V1 `:49,59,92`。当前链：UI选择补给回首页 → `Runtime.supply/setPaused/mutate → Game.supply:40-43 → Game.tick:65 → Trip.advanceSupply:80-81`；而 `Game.acceptBatch:31 → Trip.begin:33-37` 已建立deadline，`Game.beginTrip:35` 只选路线/策略。

静态反例：Route仍planned且玩家先确认补给时，供给动作推进trip.gameSeconds，但deadline已在accept建立；正式出发前已消耗期限。尚未运行该case。此修正涉及“出发锚点”与既有planned/在途期限的兼容边界，**不能借本批冻结旧已签合同的授权自行重建期限**。拟最小为Game/Trip，需PM先冻结：新批出发锚点如何表达，旧planned与已travelling/service/ready如何区分且既有在途期限不变；必要UI planned倒计时由B另行串行。不是本批顺手改项。

### 3. 食品分类风险尚未进入权威行程

依据：正式V1 `:43,69`；冻结参数 `docs/balance/2026-11-02-product-v1/parameters.json:559-581` 已给路线/易损性基表。当前链：`V2GameUI.ts:25-27,544,580` 仅按ID映射展示餐品；`FoodCatalog.ts:4-56` 有真实fragility；`Game.acceptBatch:31 → Trip.begin:33-37 → Trip.travel:96-100 → outcome:104 → Game.completeDelivery:48-50 → Dispatch/Economy结算`，TripOrder `:14` 没有food身份/fragility，travel统一使用normal基表。

静态反例：同路/同图/相同持餐暴露的易损汤面与耐颠饭盒不会因食品类别产生不同基础风险。最小候选为Game/Trip及一个共享的纯食品映射入口，UI消费须交B协调；需先冻结可选独立版本化食品契约和旧无食品元数据在途继续旧normal规则。冻结参数是fragile 12/6/2、normal 6/3/1、durable 2/1/0%，不能误抄旧GameConfig.ROUTES的另一套数值。不得更改实际订单重量、U22报价、已存抽值或重抽旧在途结果。未实施。

## 基线与验证边界

本批两源修改前SHA（编辑前重新实读核对，无漂移）：

- `delivery-game/assets/scripts/map-sample/V2RouteSession.ts`：`7d4480870bcb128f729a0b6f2a130a590b6b4e45fea7dbc6e08d770e399a72c4`
- `delivery-game/assets/scripts/map-sample/V2GameSession.ts`：`cd94c794d12e32cbe11d6c4e3cb5a0bfded29005e4afa49b679d9d2ba3b06232`

修改后SHA：

- `delivery-game/assets/scripts/map-sample/V2RouteSession.ts`：`a4af56bfbd972bebe0fe8dd48ea17cc2aab1a1d8b122241bb9b76ebe9e3780ff`（+13/-3行，仅choices方法）。
- `delivery-game/assets/scripts/map-sample/V2GameSession.ts`：`4aedd3ee5fd37a2c68064c5dc17c57505cc8bec18b65f97b922833d25a01a7fd`（+17/-1行，仅routeChoices方法及其条件估计注释）。

编辑只用正常V4A patch；初始报告用write_file。未修改权限或用终端绕写。SDK缺真实适配（Bootstrap:36明确不可用）、五图实际运行数据/独立地图生产仍属外部；不伪造。骑手新排版/万元近似仍held；旧任务奖不能把V1旧表直接嫁接到11-04起步无返利规则，未批准奖励不发。

未运行TS、tests/typecheck/回归、Creator、游戏、接单购买、广告、真实或合成存档；未构建/部署/commit/push/派Agent。既有 `v2-product-u22-scene-1106` 不是本批产物。完成实施后仍须PM组织独立审查和必要构建，作者不关闭功能/视觉/性能验收。

## 纯静态公式与写集核对

- 对第i个dropoff，`roadSeconds=sum(从起点至i的原权威leg.seconds)-origin.elapsed`。代码仅在首腿累计时减origin.elapsed；不重新寻路、不改位置、不外推。
- `serviceSeconds=2*此前pickup Stop数+此前及本单dropoff Stop数`；按Stop而非按同店订单数计pickup。既有legacy顺序也直接使用既有Stop，不偷偷改组。
- 真实推进原道路速率为 `40*speed/roadTimeFactor`，所以道路现实耗时为基准路秒乘factor再除以 `(40*speed)`；原travel把基准路秒乘factor计入游戏时间，原serviceTime按现实服务秒乘30。新ETA分别镜像这两套单位，不把车辆speed再除到游戏时间。
- `choices.seconds` 的原Route总秒表达式、原metres表达式逐字保留；Game原总秒表达式仅把相同只读factor/speed getter提取为局部常量，运算口径不变。起步safe路程/体力筛选表达式逐字保留。
- Route choices范围内 `makeLegs` 调用点仍只有原for循环的一处，不增加每方案或每别名路由重算；无snapshot、serialize、restore、随机数或时钟新调用。只遍历已计算legs/本批订单，不进入逐帧推进路径。
- 以修改前捕获的真实文本逐段比较：Route choices之前以及beginTrip起至完整restore末尾均字节不变；Game routeChoices之前及beginTrip起至完整restore末尾均字节不变。因此ready/group、merchantKey、A-QUALITY-01、完整legs/恢复验证、U22、NPC时点/双门禁、时钟/合同推进未删除或放宽。
- Runtime、TripRules、Dispatch、Fleet、Economy、EconomyConfig、GameUI在本次修改前后SHA一致。Runtime的validate→commit→publish、唯一写者和存档槽未改。B的ApprovedSkin不在本次写集/冻结哈希清单，不干扰其并行工作。
- patch工具未运行tsc（返回Project tsconfig detected/per-file tsc skipped），但自动附带LSP提示旧`.includes`目标lib缺失；这些提示对应Game原35/78/92/101/109行，现51/94/108/117/125行，均在字节不变的旧后半类。所有includes行文本与修改前一致；没有修改lib或追修无关旧诊断。不能据此声称编译通过。

## 未执行案例（deferred）

1. 同店2/3单pickup只计一次2秒，其他商家pickup顺序及legacy逐单Stop序列；各dropoff估算包含自己的1秒服务，而不含未来Stop服务。
2. 起点在原边上且origin.elapsed非零，只扣首腿一次；零长度道路仍有真实服务耗时。
3. fast/main/smooth相同路线合并别名，逐单估算一致；不同路线的逐单送达顺序/ETA确实按本方案原legs累计。
4. 晴/雨及不同车辆speed：现实ETA随factor/speed变化，游戏ETA不除speed；已有总seconds口径不漂移。
5. safe订单即使期限算术为正也预测迟到0；普通订单临界时限、已有非零trip.gameSeconds及逐单不同deadline。
6. 缺失/重复估算拒绝而不是默置0；调用方修改返回arrivals/aliases/orders后不影响内态或下次查询；重复查询不推进时钟/随机数/存档。
7. 旧有效planned/在途存档的兼容及实际Runtime透传、新UI消费均未执行。期限锚点与食品分类问题仍是独立未实施项；本批不重建旧期限/合同，不宣称整体路线预警或UI已交付。

## 精确源码diff

以下是捕获的真实修改前全文与修改后全文生成的完整unified diff（UTF-8、结尾换行）。该diff的SHA256为 `e83ac6e7878985381ec8e12fab120c58b516ca3554a37603e8ca94ec0ca5eefc`，不是Git对未跟踪文件的空diff。

```diff
--- delivery-game/assets/scripts/map-sample/V2RouteSession.ts
+++ delivery-game/assets/scripts/map-sample/V2RouteSession.ts
@@ -116,9 +116,19 @@
   }
   return expected;
  }
- choices():{preference:Preference;aliases:Preference[];metres:number;seconds:number}[]{
-  check(this.state.phase==='planned');const choices:{preference:Preference;aliases:Preference[];metres:number;seconds:number;key:string}[]=[];
-  for(const p of ['fast','main','smooth'] as Preference[]){const legs=this.makeLegs(p),key=JSON.stringify(legs.map(l=>l.segments.map(s=>[s.from,s.to,s.road]))),same=choices.find(c=>c.key===key);if(same)same.aliases.push(p);else choices.push({preference:p,aliases:[p],metres:legs.reduce((n,l)=>n+l.metres,0)-(this.state.origin.edge?this.state.origin.edge.metres*this.state.origin.elapsed/this.state.origin.edge.seconds:0),seconds:(legs.reduce((n,l)=>n+l.seconds,0)-this.state.origin.elapsed)/40+this.serviceBudget.seconds,key});}return choices.map(({key,...rest})=>rest);
+ choices():{preference:Preference;aliases:Preference[];metres:number;seconds:number;arrivals:{id:string;roadSeconds:number;serviceSeconds:number}[]}[]{
+  check(this.state.phase==='planned');const choices:{preference:Preference;aliases:Preference[];metres:number;seconds:number;arrivals:{id:string;roadSeconds:number;serviceSeconds:number}[];key:string}[]=[];
+  for(const p of ['fast','main','smooth'] as Preference[]){
+   const legs=this.makeLegs(p),key=JSON.stringify(legs.map(l=>l.segments.map(s=>[s.from,s.to,s.road]))),same=choices.find(c=>c.key===key);
+   if(same){same.aliases.push(p);continue;}
+   let roadSeconds=0,serviceSeconds=0;const arrivals:{id:string;roadSeconds:number;serviceSeconds:number}[]=[];
+   for(let i=0;i<legs.length;i++){
+    const stop=this.state.stops[i];roadSeconds+=legs[i].seconds-(i===0?this.state.origin.elapsed:0);serviceSeconds+=stop.kind==='pickup'?2:1;
+    if(stop.kind==='dropoff')arrivals.push({id:stop.orderId,roadSeconds,serviceSeconds});
+   }
+   const ids=new Set(arrivals.map(a=>a.id));check(arrivals.length===this.state.orders.length&&ids.size===arrivals.length&&this.state.orders.every(o=>ids.has(o.id)));
+   choices.push({preference:p,aliases:[p],metres:legs.reduce((n,l)=>n+l.metres,0)-(this.state.origin.edge?this.state.origin.edge.metres*this.state.origin.elapsed/this.state.origin.edge.seconds:0),seconds:(legs.reduce((n,l)=>n+l.seconds,0)-this.state.origin.elapsed)/40+this.serviceBudget.seconds,arrivals,key});
+  }return choices.map(({key,...rest})=>rest);
  }
  beginTrip(dispatch:V2DispatchSnapshot,preference:Preference='fast'):void {
   check(this.state.phase==='planned'&&['fast','main','smooth'].includes(preference));this.assertDispatch(dispatch);
--- delivery-game/assets/scripts/map-sample/V2GameSession.ts
+++ delivery-game/assets/scripts/map-sample/V2GameSession.ts
@@ -31,7 +31,23 @@
   const trip=V2TripRules.restore(this.trip.state);trip.begin(this.dispatch.economyState.selectedMapId,candidate.progress.tripId,orders.map((o,i)=>({id:o.id,...fastest[i],fastestGameSeconds:fastest[i].gameSeconds,safe})));
   const quotes=this.dispatch.acceptBatch(orders,ordinaryPricingById);this.route=candidate;this.trip=trip;return quotes;
  }
- routeChoices(){if(this.route.progress.phase!=='planned')return [];const t=this.trip.state,safe=t.orders.every(o=>o.safe),budget=this.route.serviceBudget;return this.route.choices().filter(c=>!safe||c.metres<=1000*t.orders.length&&c.metres/1000*[2,2,3,3,4][t.mapId-1]+budget.stamina<=t.stamina).map(c=>({...c,seconds:(c.seconds-budget.seconds)*this.trip.roadTimeFactor/this.effects.speedRelativeToStarter+budget.seconds,weather:t.weather,stamina:c.metres/1000*[2,2,3,3,4][t.mapId-1]+budget.stamina,gameSeconds:t.gameSeconds,orders:t.orders.map(o=>({id:o.id,deadlineGameSeconds:o.deadlineGameSeconds}))}));}
+ /** Planned continuous travel/service only: no manual waits, supplies, future events or stamina stops. */
+ routeChoices(){
+  if(this.route.progress.phase!=='planned')return [];
+  const t=this.trip.state,safe=t.orders.every(o=>o.safe),budget=this.route.serviceBudget;
+  return this.route.choices().filter(c=>!safe||c.metres<=1000*t.orders.length&&c.metres/1000*[2,2,3,3,4][t.mapId-1]+budget.stamina<=t.stamina).map(c=>{
+   const arrivals=new Map(c.arrivals.map(a=>[a.id,a]));
+   if(c.arrivals.length!==t.orders.length||arrivals.size!==t.orders.length||!t.orders.every(o=>arrivals.has(o.id)))throw new Error('路线与订单预计到达不一致');
+   const roadTimeFactor=this.trip.roadTimeFactor,speed=this.effects.speedRelativeToStarter;
+   const orders=t.orders.map(o=>{
+    const arrival=arrivals.get(o.id)!;
+    const etaRealSeconds=arrival.roadSeconds*roadTimeFactor/(40*speed)+arrival.serviceSeconds;
+    const etaGameSeconds=arrival.roadSeconds*roadTimeFactor+arrival.serviceSeconds*30;
+    return {id:o.id,deadlineGameSeconds:o.deadlineGameSeconds,etaRealSeconds,etaGameSeconds,lateGameSeconds:o.safe?0:Math.max(0,t.gameSeconds+etaGameSeconds-o.deadlineGameSeconds)};
+   });
+   return {...c,seconds:(c.seconds-budget.seconds)*roadTimeFactor/speed+budget.seconds,weather:t.weather,stamina:c.metres/1000*[2,2,3,3,4][t.mapId-1]+budget.stamina,gameSeconds:t.gameSeconds,orders};
+  });
+ }
  beginTrip(preference:Preference='fast'){if(this.trip.state.action||!this.routeChoices().some(c=>c.aliases.includes(preference)))throw new Error('路线或当前动作不可出发');this.route.beginTrip(this.dispatch.snapshot(),preference);this.trip.choose(preference);}
  pickup(){if(this.trip.state.action)throw new Error('补给动作进行中');this.route.pickup();}
  continueTrip():void {if(this.trip.state.action)throw new Error('补给动作进行中');this.route.continueTrip();}
```
