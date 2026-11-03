# Vehicle Gallery and Ownership Implementation Plan

> **For agentic workers:** 依项目约定由开发角色在当前 checkout 单写；本计划先交 PM 审核，未授权实施前不修改生产代码。

**Goal:** 独立车辆页面展示十档及真实资格，支持有上限的独立实例购买与玩家选车，并可靠迁移旧存档。

**Architecture:** 以版本化车辆库存保存稳定实例 ID、档位和玩家选中 ID；现有 `Player.vehicleTier` 暂作选中实例档位的兼容镜像，业务层校验两者一致。购买、选车和既有原车升档均由 OrderBook 先校验后一次改变内存快照，并由现有 CountySaveStore 单写/冻结重试协议提交；页面只展示状态和发送命令。

**Tech Stack:** Cocos Creator 3.8.8、TypeScript、现有资源加载器、CountySnapshot/CountySaveStore、本地整数分。

## Global Constraints

- 当前只批准计划；不实施、不提交、不运行测试、typecheck、回归、渲染或操作用户游戏存档。
- 只在用户明确说“阶段完成”后组织集中测试；必要试玩构建不等于测试。所有交付标明已实现未测试。
- 十款资源采用现有 `VehicleSideArt`，不改原图片、既有物价/速度/载重或启动 M5 骑手经营。
- D/D+/C/C+/B/B+/A 每款总上限11，S上限4、SS上限3、SSS上限2；免费初始D计入总数。
- 有活动订单时禁止购买、选车、升档和未来分配；可查看。购买也暂禁是为冻结快照及迁移保守处理，待 PM 审阅确认。
- 所有货币与价格用安全整数分；金额不足、上限、资格、活动单或pending时业务层拒绝且不变更任何状态。
- 单写、revision/commandId及失败后的同一快照重试沿用 CountySaveStore；禁止重复扣费和重复创建实例。
- 不伪造未实现城市/线索/站点资格；S/SS/SSS资格按车型永久共享并独立于骑手资格，当前缺少真实资格数据一律显示未开放。

## 现状与决策边界

- `CountyConfig.ts` 目前只有D、D+两档；`OrderBook.upgradeVehicle()` 禁活动单、花20000分把唯一玩家tier从1改2。县城玩家校验及行程冻结亦只接受1–2档。当前 `CountySnapshot` schema6 包含里程profile；迁移不得回退或重算历史里程。
- V2 §8 的相邻升档金额为 ¥0/200/500/2400/3300/8300/10700/31800/50000/77400；新增副本是 ¥500加从D至该档的相邻升档费累计。十档副本价依次 **¥500、700、1200、3600、6900、15200、25900、57700、107700、185100**。S以上额外须真实资格。原车D→D+升档仍为¥200，并非¥700；两种动作独立呈现，不能将副本购买错误称作升级。
- V2城市门槛要求先能买C以解锁城市，但本轮尚无C速度/结算完整接入及站点/城市状态。页面可显示C及更高真实价格与条件；交易实现先限定D/D+且不声称后续档已解锁。所有档位均可查看，S以上显示线索及国际/站点5条件；普通高档显示当前阶段尚未开放，并明确不等于V2最终地域锁。未来启用时接真实资格，不以虚假的零值判断为已解锁。
- 以上把新旧机制并存作为实施推荐；PM核对是否保留原车升档入口、普通C至A购买开放边界与现有县城玩法依赖后再派实施。不得自行将候选价格或后期功能描述为已实现。

## 文件与接口

- 新建 `delivery-game/assets/scripts/map-sample/VehicleOwnership.ts`：只负责库存数据、价格表、上限、严格纯校验和购买/选车前置条件。类型 `VehicleInstance={id:string;tier:number}`；`VehicleInventory={version:1;nextId:number;playerVehicleId:string;instances:VehicleInstance[];vehicleQualifications:{s:boolean;ss:boolean;sss:boolean}}`。ID用单调 `vehicle-<positive integer>`，不重用；不在本轮存NPC分配或强化字段。
- 修改 `CountySnapshot.ts` / `CountySaveStore.ts` / `OrderBook.ts`：新增schema7，严格校验和原子迁移、未知版本/未知库存profile只读；业务命令 `buyVehicle(tier:number):void`、`selectPlayerVehicle(id:string):void`、保留 `upgradeVehicle():void`。
- 新建 `VehicleGallery.ts`：独立全屏页、两页签与二列纵向滚动；通过回调读取库存/资格并请求详情、确认、选车，不直接持有或修改OrderBook。
- 修改 `MapSample.ts` / `VehicleSideArt.ts`（仅实际需要时）：车辆入口及详情确认；保留既有安全区、素材异步销毁防护与主地图；关闭页面回首页，活动时仅查看。
- `CountyConfig.ts` 以只读展示表补齐§8档位/相邻价格，现有 D/D+活动运算依赖的参数和接口维持兼容；不要直接扩展活动时钟到未经实现的高档。

## Task 1：库存规则与价目表

- [ ] 按上表建立十项只读价格/容量：`copyCents=(500+sum(adjacentUpgradeYuan[0..tier-1]))*100`；计算时验证 `Number.isSafeInteger`。上限映射 `[11,11,11,11,11,11,11,4,3,2]`，按同档所有实例统计，含初始车和玩家当前车。
- [ ] `VehicleInventory` 验证：版本必须1，实例非空、ID唯一且格式合法、tier为1–10、每档不超上限、nextId严格大于所有已分配编号、playerVehicleId恰好指向一个已拥有实例，资格三个值均为boolean；禁止未知profile、重复ID、缺选中、负值与溢出。
- [ ] 独立区分展示资格与当前可执行资格。当前只开放D/D+副本购买；S/SS/SSS没有真实后期来源故不可买，展示条件不写“已解锁”。等级上限11/4/3/2与资格分别校验。

## Task 2：schema7迁移与写保护

- [ ] 先调用现有schema1–6严格校验，再将旧玩家的唯一 `vehicleTier` 转为 `{id:'vehicle-1',tier:旧tier}`、`nextId:2`、`playerVehicleId:'vehicle-1'`；资格全false。保留钱包、玩家数据、活动单 `playerBefore`、路线/时钟/mileage、位置、订单、账单及随机数原值；不因迁移扣钱，也不额外赠送D。旧D+档仅生成一辆D+。
- [ ] schema7要求库存及玩家tier镜像一致；活动单继续原profile且冻结`playerBefore.vehicleTier`，直到既有结束流程，禁止迁移时改变活动单。校验实例及账单profile，拒绝未来 `version>7` 或未知库存版本/profile并写保护，保留现有主/备份与pre-foundation机制，不用fresh覆盖。
- [ ] schema7序列化一次包含玩家、库存、账单和活动单；恢复后nextId不可回退。旧schema1–6仍按其原规则判断，不能先用schema7宽松校验旧数据。

## Task 3：原子业务操作

- [ ] `buyVehicle(tier)`：拒绝活动、无写权限/pending由现有门控处理；校验整数档位、当前可买资格、该档上限、余额和nextId安全范围。先构造扣费后玩家和新增实例的完整新状态再提交；成功创建一个ID、nextId加一，玩家所选不变。重复点击/pending不可执行第二次。
- [ ] `selectPlayerVehicle(id)`：拒绝活动、未知ID、非空闲实例；本期库存只有玩家占用，未来骑手绑定必须在业务层扩展独占校验，不能用UI占位伪造已分配。成功同步 `playerVehicleId` 和 `player.vehicleTier`。玩家已有单仍冻结原档位。
- [ ] `upgradeVehicle()` 继续对当前玩家D实例原位升D+、¥200；校验D+总上限与余额、无活动，保留实例ID，原子更新档位与tier镜像。已有D+不得重复升级。购买副本不触发资格和升档，也不更改玩家选车。
- [ ] 统一 `MapSample.act` 和 `CountySaveStore.save`：确认后只调用一次业务命令；失败保留原提交快照并冻结界面，不重复调用命令。保存成功后关闭确认并刷新；失败期间不提前显示成功、开放其他操作或再次扣钱。页面关闭/重建期间不得丢失待提交状态。

## Task 4：独立页面与确认

- [ ] 车辆入口打开独立全屏页面（非旧单一弹窗），关闭返回首页；底部原导航不透出。按安全区及16 CSS px设置页面留白，纵向滚动两列卡片；卡片采用10档对应侧45资源、名称、拥有数/上限和锁状态，图片等比。切换“全部车辆/我的车辆”，后者按实例展示，空列表有真实空态，滚动内容不能遮导航或安全区。
- [ ] 全部车辆卡片可查看详情：名称、图、§8实际配置、真实价格、资格和拥有数；未开放档不得展示已解锁。详情中分开“购买副本”和当前可用的“原车升档”，购买二次确认显示目标档、具体整数分金额、购买后数量及余额；上限/余额/活动/pending显示具体禁用原因。已拥有实例可选为玩家车辆；已选择者显示当前使用。
- [ ] 活动期间允许只读打开与关闭、切页及详情，不允许调用购买/升级/选车。关闭、重绘、异步图片返回和存档失败时保持安全；不生成未来骑手配车页面或假装能分配。

## Task 5：交付与阶段集中验证

- [ ] 实施时先存各修改文件真实before与SHA，导出本轮patch、最终源码/构建manifest及 `docs/reviews/vehicle-gallery-ownership/implementation-report.md`，报告迁移前后语义、资格边界、价格表、失败冻结和未验证范围；不得覆盖其他在途文件、用户存档，不commit/push。
- [ ] 可做必要试玩构建与4181静态文件交付，保留Cocos原始诊断；不自动运行测试、typecheck、回归、渲染或读取/操作用户真实存档。
- [ ] 用户明确“阶段完成”后由PM安排集中测试：使用隔离合成存档覆盖schema1–6的D/D+、活动中不同phase及schema6里程；迁移前后钱包/账单/活动字段逐项相等、重复恢复不产生新车；未知schema/库存profile只读且原始字节不变。覆盖每档上限、初始D计数、S资格永久性、余额不足、错误ID、活动期间命令拒绝、同一提交失败重试/双击/多标签竞争，以及玩家选车的tier镜像。对可执行D/D+检查原车¥200升级与副本¥500/¥700购买分别扣款一次。
- [ ] 同一集中阶段由测试角色用隔离数据检查两页签、详情确认、滚动和狭窄/安全区屏幕、资源异步切页及失败态；用户自行操作确认视觉和体验。此前所有交付均标注未测试，不拿历史通过记录套用。

## PM核对点

1. 保留原车D→D+ ¥200升级，同时新增按累计价格购买副本；这是避免改变已有经济的建议。
2. 普通C至A在本次仅可查看、不可购买，直至其真实可用车辆数值及资格依赖实现；需PM确认是否有已授权的更早开放方式。
3. 有活动单时购买与选车均禁止；对未来骑手分配只预留稳定ID，不提前实现M5。
