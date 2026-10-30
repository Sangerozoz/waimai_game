# 第一阶段验收反馈修订 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: subagent-driven-development。按Task1→Task2→Task3顺序实现，每项独立审查规格与代码质量，最后根任务完成构建与真实UI交付。当前代码大量为既有未跟踪工作，使用完整恢复ZIP及逐文件差异包，不混入无关变更或强行提交旧工作。

**Goal:** 落实已获用户批准的六组验收反馈，并交付可继续旧进度的第一阶段修订版。

**Architecture:** OrderBook继续作为唯一状态，纯时钟/经济/存档与可玩城区/内容目录分开，Cocos视图调用域操作。历史活动单冻结旧规则，新单用本轮规则。界面不自行加钱。

**Tech Stack:** Cocos3.8.8 / TypeScript / Node内置测试 / 本地PNG / CUA浏览器验收。

**最新执行状态（2026-10-28）：** Task1–3实现及独立审查完成；Task4最终103项自动检查、类型检查、构建和独立整体复审通过，窄长屏视窗越界已修复并有先失败后通过的实际布局回归。用户最新明确接管全部页面操作/体验测试，助手停止浏览器操作，只检查代码逻辑与数值；原Task4的CUA补测步骤由该指令覆盖，剩余视觉/交互项目保持待用户复验。当前4181服务可用，不开展第二阶段。证据见[接续交付记录](../../reviews/2026-10-28-stage-one-revision.md)。

## Global Constraints

- 用户确认：30分钟=10秒，上限15秒；D→D+200元；50经验/第5单首次Lv.2。D平均速度12km/h、D+13.2km/h为本轮可调游戏配置。
- 10条普通单、无分页、两段道路全程≤10km；新范围不破坏连续取送，50m默认、30–100m缩放。
- 保留现有进度、已抽随机和历史回执；不注入/清空用户存档，不回扣旧320元购车支出。
- Main.scene、旧DeliverySession.ts与旧躲避游戏不改。沿用当前codex/food-delivery工作目录及恢复快照。
- 用户已批准设计并要求立即修改，不逐任务重复确认；第二阶段和广告SDK不在本轮。
- 先写能观察规则的失败检查，再实现并记录red/green。每项实现后独立只读审查，重要问题修复后再进下一项。

### Task 1: 时钟、经济与兼容存档

**Files:** 新建assets/scripts/map-sample/CountyConfig.ts；修改DeliveryClock.ts、CountyRules.ts、CountySnapshot.ts、OrderBook.ts及相关tests；必要调用点只做单位/方法接线，UI重排留Task3。

**Interfaces:** `deliveryTiming(distanceMetres,speedKph)`、`animationSecondsFor(displaySeconds)`；`OrderBook.timing(distanceMetres)`、`timingForRoute(route)`为统一时间查询；当前player/active/progress/riderPose/list/settle/finish等外部含义保持。县城专用COUNTY_VEHICLES和countyExperienceLevel不改旧域配置。CityData可预留playBounds/legacyMapIds元数据供Task2，字段不依赖引擎。

- [ ] 写并运行失败检查：`animationSecondsFor(1800)===10`、2700/3600均15；`deliveryTiming(6000,12).displaySeconds===1800`，无8分钟或额外倍率；D+同程更快。
- [ ] 写失败检查：4单Lv1/5单Lv2，第5单收入按出发Lv1；余额20000恰好升级、19999不足、重复不扣款。
- [ ] 设计新快照版本及旧格式严格校验→迁移。先保存旧v2真实快照夹具，覆盖闲置、选路、途中、paused、arrived、done，旧时钟/结果与现金冻结，当前等级可重算，新版本再次恢复不抽随机。
- [ ] 实现纯规则与迁移，移除主动暂停能力，恢复running/旧paused自动继续。后台冻结仍由视图控制advance。新单位置按实际道路距离推进，取餐切换按两段里程比例；旧单保持旧姿态。
- [ ] 更新本轮语义改变的检查，运行`npm run test:map`、`npm run test:county-store`与必要类型检查；报告确切命令、输出、限制。root负责后续完整构建。
- [ ] 自审及独立双轴审查通过，保存任务快照和差异包。

### Task 2: 主城区、地图边界与丰富内容

**Files:** 新建CityExtent.ts、PlaceCatalog.ts、FoodCatalog.ts纯模块；修改MapTypes.ts、CityMap.ts、OrderBook.ts及必要CountySnapshot兼容接线，新增相应tests并接test-map.cjs。

**Interfaces:** `CityExtent`导出Bounds与基于视窗半宽高的`clampCamera`，CityMap所有移动路径使用；`prepareCity(data):CityData`保留原graph及地点索引并扩充唯一虚构地点，附playBounds与可信legacyMapIds；`FoodCatalog`每项含id/name/imageIndex，图集4×4从左上到右下16格，供Task3按imageIndex取图；旧offer.food可通过稳定映射找到兼容图。

- [ ] 先观察真实建筑密度确定以初始主城为核心的边界和10%外扩，记录范围及原/新增地点数量；不把山路、整张数据框当主城区。不修改city.json路网。
- [ ] 先写失败检查：不同viewport/30–100m下视窗四边不越界，follow/setRider/locate/zoom/drag都走相同限制；旧城区外位置仍能看到并继续履约。
- [ ] 实现真实道路节点上的虚构餐厅/顾客扩充，至少40个城区商家及120个城区顾客，唯一商家名称和地址，保留旧索引及存档身份别名。
- [ ] 16类餐品按图集顺序：鸡腿饭、牛肉饭、红烧肉饭、麻婆豆腐饭、鲜汤面、拌面、馄饨、小火锅、饺子、包子、披萨、汉堡、轻食沙拉、寿司、蛋糕、奶茶。数量/重量/易损类型匹配，首单基本条款沿用。
- [ ] 先写同批10单目的地不重复、商家/餐品分布丰富、不同刷新继续丰富的检查；小型仅1商家/1顾客测试图可降级重复而不死循环。新的正常派单地点与整条路径在可玩范围内，旧活动单及城区外回城恢复单保留兼容路径。
- [ ] 实现内容生成及有界路径筛选，不仅换文案；拒绝失败候选继续搜索，保留全程≤10km。完整自动检查与类型检查；双轴审查并修复重要问题。

### Task 3: 餐图、精简手机与自动结算弹窗

**Files:** 新建FoodImages.ts；修改OrderPhone.ts、MapSample.ts、SampleUI.ts；接本地assets/resources/map-sample/food-atlas-v1.png（root使用imagegen生成）。必要测试聚焦弹窗状态/幂等，不增加仅检查字符串的无效测试。

**Interfaces:** `FoodImages`按FoodCatalog.imageIndex加载并裁出图集格为SpriteFrame；生命周期中销毁后不异步添加节点。所有金额/等级/速度显示来自COUNTY_VEHICLES及book，禁止320/12/30→5旧硬编码。用`book.timingForRoute(route)`保证旧活动单预览与实际一致。

- [ ] 新手机卡片显示餐图与餐名、商家、顾客、预计收入、全程公里和预计时间；常规重复信息删去，加急/怕洒作为标签；ScrollView仍10单无分页、滑动不误接。
- [ ] 接单后的路线面板可查重量、需求、时限与风险，保留选路和退回。需要精简的字段不是从游戏规则中丢失。
- [ ] 移除暂停/继续配送按钮及相关提示；后台/刷新恢复按Task1继续原进度，车辆仍不可配送中升级。
- [ ] 订单完成自动弹结算，门口先选择后弹结算；确认调用finish并开下一轮大厅。关闭可留在回执并重开，重建布局/回执恢复不会多次叠弹窗或重发奖励。
- [ ] 车辆显示D12km/h、D+13.2km/h、200元，首升目标与5单经验提示统一。类型检查与相关检查，双轴审查。

### Task 4: 根任务集成、验收与交付

- [ ] 运行最终npm test、typecheck、Cocos build，保存日志与构建哈希，原受保护文件哈希相同。
- [ ] CUA隔离源真实操作：旧档加载、新档5单升级与200购车、10单图片与滚动、取送连续、15秒封顶、无暂停入口、自动结算、需求先后、重载不重奖、地图各边与长屏；不脚本改玩家状态。
- [ ] 更新主方案与README，新验收页面使用修订记录键，不覆盖用户旧17/3/4反馈；提供重点复验清单和新规则预期。
- [ ] 最终独立审查；修复后只做覆盖改动的回归。保留可运行入口与新恢复快照，交用户验收，不代勾通过，不开展第二阶段。
