# T01-R：真实路网地图样板执行计划

2026-10-28 用户已给出 R1 反馈，当前后续执行 [T01-R2](2026-10-27-order-phone-and-delivery-clock.md)。本文件保留 R1 的历史验收边界，三个固定演示订单不再是现行限制。

> Execute inline in the current authorized workspace; preserve all pre-existing changes. Current branch is codex/food-delivery. User authorized the sample and its technical implementation.

执行主流程：[game-idea-to-plan Skill](/Users/sanger/.codex/skills/game-idea-to-plan/SKILL.md)。当前是 T01 返工中的**代表性样板**；旧版被用户否决，本样板尚未通过用户体验验收。范围见 [样板规格](../specs/2026-10-27-real-road-map-sample.md)。通过后接回 T01 的完整配送循环，T02 及后续系统仍以前置任务验收为条件。

**Goal:** Deliver a polished Cocos map sample using real OSM roads, fictional labels, and verified route animation.

**Architecture:** Offline OSM extraction produces shared geometry and a directed road graph. A pure TypeScript router computes paths and timed positions. A separate Cocos scene renders the city and a working route-selection interface without touching the existing delivery save.

**Tech Stack:** Cocos Creator 3.8.8, TypeScript, Python importer, Node tests, local Web Mobile preview.

## Global Constraints

- Work inside delivery-game; leave Main.scene and the existing DeliverySession changes intact.
- The source map is real and attributable. Game labels are fictional. No live map service is required at runtime.
- Use Cocos MCP for scene creation, component assignment, save, and readback.
- Expose only implemented interactions. Sample delivery does not mutate player money or saves.

## 已确认与待验证

| 条目 | 状态与依据 |
| --- | --- |
| 二维地图经营风格，真实道路、虚构地名 | 已确认，用户选择并授权实施 |
| 一块街区、8 个地点、3 组演示订单 | 本次技术取样，不是正式内容数量 |
| 速度、颠簸、时间压缩、演示价格 | 临时配置，不覆盖正式经济规则 |
| 画面质量、操作理解、手机手感 | 待用户体验及真机验证 |

要回答的问题：能否用可重复的数据流程，制作清晰、可操作的地图，并让选路、耗时与骑手位置一致。实验边界是一块街区和三组演示订单；不在本阶段扩展整座城市或经营系统。

## 当前任务卡

### S01：可信且可重复导入的道路与配送路径

- **目标与依赖：** 在已确认的真实路网方向下，使虚构地点之间能沿有效道路配送；输入为可追溯的 OSM 提取。
- **做 / 不做：** 保留源节点、方向和实际几何，生成三种偏好并去重；不接在线瓦片、实时路况或完整导航，不把真实地名带入运行数据。
- **交付与集成：** `data/map-sample/`、转换脚本、`city.json`、`RoadRouter.ts`；米制坐标和路线契约统一在 `MapTypes.ts`。
- **可观察验收：** 重导入字节一致；逆行需要绕路；几何交叉不凭空连通；演示地点能双向到达；里程、计时、分段移动一致；首单有不同合理路线。
- **验证：** 助手执行手工图与真实图的自动检查、重导入比对。
- **回退与未知：** 新目录与原逻辑隔离；数据孤岛时调整范围或地点，不能补脱离道路的直线。
- **状态：** 技术检查通过。6 项测试通过，其中逐段核验 168 组起终点与偏好组合；重导入一致。

### S02：看地图、比较路线并完成一段配送

- **目标与依赖：** 使用 S01 数据和原工程 Canvas/相机，交付可审阅目标画面及操作反馈的独立样板。
- **做 / 不做：** 地图、虚构标签、取送点、骑手、订单卡、选路、全景、缩放、拖动、定位、暂停/继续、到达/重看/下一单；不加未实现的经营入口，不结算金额或写存档。
- **交付与集成：** `CityMap.ts`、`SampleUI.ts`、`MapSample.ts`、通过 Cocos MCP/AssetDB 创建并读回的 `MapSample.scene`，输出 `build/map-sample/`。
- **可观察验收：** 路线高亮与卡片同步；缩放拖动后路径与道路重合；骑手沿选定路到送点；暂停停表；送达后可重看、换单；宽桌面和长手机比例可操作；来源署名可见并能打开许可说明。
- **验证：** 助手执行类型检查、构建和实际浏览器操作，保存截图；双指手感与手机性能需真机证据。
- **回退与未知：** 原 `Main.scene` 保留，样板内原控制器禁用，原存档不接入。画面不接受时继续返工本样板。
- **状态：** 构建、类型检查与浏览器完整路径检查通过；地图质量待用户体验验收，真机未测。证据见 `docs/reviews/2026-10-27-real-road-map-sample.md`。

### S03：交付样板并返回 T01 的完整循环

- **目标与依赖：** 基于 S01/S02 的技术证据，交付可直接试玩的入口、截图、运行说明、状态记录和恢复快照，供用户判断体验。
- **验收与状态：** 待用户体验验收；技术证据、截图、构建与恢复快照已备齐，由用户判断「已接受 / 需返工」，不能用构建成功代替接受。
- **通过后接入：** 回到 T01，将地图接入 `DeliverySession` 的主动接单→选路→配送→到达→结算→保存→下一单。先统一实际路径、预计时间、车辆/天气倍率、订单时限与餐损，避免移动和结算使用两套时间。已接受路线与抽样须保存，恢复不能换路或重复发奖。
- **完整 T01 出口：** 新存档完成首单，获得正确的钱/评价/经验，回到有容量保证的五单列表；刷新可继续且不重复奖励；用户接受完整体验后才展开 T02。

## Task 1: Offline map and routing

- [x] Download one bounded OSM extract with roads, buildings, water and parks; preserve provenance and ODbL notice under data/map-sample/.
- [x] Convert lat/lon to local metres. Keep source node IDs, direction, road class and real polygon geometry; exclude unsuitable access routes.
- [x] Create assets/scripts/map-sample/MapTypes.ts and RoadRouter.ts. Interface: `new RoadRouter(data).find(start, end, preference)` and `routePosition(route, elapsed)`; route includes length, duration and segments.
- [x] Test hand-built directed/disconnected graph cases before implementation. Verify candidate paths against the actual imported graph, their timing and endpoints.
- [x] Generate map data in assets/resources/map-sample/city.json with geometry, graph and curated fictional POIs. Save conversion script for reproducibility.

## Task 2: Cocos map scene and visual sample

- [x] Create CityMap.ts for cached geometry, route strokes, labels, pins, rider, drag and zoom.
- [x] Create MapSample.ts and SampleUI.ts for the portrait map, order selection, route options and delivery/replay controls.
- [x] Add a separate MapSample.scene through MCP using the existing Canvas/camera configuration, replace only the sample scene's controller, then save and read back.
- [x] Typecheck, preview, inspect screenshots at overview and route focus, and exercise selection, zoom, pan and completion.
- [x] Build a separate web output, preserve source attribution and deliver preview with verification limits.

## Progress

- Direction and scope confirmed in conversation.
- Existing implementation is preserved in place; no destructive operations authorized or planned.
- [x] 本轮挂回 T01 返工，并更新总规格、总计划。
- [x] 源数据、许可、转换脚本、真实路图与位置计时检查。
- [x] 独立场景接入，类型检查及 Web Mobile 构建。
- [x] 浏览器完整操作路径验证及截图交付。
- [x] 独立审查，关闭双指中心点计算问题；最终 9 项地图检查通过。
- [ ] 双指操作、手机首屏与帧率真机实测。
- [ ] 用户接受地图样板。
- [ ] 接回 T01 经济和存档循环并重新验收。
