# M1方案A界面优化 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task-by-task. Steps use checkbox (`- [x]`) syntax for tracking.

**Goal:** 将用户已确认的A方案落到当前Cocos配送游戏，保留大厅手机外框，并在完成检查后重启Cocos内置预览。

**Architecture:** 保留OrderBook与经济、地图、存档逻辑。界面重排限定在现有渲染层；内容较长的弹窗固定头部和主按钮，仅内容区滚动。必要时以小型界面辅助模块复用换行、滚动和车辆图片加载，不重构游戏状态。

**Tech Stack:** Cocos Creator 3.8.8、TypeScript、现有node:test与引擎边界模拟、现有Cocos构建脚本。

## Global Constraints

- 用户2026-10-29明确批准A，接单大厅保留手机外框；不实施B任务条主页或C去手机框。
- 白色悬浮顶卡无阴影，保留顶部安全区外12设计单位、左右18设计单位与设备安全区；透明底栏。底栏仅招募/车辆/抢单/地图/账单，抢单仅黄色两字；站点右上、定位右下。禁用仅灰化无事件，不增加状态小字。
- 保留黄色真实地图、10–100米缩放及30米默认、地图顶视车辆80×128设计单位、版权和比例尺；已有路线白描边保留，可加深快捷路内芯至#795020。
- 保留当前一单自动取送、到店2秒、普通自动结算、门口需求不可关闭跳过、D+¥200、全部原经济/经验/存档/账单规则；不改OrderBook、CountyRules、CountySnapshot或其他领域模块。
- 正式图标仍由用户提供；不生成新的正式美术。现有两款侧视PNG逐字节复制到工程资源，再以D/D+正确映射使用。
- 大厅保留10单无分页、刷新额度、餐图、餐名、预计收入、商家、目的地、里程/时间与必要加急/怕洒标签。
- 账单保留12项、日期、≥历史下限及未知—；重排不能补造数据。结算金额和全部原摘要均保留，不添加领取步骤。
- 不操作用户接单/升级流程，不注入或清理用户存档，不改验收结果。允许Cocos停止/重启预览、静态截图和只读运行时节点检查以展示用户授权修改。
- 在现有codex/food-delivery目录实施；当前未跟踪工程是实际基线，恢复点已在docs/reviews/m1-art-implementation/before，不用reset/clean或清理其他工作，不自动提交整套未跟踪工程。

---

### Task 1: 方案A完整界面重排与资源接入

**Files:**
- Modify: `delivery-game/assets/scripts/map-sample/MapSample.ts`, `SampleUI.ts`, `OrderPhone.ts`, `CityMap.ts`（仅配色）
- Create if needed: `delivery-game/assets/scripts/map-sample/PresentationLayout.ts`, `VehicleSideArt.ts`，职责分别为显示尺寸/文本滚动布局与侧视图异步加载；对应.meta由Cocos导入生成。
- Import: `delivery-game/assets/resources/map-sample/vehicles/side-d.png`, `side-d-plus.png`
- Test: 现有`delivery-game/tests/map-hud.test.cjs`, `modal-shade.test.cjs`, `map-vehicle.test.cjs`；仅在引入可复现的布局/异步生命周期风险时添加有意义回归，并在`scripts/test-map.cjs`登记新文件。

**Interfaces:**
- Consumes: `book.player`, `book.list()`, `book.active`, `book.billing`, `billingRows`, `safeInsets`与现有UI绘图/点击封装。
- Produces: 原有MapSample各页面、OrderPhone构造/close接口保持。新辅助接口集中导出且不得依赖OrderBook。共享UI基础继续兼容旧场景；不要全局增大所有label导致旧布局溢出。

- [x] **Step 1: 确认基线与短屏缺口。** 阅读已批准方案`docs/reviews/2026-10-29-m1-art-audit-and-proposal.md`；检查before恢复点。已有基线为184项通过、类型通过。先用现有HUD真实节点测量增加必要失败用例，例如短屏弹窗内容可滚动且主操作在安全区内、账单12项不会漏、车辆图片异步回调不会写销毁节点。纯可逆样式不写镜像测试。

```js
// 验证实际渲染入口输出，使用独立手算的边界与真实book。
// 不从生产布局函数生成期望值，也不读写真实浏览器localStorage。
assert.equal(book.serialize(), savedBeforeOpeningPages);
assert.ok(actionBounds.bottom >= safeBottom);
assert.ok(contentHeight > viewportHeight && scrollView.vertical);
```

- [x] **Step 2: 字级与内容布局基础。** 保留主黄#FFC52D、正文#302B20；辅助字#64695F、分隔线#E3E2D8。字体按最终显示比例选择设计单位，目标主文15–16 CSS px、辅助13–14、关键金额24–28；通过换行/内容区滚动优先保障可读性，而非整卡缩小。设定实际最小字号，字体不能无限SHRINK。关键操作触区目标44CSS px，注意相邻触区不重叠。窄屏/短屏以真实frame与SHOW_ALL比例换算；保留原安全区换算。

```ts
// 内容区结构示意，位置和尺寸在具体页面按可用高度计算。
const viewport = item(card,'ScrollableContent',0,y,width,availableHeight);
viewport.addComponent(Mask).type = Mask.Type.GRAPHICS_RECT;
const content = item(viewport,'Content',0,availableHeight/2,width,contentHeight);
content.getComponent(UITransform)!.setAnchorPoint(.5,1);
const scroll = viewport.addComponent(ScrollView);
scroll.content = content; scroll.horizontal = false; scroll.vertical = true;
scroll.elastic = false; scroll.cancelInnerEvents = true;
```

- [x] **Step 3: 大厅保留手机造型并重排。** 黑色圆角外框/侧键/系统装饰保留，蒙层改黑色alpha153。卡片增高至能容纳清楚字级：餐图与餐名/预计收入先读、商家/目的地分行、里程与时长/必要标签第三层，接单按钮独立留白。10单仍滚动，无分页；窄屏长地址换行、金额不截断；最后一张与底部装饰留距。安全区尺寸不足时先减少装饰留白与可见卡片数。

- [x] **Step 4: 主页与活动面板。** 顶卡按可用宽度分配头像昵称/等级、余额、评价，取消横向压扁内容，长金额为足够宽度或分行；不要省略真实余额。导航仍透明，主次/占位图标尺寸基线统一。路线比较齐列时间/风险，主按钮单一突出，需求文案换行；必要时适当增加面板高度并同步地图视口和定位/版权位置，避免骑手落进面板。配送中保留阶段/剩余时间/进度与2秒取餐文字，不改计时器。

- [x] **Step 5: 内容弹窗。** 通用蒙层60%黑色、白色不透明卡。用安全区内固定卡宽/可用高度取代长内容整体缩小，头部与关闭触区固定；结算实际收入最大，全部summary、评价/经验/余额可完整读取，继续按钮固定底部。门口需求两原有选择保留、无关闭。地图目录完整显示现有解锁条件，未上线继续灰化；内容必要时滚动。

- [x] **Step 6: 账单与车辆。** 账单分钱包1项、今日8项、累计3项，左标签右数值，突出钱包余额/今日收入，保留>=/—语义（界面继续使用原≥字符），滚动内容能读到末项。车辆页用源素材旧电动车/翻新电动车侧视图作主视觉，不重画/裁剪源文件；展示当前车型和D/D+，速度/容量/倍率与升级状态源自配置，禁止硬编码用户金额。加载缓存、失败回退与节点销毁/快速关闭保护沿用MapVehicle的模式。

- [x] **Step 7: 自检并报告。** 先跑相关布局/生命周期检查，再跑`npm test`和`npm run typecheck`；记录真实输出和可能限制。报告到`docs/reviews/m1-art-implementation/implementation-report.md`。不自行构建/启动预览、不提交/推送，交主代理复核与集成，避免导入与构建并发。

### Task 2: 集成复核、构建与Cocos展示

**Files:** 修改范围见Task1；更新`delivery-game/README.md`、`docs/asset-library.md`与本轮交付记录。

- [x] **Step 1:** 从before生成逐文件完整diff，独立中档审查员检查规格与质量，重点新滚动、异步图片生命周期、长金额/安全区和原12项/状态保留。修正实际发现，不重复整套审查。
- [x] **Step 2:** 领域源码和原资源SHA与baseline核对，完整检查/类型通过后执行`npm run build`保存日志。Cocos AssetDB确认新增侧视资源已导入，预览场景为MapSample。
- [x] **Step 3:** 通过MCP启动gameView；读回运行/未暂停状态，获得静态截图或只读真实运行节点证据。必要时恢复窗口显示。只展示，不自动接单/升级或注入存档。4181继续提供最新构建。
- [x] **Step 4:** 记录已做、检查、构建和仍需用户真机复验的范围，向用户交付Cocos预览与入口。没有截图证据时不能声称已完成所有视觉验收。
