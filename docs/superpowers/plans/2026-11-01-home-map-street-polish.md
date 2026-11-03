# 首页街区接续与HUD细化 Implementation Plan

> **For agentic workers:** 使用既有固定开发/美术会话执行；AGENTS和用户授权优先，沿用同checkout，不新建重复角色或worktree。用户未说阶段完成，覆盖技能默认TDD、逐改动测试、独立复验和提交步骤。

**Goal:** 在已交付HOME-STREET-1101上补齐跨块装饰接续、近景路口/屋顶细节和已认可概念的人物卡组合，交付同入口可试玩构建。

**Architecture:** 保持CityData和业务逻辑，装饰生成改为世界单元一致的确定性竞争及保护，近景细节以独立呈现层位于材质之上/路线车辆之下。HUD只改MapSample的组合和实际可见边界，数据来源继续OrderBook现有player，已有图标复用。

**Tech Stack:** Cocos Creator3.8.8、TypeScript、现有PNG/SpriteFrame、Graphics、离线CityData。

## 执行状态

**17:14最新交付：** 开发已完成本任务实现并生成试玩构建；build.log显示17:14:50 Finished，报告命令退出0，保Cocos原诊断。实现范围见docs/reviews/home-map-polish-20261101/implementation-report.md及docs/team/reports/2026-11-01-home-map-polish-pm-delivery.md。以下勾选仅表示实现/交接动作完成，不表示运行验证、视觉或性能通过；用户体验与阶段测试待后续指令。

用户再次“继续”后，已恢复固定开发与美术会话。此前两会话因平台额度限制中断，尚无本任务最终报告/构建或HUD规格交付；不得把第一轮HOME-STREET构建套作本轮结果。现两会话均已恢复执行，开发先接续落盘代码，美术补唯一HUD规格；仍不触发集中测试。

恢复后HUD制作规格已实际落盘`docs/art/home-map-production/home-hud-polish-spec.md`并交开发。规格中“保灰站点”仅作历史措辞，PM已明确以既有站点资源原色为准，不恢复灰滤镜；其余仍按已认可首页方向与实际安全区适配。

## Global Constraints

- 用户2026-11-01明确“继续”，沿用已认可首页概念与允许空地补景授权，不登记样板审美验收，不扩M3–M7或全县逐栋制作。
- 输入：docs/art/home-map-concept/home-map-screen-v1.png、docs/superpowers/specs/2026-11-01-home-map-art-implementation-design.md、上一轮实施报告及home-map-production资源交接。
- 真实道路/建筑/取送点、路由、计时、存档/经济、用户相机与车辆位置不变；空地装饰无交互经营语义。保持默认15m、路线蓝黄绿、主角也是骑手、现有五导航入口、无按钮火焰。
- 全部dirty/untracked保留，不reset/clean/commit/push。开发单写源码/引擎导入，美术仅写本任务规格，PM协调及文档。
- 不打开游戏页面/渲染/测试/typecheck/回归，不读取或修改用户存档；允许为交付必要构建并读取其日志。暂不继续TapTap。
- 不从概念图裁图，不新生头像/车辆/材质。光源左上、影右下；已有素材完整原件保留。

## Task 1：世界单元装饰接续（固定开发）

**Files:** HomeMapArt.ts，必要时CityMap.ts的可见块调用/缓存。

**Interfaces:** 输入只读准备后的CityData；输出既有NeighborhoodPlacement中的trees/houses。drawTile继续兼容，但结果应来自世界单元固定候选，不能取决于已经加载的邻块或调用先后。

- [x] 将同600m块内的accepted列表互斥补为跨边界一致规则，包含邻接世界单元中可能相交的房屋、院落、树冠/地影保护范围。
- [x] 用固定空间优先级/候选邻域或等效方案决定竞争；不能仅查看当时已加载的块。候选归属单元固定、缓存有界，拖回相同范围不累积或更换装饰；不要全城铺Sprite。
- [x] 保既有道路/建筑/水面/水道/运行时POI保护与合理沿街配额。若新规则因互斥减少候选，说明实际机制，不假称实测密度。

## Task 2：近景街道与屋顶细节（固定开发）

**Files:** HomeMapArt.ts/HomeMapSurfaces.ts/CityMap.ts；如分离新建HomeMapDetailInk.ts，仅负责表现绘制。

**Interfaces:** 使用真实道路节点/中心线/宽度/桥标识及建筑多边形。细节节点位于材质上方、路线/车辆/地点下方，按当前视野与缓冲更新/缓存，scale低于近景门槛不绘制附件。

- [x] 为适合的真实路口/路段补少量连贯路缘、车道虚线和人行横道细节。仅在几何空间允许且道路宽度适合时画；避开桥面、水道、不连通邻近路和狭小支路，不画虚假连接/新路口，不改变寻路。设施是装饰表现，不当作OSM实测标签。
- [x] 给真实屋顶补材质之上的细边/高光及少量小型屋面附件，附件四角需处于足够大的原建筑轮廓内，无法容纳就跳过；不把大设备跨屋顶摆放，不使所有建筑变同款。
- [x] 路面标线、屋面细节、既有T01–T03贴图不得互相错误覆盖；视觉失败保原有回退。按块/LOD收敛，不新增每附件的大mask或全城节点。

## Task 3：首页人物卡与状态组（美术规格→固定开发）

**Files:** 美术独占docs/art/home-map-production/home-hud-polish-spec.md；开发修改MapSample.ts的header/layoutPlayerHeader/controls必要部分。

**Interfaces:** 美术输出明确720坐标制作建议和窄屏优先级；开发以实际safeInsets、pageMargin(16CSS)和字体度量布局，不把941宽概念比例机械固定。数据仍player.level/experience/money/rating，头像点击骑手。

- [x] 左上头像与“澄川骑手”默认显示名、动态Lv和经验进度组合暖白人物卡，区域小牌在其下。缺少自定义姓名/县名字段时只用已有品牌“澄川骑手”与“县城”，不新增身份存档、不凭空写具体地名。
- [x] 右上紧凑金币/评价胶囊优先同排，图标靠数值，金额增长图标/胶囊向左适配；长数值不换行或遮住人物卡，狭窄时在右侧列上下排列。
- [x] 保长屏和安全区外边距；配送中的小白暂停保原逻辑/触区，放人物区域下方不盖经验/区域牌/地图状态。HeaderClearance取实际绘制下边界；站点定位同尺寸、同底线，现底栏五入口保留。
- [x] 复用头像/币/心/导航图，站点资源保原色；暖白底板/柔影/细描边由引擎绘制，无新图需求；不修改商城/骑手配车/订单状态流程或全局readable。

## Task 4：构建及交付（固定开发＋PM）

**Files:** docs/reviews/home-map-polish-20261101/implementation-report.md、build.log；PM本计划进度和精简交接。

- [x] 完成依赖后必要npm run build:map --prefix delivery-game；有实际构建阻塞仅修阻塞再重建，保完整Cocos诊断。
- [x] 4181沿用现有产物。报告实现范围、修改文件、各新增规则/资源、构建证据及未测项；无需运行用户游戏页面。
- [x] PM根据实际产出报告，不把命令成功当画面/性能验收。用户未说阶段完成，保持已实现未测试。
- [ ] 用户查看真实画面后的反馈与体验验收；用户明确说“阶段完成”才组织集中测试。

