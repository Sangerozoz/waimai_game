# 整数容量与首轮经济校准：隔离源码交付

状态：已在stage接齐真实源码路径；未编译、未测试、未合live、未构建部署，不自判PASS。

## 交付
- 7份既有stage源码实际修改，新增V2LoadRules、V2EconomyProfiles、V2SlotEconomyConfig，共10份代码。
- 唯一参数源仍是PM拥有的parameters.json；运行表从该JSON生成并带来源SHA，未另算或改参数。
- source.diff为相对于baseline-manifest的完整精确补丁；implementation-manifest.json记录每份前态、stage后态、live收口SHA和只读依赖指纹；contract.md供PM/B对接。

## 实际代码路径
- LoadRules严格区分kg-v1与slots-v1。新订单只带load；占用按通过身份/端点校验的稳定ID可信生成，不能借用FoodItem.unitWeightKg或caller价格。
- Profiles从同一30级/10车型表读效果、相邻升级费及购买费。显示报价和扣款共用方法；初始金币、购买价、普通基费不提高。
- Economy2混合接纳显式旧kg标记和完整新slot条款。原完整经济校验保留；新报价独立distance-effort-slots-v1，不使用extraKg。校验绑定完整profile/price/effect/load/capacity/等级/速度/收入/服务省时，未知/缺失/显式null与undefined不降级。
- Dispatch2提供真实acceptSlotBatch和按对象放行的经济命令。NPC培养/申请配置可以在工作中提交；主角活单换车/升级仍禁，唯一车辆分配与旧fleet锁保留。
- Fleet2新批以固定、有限、可跳过放不下项但绝不重抽的1/2格池组单，恢复时复算同一有限ID集合；新分支不读旧expectedBatchDensityCap。数量进入原timing模型，旧批dueMs/paidCount/elapsed/quota/日期时钟不重建。
- Route3加入显式loadProfile/sourceNextId/sourceOfferId，绑定稳定普通ID与权威端点，保留2×POI扫描边界和既有路由/分组/ETA/位置；不修改任何地图数据。
- Game6新批走slots报价与原Trip3食品；原Game1—5组合先过原完整组合/路线/Trip/Dispatch/Fleet/Economy门禁，再给旧quote添加kg标记。旧quote去除这个标记即原payload；不改钱、等级、账本、风险draw、期限、进度、位置或序号。
- Runtime沿PM复审a5c19c46基线仅增加真实只读DTO/报价入口及返回类型；原错误诊断、事务validate→commit→publish及drive代码逐字保留。

## 已做证据，不是应用测试
- Python仅做文件/SHA、参数JSON、费用相邻差分、命名导入/导出及原文对照；未加载或执行TS。
- 运行表与PM源JSON逐值一致；30级/10车型相邻差分一致。7份live均未改。50处相对命名导入按stage优先、live只读依赖解析，无缺项；这不等于类型检查。
- 完整source.diff的只读`git apply --check`实际退出0；没有执行apply，不代表源码编译或应用行为通过。
- 原完整经济/计价校验、旧helper、原ETA、fleet绝对推进、原v1路线恢复，以及PM Runtime诊断/事务/drive有精确原文保留证据。新代码没有新增Math.random调用；不把文本计数当随机行为实测。

## 自动LSP单列
编辑器曾报隔离目录缺少只读依赖及随后的implicit-any/receipt基类类型错误；本轮不复制这些依赖、不改其引用路径来掩盖。新容量查找可空问题、一个新回调推断问题已修；未主动typecheck/编译，不能据此宣称无类型错误。

## 未执行案例（等待阶段授权）
1. 新普通/专送的接单、移动、服务、结算与实际屏幕格数。
2. Game4/Trip2旧normal在途、Game5/Trip3已分类在途的完整运行恢复，含正G planned与部分补给。
3. 新Game6混合旧kg批次、新slot批次的保存/恢复/取消，原quote/dueMs/风险draw/期限/位置/序号及历史到账保留。
4. 新metadata缺失、null、undefined、未知版本、混合单位、伪造占用/效果/价格、重复ID；这里只实现拒绝路径，未制造或运行合成档。
5. NPC活批培养/换车申请与旧车锁，旧单后新条款，有限quota、午夜日期及在线/离线分段一致性。
6. 容量节点的稳定候选前缀/有限扩展/耗尽，以及NPC多单数量/时间/收益；未做地图导航实测。
7. 30级封顶、余额不足、实际扣款同显示报价、原购买/成长目标及整套长期平衡试玩。
8. 单写者保存失败保护、旧包拒绝Game6且不覆盖进度；未操作真实存储。

## 不在本交付内
未修改任何live、UI/Spacing/Skin、FoodCatalog/TripRules、旧Config、参数原文件、地图/资源/布局/边界、存档或公共台账。B仍需按contract.md接新字段，不能将旧UI与本候选混发。所有reader/writer与10个源码文件应由PM独立复审后协调应用，不能单发新档writer。

交回后停止stage写入，释放本租约，由PM恢复原Default。
