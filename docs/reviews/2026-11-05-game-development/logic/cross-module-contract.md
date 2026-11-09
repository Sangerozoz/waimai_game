# 正式V1§4最小跨模块契约提案

日期：2026-11-05。提交父PM thr_axf6i4e89t；原逻辑 thr_tdwjukd785，Runtime thr_f2cxhbkw45，UI thr_uevwv32vnh。**PM续推已批准第1—5节，现进入Route/Trip/Game与Runtime/UI两写集实施；第6节NPC时点仍留下一批串行落实。批准不等于实现或通过，不要求用户重复确认既定玩法。** 当前执行范围以game-development计划“当前续推批次”为准，禁止读取/修改真实用户slot。

依据：正式V1§3/4/6/7及baseline最新反馈段、feedback-ledger U01/U02。用户禁止玩家重开，覆盖旧文档重开方案。保持原city/原路/宽度/三框、当前报价、40游戏秒/现实秒及取2送1，不用调速或瞬移掩盖卡顿。

## 1. 方案选择

推荐在现有状态机增加一个`ready`等待继续阶段，并把同商家取餐做成一个服务Stop。相比只在UI隐藏移动按钮，这会让暂停/自动/恢复都遵守同一规则；相比全面重写事件总线和路线规划器，写集和兼容面更小。先保证合法确定的取送顺序，不把本次变成全局最优排程重构。

当前证据：Route.plan固定逐单pickup/dropoff；Route.advance取餐服务结束直接travelling。Game.tick没有ready分支。UI目前只有到店取餐；`V2GameUI.ts:552`移动显示被0.5秒节流，`:556–558`更新骑手/路线；CityMap.setRoutes清除follow。卡顿/跟随由各owner处理，不把新增ready当作U01/U02全部解决。

## 2. Route/Game状态与动作

|阶段|含义及位置|手动/自动行为|
|---|---|---|
|travelling|沿当前合法leg逐段移动|保持现有真实legSeconds与position|
|pickup|停在商家、尚未确认取餐|手动pickup；自动调用相同入口|
|service|已确认取/送服务；serviceCharged持久门闩|取餐2现实秒/60游戏秒；交付1/30，不插另一动作|
|ready（新增）|取餐服务已完成，停在原商家；cursor已指向下一站，legSeconds=0|手动必须continueTrip；自动同帧显式调用continueTrip后继续|
|finished|本批逐单完成|保留首轮自动下一批串联|

新增`V2RouteSession.continueTrip():void`及`V2GameSession.continueTrip():void`。必须phase=ready且无补给action，其他阶段拒绝；仅ready→travelling，不扣费、不耗体力、不修改时限、不跳位置、不补跑等待时长。重复提交不能推动第二站；Runtime同步事务完成后UI立即根据新phase禁用旧按钮。若后续引入异步命令队列再加tripId/cursor令牌，本轮不引入该队列。

取餐服务完成：清serviceCharged/serviceSeconds，cursor前移，停在ready；`advance`立即返回真实已消耗秒数，手动本帧尾段不推进。ready等待不增加gameSeconds/里程/餐损/体力消耗，NPC仍按现实经营；不是设置全局暂停。继续按钮前Runtime先tick到实际当前时刻，因此等待时间不会被后续行动追赶。到顾客仍自动服务并逐单结算，随后自动前往计划下一站，无新增交付确认。

ready.position取已到站anchor，不能误取下一站终点；当前leg可预画，但人物不移动。恢复ready后继续等待，取消保留此站位置。auto在ready调用同一个continueTrip；权益耗尽即保留当前状态转manual，不自动代点后续动作。暂停/后台/恢复首帧逻辑不变。

## 3. 同店合并服务（最小确定排程）

Stop新增`orderIds:string[]`；保留`orderId=orderIds[0]`兼容现有主目标展示。pickup允许多成员，dropoff必须单成员。商家身份由当前权威POI解析，至少同时匹配pickupNode及其规范pickupName，不能仅凭屏幕名称合并不同地点；同节点不同商家无法确认时不合并，后续有正式merchantId再扩展。

新批规划：按所选订单首次出现的商家顺序分组；每组一个pickup Stop，随后按组内原稳定顺序逐单dropoff，再下一商家。这只是确定合法排程，不声称最优。对重排后每个有向段重新验证可达，失败整批不提交；总重量仍按整个批次比较实际容量，不借分段卸货突破容量，不改原路。

pickup一次进入服务，Route.picked加入该组全部ID。新增TripRules.pickupGroup(ids)在检查体力>=1后只扣1点并一次标记全部订单picked；Route服务门闩仍只一个。Game给Route hooks增加可选pickupGroup(ids)；多成员组必须走该hook，不能退化为循环service(id)多扣。单成员与dropoff仍可用现有service(id,kind)路径。取餐服务时间统一2秒/60游戏秒，不乘人数；每顾客交付仍逐单1点/1秒/30游戏秒。

Game恢复校验要把现有“当前pickup服务未扣点时，Route.picked已记而Trip.picked未记”的特例扩为整组，不漏一单/重复记一单。报价、每单独立期限/到达凭证/逐单收入经验都保留；仅实际共享的取餐时间和体力合并。routeChoices总服务时间改为`2×pickupStops+dropoffStops`，总服务耗能改为`pickupStops+dropoffStops`，起步阶段预算用同口径，独立最快单期限仍含自身一次取/送必要服务，不因合并虚构奖励或重建期限。

## 4. Runtime/UI最小接线

Runtime owner只新增`continueTrip()`，用现有mutate候选事务调用Game入口：同步旧时钟→执行命令→验证→唯一slot提交→发布。和pickup/beginTrip同样处理错误及后台门禁，不在Runtime直接改Route.phase。保留原公开动作方法。

UI owner在phase=ready显示“去下一站”，下一站dropoff可写“去配送”；phase=pickup仍“到店取餐”；service显示真实动作进度且不可重复点；ready可补给/暂停/取消。组pickup显示商家和件数，逐单送达不合并收据。UI不自行推cursor或将人物放到目标点。

移动显示与HUD慢刷新拆开；每帧拿当前权威position显示，不把整条leg时间当一帧delta，不在取餐点击后补跑等待区间。跟随状态由出发/用户拖动/定位明确管理，setRoutes/phase切换不能无声取消。连续显示的只读轻量接口由Runtime性能owner提供，我不写该owner文件。

## 5. 当前唯一存档兼容（提案，须统一串行实施）

建议Route snapshot version=2（Stop.orderIds、ready），Game组合version=4；TripState继续version=2，Dispatch/Fleet保持现版。新timeProfile标识`road40-service2-1-grouped-v2`，数值不变。不能让旧restore将新ready误当travelling，也不能让新组Stop被旧的orders.flatMap校验拒绝。

对**当前唯一slot现有有效组合v3/Route v1**：先执行原完整校验，再转换所有旧Stop为单成员orderIds，保留旧stops顺序/cursor/legs/legSeconds/serviceSeconds/serviceCharged、picked/arrivals、tripId及令牌；不重排在途旧批、不重算已走里程、不重开服务或重发钱/经验/额度。已travelling的旧区间继续原位置，不倒推/撤回既有出发；以后完成pickup服务进入ready。新批才按分组排程。Game.restore返回规范新结构，由Runtime已有成功载入事务写回同一个slot；失败保留原字节并拒绝载入。

新校验逐单要求恰好一次pickup成员/一次dropoff、先取后送、pickup成员商家一致、leg与权威原路完全一致；ready必须cursor有效/前一站pickup完成/anchor为该商家/legSeconds与serviceSeconds均0/无已扣未完服务，Trip/Dispatch对应状态一致。旧令牌继续按旧cursor保留；新令牌按新批tripId/Stop位置/逐单ID生成。

这是当前进度的结构升级，不读取已废弃游戏keys，不建第二slot/备份、不恢复历史经济档，不提供清档/重开入口。未来未知版本仍拒绝。组合v1/v2原有处理边界不扩大，不能借兼容伪造缺失的在途状态。

## 6. NPC帧内时点最小契约

**11-06父PM已批准本节由复用开发A实施。** 前批同店/ready、恢复互斥和轻量读取已合入；逐笔workAt归日已独立静态PASS。本批只接尚缺的帧内事件链，不迁移旧null日期，不重做resolver，不改Fleet/Runtime/Trip/UI、经济数值或持久版本。Game/Route/Dispatch为本批唯一源码写集。

问题：Dispatch.tick当前先fleet.advanceTo(frameEnd)，Game后续arrival默认frameEnd结算补额度。静态反例：额度0、帧0→60秒、主角真实第10秒完成，粗帧直到60才补；拆成0→10→60则后50秒可经营。必须按真实事件切分，不能把workAt改成整帧末尾，也不能把新额度回填到帧起。

推荐对Dispatch.tick现有options**新增可选`deferFleet?:boolean`（默认false，旧调用保持行为）**，新增`advanceFleetTo(nowSeconds):void`用于组合owner。Game调用`{deferAuto:true,deferFleet:true}`，从帧前高水位记录wallStart；Route arrival hook新增第三参数`elapsedSeconds`，是该次advance内从0开始的真实消耗时间。Game把此前已消耗的补给/路线秒数加到offset，得到`eventAt=wallStart+offset+elapsedSeconds`，不能用gameSeconds/40代替现实秒。记录的是累计已消耗时间，不能用本帧剩余量倒贴frameEnd。

每次交付按下列顺序：

1. `dispatch.completeDelivery(id,token,eventAt,outcome)`利用已有nowSeconds参数先推进NPC旧额度到eventAt，再结算主角并通过事件游标补一次。
2. 新额度仅可用于eventAt之后；接着处理后续真实到达/补给购买/下一批签约，所有影响余额/资产的帧内动作前也先advanceFleetTo其真实时刻，避免使用未来NPC收入购买早发生的补给。 主角交付和补给购买也要临时设置ledgerContext.nowMs为事件绝对毫秒，dayKey按Runtime现有本地日口径从该毫秒派生，事件后恢复帧上下文；不能只传completeDelivery的nowSeconds却仍把主角账目记在帧尾。Fleet现有逐笔workAt及已接入的日期resolver保持；无resolver仍按既有未知日期边界处理，不伪造或迁移旧null账目。
3. 帧尾统一advanceFleetTo(frameEnd)，包括主角在pickup/ready等待、零体力停住、无车、广告/后台/暂停/恢复首帧的全部退出路径；这些路径只冻结主角。相同NPC due时刻先结算NPC旧合同，再处理主角事件，排序固定。
4. finish只扣真实自动动作秒数；该帧所有状态在Game候选内完成后一次提交，不持久化“frame已到终点但fleet尚未到终点”的中间态。异常整候选不发布；重复frame不重补额度。时间倒退按既有高水位0推进，不倒走NPC。

Fleet.advanceTo现有workAt/nextDue/ledger时间推进保留：每段从上次高水位算到下一笔合同due/额度耗尽，逐笔账目写实际workAt，不能把每笔时间统一替换成frameEnd。绝对秒统一floor到毫秒边界；同毫秒事件允许顺序处理而不重复推进，分帧只取绝对时间floor，不累计逐帧取整误差。

本契约不需新增持久字段或更改NPC报价/额度公式，只新增组合内部调用选项和事件offset。Runtime仍只调用Game.tick一次，不自己循环补跑；Runtime不向主角转交后台秒数。待PM协调后由我改Game/Dispatch/Route内部链，Runtime owner只需保留候选原子提交。

## 7. 原路/蓝框证据与后续核验

Route.prepare仍使用city.dispatchBounds||city.playBounds并拆断过滤后的原道路run；不连断点造捷径。源city.json没有bounds字段，Bootstrap→PlaceCatalog.prepareCity以密度核心/内缩推算范围，并非用户selection.json蓝框直传。此问题已报父PM，具体路径在remaining；本方案不改city、原路、POI或边界。后4张运行图未完成也保持明示。

待阶段集中case：同店2单只1次取餐扣点/2秒服务；不同店不合并；ready等待10秒无主角推进而NPC推进；重复继续/后台恢复/零体力补给/部分送达取消；当前v3服务中/道路中/已完成档转换不重奖；自动600秒末帧停在真实位置；0→60帧与0→10→60在额度、逐单账目、eventCursor/时间上相同。所有case均未运行；第1—5节已交回源码，第6节现开始实施，不作主循环通过结论。
