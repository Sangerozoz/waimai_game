# 阶段一点位与附近派单实施计划

> **For agentic workers:** 按当前用户授权在本会话依次执行；复用当前共享工作目录，保留已有未提交改动。页面操作由用户负责。

**Goal:** 消除边缘营业点位，使普通取送全程主要10–20分钟、少量20–30分钟。

**Architecture:** PlaceCatalog派生150米内缩营业区和补充地点，原地点身份保留。OrderBook以真实道路和当前车速执行8条20分钟内、最多2条30分钟内配额，并确定性筛选旧候选。CityMap仅绘制营业区点位，旧活动路线保留。

**Tech Stack:** Cocos Creator 3.8.8、TypeScript、Node test。

## Global Constraints

- 页面操作与体验验收由用户完成，不自行操作浏览器。
- 保留真实路网、原始city.json、经营进度、每日次数和旧在途/回执。
- 地图显示范围和30–100米缩放不变；营业点位距边界至少150米。
- 普通新单全程≤30分钟，每批至少8条≤20分钟，目标10–20分钟；旧外城回城兼容另记。

## Task 1 · 点位安全区与兼容

Files: MapTypes.ts、PlaceCatalog.ts、CityMap.ts、tests/city-content.test.cjs。

- [x] 保存修改前真实v3 idle/routes/running/done夹具，记录旧地点池身份。
- [x] 增加实际地点池回归：40/120内部点位、边界150米、原272地点不移动；运行 `npm run test:map` 看失败。
- [x] 增加dispatchBounds，保留旧地点并补足内部数量；地图过滤边缘营业点，旧取送标记照常显示。
- [x] 检查新旧可信mapId，并运行地点及在途兼容回归。

## Task 2 · 道路时长和附近取餐

Files: OrderBook.ts、tests/city-content.test.cjs、tests/order-book.test.cjs。

- [x] 新增首批、两次刷新、连续完成订单的真实城区回归：每批10单，全部≤1800秒，至少8条≤1200秒，目的地唯一。
- [x] 新增修改前v3迁移回归：经营/每日/骑手不变，活动完整保留，旧候选自动筛选，二次恢复不重抽。
- [x] 运行 `npm run test:map` 留存失败。
- [x] 按实际取餐道路距离排列商家，按两段总道路时长选择目的地并补齐配额；接单的备选路线也限制1800秒。
- [x] 旧候选按当前位置筛选；缺额确定性补充，不消费免费次数或业务随机；旧外城保持既有回城例外。
- [x] 运行聚焦回归并检查实际批次分布。

## Task 3 · 交付与验收

Files: README.md、docs/acceptance/2026-10-28-stage-one-revision.md、acceptance-revision/index.html、docs/reviews/stage-one-locality/。

- [x] 更新验收预期为营业留白与全程时长分布，保留用户历史结果和已有记录键。
- [x] 执行 `npm test`、`npm run typecheck`、`npm run build`，记录结果及本轮前后统计。
- [x] 检查构建和4181入口一致；不操作页面、不改用户localStorage。
- [x] 报告代码结果与用户待验的精简步骤，阶段一保持待用户验收。
