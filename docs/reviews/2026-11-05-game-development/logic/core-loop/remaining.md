# 核心配送闭环A剩余项与集中案例

**下列案例全部未执行。** 用户未说“阶段完成”，本批仅做源码静读和指定文件编辑。没有tests、typecheck、回归、游戏、真实/合成档执行、构建或部署证据；不能据此关闭U01/U02或宣称迁移/性能/闭环通过。

## 集中测试前提与禁止事项

- 由PM等用户明确“阶段完成”后安排；必要Creator构建由PM统一，不由本执行者启动。
- Runtime/UI接线合入同一checkout后核对，不覆盖其他dirty/untracked。
- 不为测试当前进度而读取真实用户slot、接单/购买、造档或清档；届时使用何种获准隔离夹具由PM统一安排。这里列的是未来案例，不是已执行记录或真实存档内容。
- 当前唯一slot规则不变；不得建立第二运行slot/备份运行档、读废弃key、自动重开或回滚用户进度。

## 同店分组与原路/容量

|ID|精确未执行case与预期检查|
|---|---|
|A-G01|同一真实经营POI的2单：规范一个pickup、两个按原序dropoff；一次取餐扣1点、服务2现实秒/60游戏秒；每单送达各1点/1秒/30游戏秒。各单独立receipt/经验/收入/补额度不合并。|
|A-G02|选单次序A店1、B店1、A店2：先A组pickup→A1顾客→A2顾客→B组pickup→B1顾客；首次商家顺序和组内原顺序稳定。|
|A-G03|相同屏幕名称、不同pickupNode均匹配真实POI：不能合并。|
|A-G04|相同pickupNode、不同canonical pickupName均是真实商家：不能按节点合并。|
|A-G05|同节点且相同伪造/别名/空名称，或同一node+name在权威POI中重复有歧义：每单独立pickup，不凭输入文字合并。|
|A-G06|同店批次总重超过车容量，即使分段卸货后可放下也必须拒绝；等于容量可接受；失败无Dispatch新合同及Route新计划提交。|
|A-G07|各订单独立可达但分组后的某个跨顾客/商家有向段不可达：整批拒绝，不退回任意乱序、不造捷径、不改city。|
|A-G08|同一顾客节点的多个dropoff：零道路腿仍保留每单服务，不合并交付扣点、时间或arrival令牌。|
|A-G09|快捷/均衡/平稳共路别名及不同路：仍沿原router真实段，不能以分组跳过中间道路或改变车速。|

## 组原子性与服务门闩

|ID|精确未执行case与预期检查|
|---|---|
|A-S01|pickupGroup输入空数组、重复ID、未知ID、混入已picked/已delivered成员：整组拒绝，体力和所有成员picked不部分变化。|
|A-S02|组服务前体力0、介于0与1之间、恰好1：前两者false/blocked、不标记；恰好1只扣一次到0且全部picked；已扣点服务仍可完成剩余2秒。|
|A-S03|多成员Route未提供pickupGroup hook：拒绝，不能循环旧service；singleton仍经旧service入口，dropoff仍每单扣点。|
|A-S04|pickup确认后尚未service计时的保存点：Route.picked全组、Trip.picked全false、serviceCharged=false可恢复；恢复后只扣一次。|
|A-S05|组pickup服务半程、已扣点保存并恢复：保持serviceSeconds、整组Trip.picked和门闩，完成只用剩余服务时间，不重扣。dropoff半程同样不重扣/不提前结算。|
|A-S06|重复pickup、在service中再次continueTrip、重复已到达结算凭证：拒绝不合法动作或保留既有去重结果，不重复发钱/经验/额度。|

## ready、继续、取消与时间

|ID|精确未执行case与预期检查|
|---|---|
|A-R01|一次手动tick含到店/取餐结束后的长尾：advance只返回真实已用时间，pickup结束进ready，cursor指下一站，两个计时归0且门闩false，尾段不追赶。|
|A-R02|无补给ready空等10现实秒再点击继续：位置仍原店，gameSeconds/里程/体力/餐损/期限均未变；NPC仍按现实与既有额度经营。Runtime先同步旧时钟，下一tick不能把10秒补跑。|
|A-R03|连续两次continueTrip及idle/planned/travelling/pickup/service/finished各phase调用：只有第一次合法ready成功，不跨第二站、不扣钱/体力、不改期限；重复事务不发布错误候选。|
|A-R04|ready发起补给，动作中continueTrip拒绝；动作完成后仍ready，可手动继续。补给自身时间/费用/库存按原规则，不把主动补给等同无动作空等。|
|A-R05|ready零体力继续、道路耗尽、组服务不足1点：真实原地停止，经原补给恢复后继续，无未授权自动补给费用。|
|A-R06|ready取消、道路边中途取消、恰好腿末/零长度腿取消：保留真实anchor/位置；已完成收入经验保留，取消全部未完成，无额外奖励/罚款。|
|A-R07|ready/pickup/service/道路中hide→show、暂停→恢复、重载首帧、pending广告：不补跑隐藏主角行程和动作，NPC仍走既有现实经营路径。|
|A-R08|dropoff交付完成后自动前往下一顾客或下一商家，无新增逐单确认；到下一商家才再手动pickup。|

## 自动控制与预算

|ID|精确未执行case与预期检查|
|---|---|
|A-A01|自动组取餐完成且本帧仍有合法余秒：先经同一个Game.continueTrip，再推进后续；跨批剩余时间和既有deferAuto计费保持。|
|A-A02|自动权益精确耗尽在pickup到店、组服务结束ready、顾客服务结束、跨批边界：保留真实状态/位置，不能在零余秒代点下一pickup、continue或下一服务扣点。下一帧manual不追回被截掉的尾段。|
|A-A03|自动低体力、有/无明确补给授权、授权预算不足、库存补给动作在途：沿原授权规则停住或补给，不重复组扣点，也不以ready绕过action门禁。|
|A-A04|自动无车/无候选/组合过长删减选单/前15单组合预算拒绝：不产生无限零进度循环或部分合同提交。|
|A-B01|同店多单、不同店单、已转换legacy计划：Route.choices和Game.routeChoices的服务秒/体力分别按实际pickup/dropoff Stop计，不再按订单数统一估算。|
|A-B02|首15预算恰好足够/差不足1点、分组省一次pickup的边界：接受过滤与出发过滤口径一致，道路每公里耗能与容量不变。|
|A-B03|每单fastest必要服务仍取2送1；合并前后逐单期限不重签，不加合并收入/经验奖励；天气/车速只修正道路秒，不把服务2/1缩放。|

## 当前进度兼容与非法档拒绝

|ID|精确未执行case与预期检查|
|---|---|
|A-M01|旧Game v3/Route v1的idle、planned、travelling边中、pickup等待、pickup服务未扣/已扣半程、dropoff半程、部分已送及finished各状态：先原组合及原Route完整校验，转换后保持原序/cursor/legs/所有进度/position/tripId/picked/arrivals/token及Trip随机/期限，无重扣/重奖。|
|A-M02|旧缺serviceCharged但serviceSeconds>0及等于0的原接受输入：仅沿用原门闩推断；随后序列化为Game v4/Route v2并再次恢复时语义一致。|
|A-M03|旧同店多单在途：转换为legacy-sequential单成员，不合并/重排既有旧批；当前已出发腿不倒退；之后完成pickup进入ready；下一新批才grouped。|
|A-M04|旧档篡改leg的road/from/to/metres/seconds/points/风险等任何输入字段，或者同弱mapKey但不同router/city：原完整legs比对仍拒绝；缓存命中不得放行。|
|A-M05|新档pickup重复/漏ID、dropoff多成员或漏单、先送后取、未知商家伪合并、grouped非稳定排序或legacy非原逐单序：拒绝，不以任意乱序解释。|
|A-M06|伪ready的cursor=0/越界、前一站dropoff、anchor错店/边中、计时非0、门闩true、全组picked漏一个或Trip只首ID picked：均拒绝；正确ready恢复仍等待。|
|A-M07|新旧arrival token改tripId/stopIndex/orderId，Trip delivered与arrival不一致，Dispatch completed/receipt与Route/Trip不对应：全部保留原拒绝/去重边界，不重发钱。|
|A-M08|Game v1有活跃批或缺失在途Trip仍拒绝，v1原可接受无单范围保持；Game v2只接受原TripState v1组合；v3必须TripState v2且Route v1，v4必须TripState v2且Route v2。未知未来版本、错profile、错配或缺字段拒绝。|
|A-M09|组合/Route任一校验失败、存储commit失败、并发旧writer：Runtime/Store不能发布候选或覆盖原slot；成功载入升级只写当前同一slot。由Runtime owner核对事务，不创建备份运行档或清档重开。|
|A-M10|真实map命名/经济参数与旧MapData准备不变；同一CityData WeakMap命中、期望legs16项淘汰、超262144字符不缓存仍完整校验。仅在阶段许可后测量耗时/帧率，不能现在宣称性能通过。|

## 未完成/非本批

- **Runtime/UI集成和实际可见效果**：PM最新告知B已交回continueTrip/ready/orderIds展示接线。本执行者没有改/运行其文件；PM统一集成与必要构建。B发现的未扣点service补给可达性由PM在UI处理，不扩大本写集。新增ready不等于原U01卡顿/U02跟随已解决。
- **NPC帧内真实时点/补额度先后/归日**：`../cross-module-contract.md`第6节尚未实施；本批Game仍用原Dispatch.tick帧尾推进和原completeDelivery默认时刻。粗帧与拆帧是否一致、账目日归类不能记通过。
- **红灯/途中变天**：保持现状未实施，不新增事件快照或随机状态。
- **蓝框权威传入与后四运行地图**：保持现状；不改原city、三框、地图或POI，不把已有过滤等同用户蓝框问题已解决。
- **报价差异/成长经济体验**：不改报价/经济配置；差价反馈尚未闭环，不用调价格掩盖配送卡顿。
- **真实广告SDK**：本批不接入、不购买或触发广告；现有SDK完整闭环仍未完成。
- **类型/运行/性能/迁移验证**：patch工具自动TypeScript检查为skipped，本批没有任何通过结论；须等阶段授权再集中验证。

## 本批实现时采用的可复用纪律

- 旧结构升级前保留旧完整校验，组合不先丢失原字段；升级只加结构标识，不重排在途事件索引。
- 合并服务先做全组预检，再单次扣点；可恢复的Route/Trip未扣点差异必须按全组校验。
- 手动确认边界由权威状态机截断实际用时，显示层不能伪造停车；自动继续复用同一公开入口。
- 路线期望缓存只接受router生成值，永不以缓存替代输入完整校验。
- 遵守本批独占写集和禁止测试范围，未在个人skills目录或其他公共文件另写记录。