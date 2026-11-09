# FOOD-RISK-IMPLEMENT-1106：PM冻结实施契约

本轮按用户持续授权的产品方案/规则/数值/UI完成要求，批准A的domain-proposal.json中publicContract、versionCompatibility与B的layout/food-risk-contract-1106/ui-proposal.json语义需求。两者仍是输入，不代表实现或验收。本文件冻结精确API与双版本策略，A/B各自单一写集并行，统一reader/writer候选集成后才可发布。模型仍Hermes acp-hermes-agent→OpenAI API openai-api:gpt-6.1-sol，不用Codex/嵌套CLI/新子Agent。

## 1. 确认数据与边界

- 正式V1第43/47/69行；V1参数risk第538—599行：fragile fast/main/smooth为.12/.06/.02，normal .06/.03/.01，durable .02/.01/0；地图因子.25/.5/.75/1/1.25，rain/severe加.02/.05，cap .25。balanced映射main，不套旧GameConfig.ROUTES或价格。
- 唯一食品目录是现有FoodCatalog.ts的50项id/name/imageIndex/fragility，顺序和现有hash选择一起冻结为food-risk-v1。不复制另一份50项表，不调用有roll的selectFoodForOffer，不添新概率/参数或改旧成长。
- 真实订单weightKg仍原正整数、容量与ordinary-effort-v1权威链；FoodItem.unitWeightKg完全不进入业务输入、重量、报价。NPC/专送价格、SDK、地图及原路均不改。

## 2. 精确接口

由domain/V2TripRules.ts导出：

- `V2FoodRiskContract = Readonly<{version:'food-risk-v1';foodId:string;fragility:Fragility}>`。
- `V2FoodRiskById = Readonly<Record<string,V2FoodRiskContract>>`。
- `parseV2FoodRisk(raw:unknown):V2FoodRiskContract`：仅结构校验，own keys精确3项，非数组非null，版本/非空foodId/三枚举均严格，额外risk/draw/系数拒绝；返回副本，不能代替目录真实性校验。
- Trip状态严格判别：原version2 orders禁止own food字段；新version3每单必须完整food。既有其余字段不变。
- `begin(mapId:number,tripId:number,orders:{id:string;fastestGameSeconds:number;heldMetres:number;safe:boolean}[],foodById?:V2FoodRiskById):void`。完整验证后才写状态/roll。提供第4参必须完整、无多余/缺失/重复ID，null-prototype表与own-key检查。显式null/undefined不是合法食品上下文；只有真正省略第4参才兼容旧version2调用，version3实例不得省略降级。生产Game始终传完整表并生成Trip3。

由现有map-sample/FoodCatalog.ts导出：

- `foodForV2Order(orderId:string):V2FoodRiskContract`：与旧UI完全一致的UTF-16 charCodeAt FNV式hash、现50项顺序，返回可信标量副本，不trim/改大小写/重抽，不返回unitWeight。
- `foodPresentationById(foodId:string):Readonly<Pick<FoodItem,'id'|'name'|'imageIndex'|'fragility'>>`：严格唯一ID查找，未知报错，不借foodForOffer回落首菜，返回副本。只类型依赖Trip合同，Trip不运行时导入map-sample。

由Game提供：

- `export type V2FoodOffer=V2RouteOrder & {food:V2FoodRiskContract}`；normalCandidates(count=8)与specialCandidate(id)追加可信food，Runtime原透传不改。
- acceptBatch保持原V2RouteOrder[]参数兼容：先保留原合法路线/经营/重量/容量/safe检查，再按合法id生成canonical food。输入own food缺失可，显式food须parse及全值匹配canonical；非法/null/undefined/不匹配拒绝。caller任意risk/draw不能控制业务。
- Route/Dispatch只收到白名单投影id/kind/weightKg/pickupNode/dropoffNode/pickupName/dropoffName，不混入food或任意额外风险字段。

## 3. 真实风险与随机数

Trip3仅对已取未送非safe单，以已冻结food.fragility选择基表，原累积`min(.25,oldRisk+(base*mapFactor+weatherExtra)*metres*fraction/heldMetres)`保持。Trip2永远原normal。保留原天气与每单draw/severityDraw的调用次数/次序/保存值、体力截断、safe免风险、outcome及保留收入率；不添加分段重抽或每帧天气加值，不扩红灯/途中变天/预计餐损概率读模型。

## 4. 双格式与旧进度

- 新Game5/Trip3；Route2、Dispatch、经济config和唯一slot不变。
- Trip2仍序列化Game4/Route2/Trip2，Trip3序列化Game5/Route2/Trip3。只读一次Trip快照决定组合版本，别新增帧内全量clone。
- Game1—4先执行原版本配对和全部原恢复/跨组件校验，旧Trip1→2/Route1→2原接受边界保持。旧当前批保留Trip2的D/G/risk/draw/severity/seed/action/到账，不补food、不按当前hash迁移；下一次合法新批才升3/5。
- Game4+Trip3、Game5+Trip2、未知版本均拒绝；Game5必须Route2和Trip3，所有food在Game按真实orderId与canonical helper相等核验。新Trip3不得缺food或退回normal。
- 旧Trip1/2只允许food真正缺失；显式null/undefined/对象均拒绝，presence在JSON clone抹除undefined之前核查。保留所有旧完整校验，不修坏数据或放宽服务/动作/凭证/价格/期限门槛。
- 历史completed/cancelled Dispatch/receipt不追写food、不重结算；新food只随当前Trip生命周期保存，不宣称永久历史食品详情。旧reader拒绝Game5时保留slot、不给重开/清档兜底。

## 5. UI只读展示（B）

- 候选直接读Game返回food。已接Trip3从同id Trip订单food解析，再strict foodPresentationById获得菜名/图像/类别；不重新hash兜底。结构/目录非法不得回落首菜。
- Trip2保留现hash的旧菜名/图片展示推测，但不当风险身份，不冒充已升级；用明确“旧批规则/沿用原普通风险”说明，不把当前目录fragility标成旧单真实类别。
- 三处消费者统一：大厅、本批/在途卡、planned ETA身份行。类别脆弱/普通/耐放；ETA仍剩余游戏时长、late/safe权威字段不重算。
- 保留真实重量紧跟名称、金额、地址、控制/禁用、滚动、全部订单可读与动态高度。补给插图不是配送食品合同，不附加配送类别；专送卡未有图的状态不扩设计。
- 可信ID必须能strict解析到当前唯一规范name后再进入现foodImage，避免旧foodForOffer未知名默认饭盒路径。不改FoodImages/资源loader/manifest/图片。50条目录不是50张新原生图完成。
- 骑手新排版/万元规则仍held，G04仍unknown，不夹带改动。

## 6. 独占写集与验证

A独占FoodCatalog.ts、V2TripRules.ts、V2GameSession.ts和logic/food-risk-1106/实施报告；B独占V2GameUI.ts和layout/food-risk-ui-1106/报告。其他源只读。当前冻结Game SHA0fe0d7fe23a1457e4c5286539ea32a7f5a796c94fe45312f5f143ddda65abce3、Trip213cefc4da3a6166c5ba9b5bd36d3a795b94f676d92fcf5448324df79a768e01、UI8fd5df4ee2cc7ca85cecd9488eec7cdd89fc08c374e8580d6bdcbc0b8336cd9c；实际先核对，漂移先协调。

仅A/B沿用户本轮临时Accept Edits在各自本段写lease内编辑，交回立即停止，PM恢复各自原Default；不更改全局/其他角色。拒绝不得终端绕过。

不跑tests/typecheck/TS/回归/Creator/浏览器/游戏/真实或合成档，不commit/push。静态diff/SHA/分支/独立算术允许，PM统一两阶段审查、必要构建和授权外观。当前deadline历史候选不包含此新食品增量；未获任何运行或用户验收，不关闭反馈、不宣称98%。
