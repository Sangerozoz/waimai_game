# 既有美术接入与游戏启动 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task. 用户已明确要求直接接入并启动，无需再次询问执行方式。固定开发负责业务源码；用户测试节奏覆盖技能中的TDD、逐改测试与自动提交默认要求。

**Goal:** 将已经生成且用途相符的素材实际接入当前Cocos游戏，构建并启动4181试玩入口，让用户自己查看。

**Architecture:** 复用现有俯视地图、地图地区页、头像及弹窗基础。增加独立资产映射/异步展示模块管理本批原图、裁切和加载，CityMap仅接环境表现，MapSample仅接地图页和只读人物展示；不使用新生成的整屏概念图当游戏背景，不重排首页为新大厅。

**Tech Stack:** Cocos Creator 3.8.8 / TypeScript / 既有map-sample资源加载与Graphics/Sprite。

## Global Constraints

- 用户2026-10-31原话：“你还是先把我们做好的素材应用上去，启动游戏让我看看吧”。本次为明确实施授权，概念比较停止。
- 当前checkout全部未提交/untracked保留，不新worktree、不reset/clean、不自动commit/push。
- 唯一风格：docs/art/2026-10-30-style-bible.md。顶视地图、侧45展示与地区海报用途不混淆。
- 地图道路/建筑/POI位置及路线、相机、时钟、接单、取送、库存、价格与存档规则保持；只有county可玩。路线蓝/黄/绿；不恢复火焰。
- 不运行测试、typecheck、回归、独立复验、渲染矩阵；用户未说“阶段完成”。允许必要构建、静态HTTP交付、按本次指令打开游戏；不替用户接单/购买/换车/清存档。
- 21张为候选，不得称全部可用/验收。原图不覆写；P04身份过似、未完成的NPC业务不得伪装为已实现。确不适用项逐项列明，不因一项待修阻塞其他可用项。
- 现有18车辆、50餐品、图标继续保留，不重复生成。

## Inputs and ownership

- 输入：docs/art/prompt-batches/FULL-PRODUCTION/manifest.json、docs/art/user-deliveries/full-production/、docs/art/2026-10-31-production-progress.md、docs/team/handoffs/development-current.md。
- 美术只写docs/art/2026-10-31-integration-placement-notes.md，提供静态用途/裁切建议，不共改代码或原图，不再生图。
- 开发单写delivery-game/assets及docs/reviews/existing-art-integration/；可新增一个批次资产模块，避免把所有图像代码挤入MapSample。
- PM写本计划、收交付、检查构建/服务交付记录并打开试玩入口，不补跑测试。

### Task 1: 资源映射与地图屋顶

**Files:** 新建批次资源目录及资产映射模块；修改delivery-game/assets/scripts/map-sample/CityMap.ts。

**Consumes:** FULL-PRODUCTION真实原图、既有CityData建筑/道路几何、当前异步加载惯例。
**Produces:** 可被地图与页面复用的图像加载/尺寸裁切映射；地图屋顶呈现。

- [ ] 复制真实原图到资源目录，保存来源映射；原件字节不变，静态alpha边界用于SpriteFrame裁切，不用图片重生成代替接入。
- [ ] 在既有可见地图瓦片上挂顶视屋顶候选。只选形状/朝向/尺寸能合理容纳的建筑，等比适配，不把整张图拉扯进任意多边形，不把建筑图片贴到路上或覆盖POI。真实建筑图形保留为无图/不匹配时回退。
- [ ] 对可见立面候选可采用合理的屋顶裁切；若不能保持严格顶视则留待修，不强行应用。保持地图尺度和暖光，限制瓦片内节点/并发加载，离屏释放与异步完成需检查节点存活。
- [ ] 报告实际使用的T编号及未用项，不将仅复制文件算作可见接入。

### Task 2: 地区展示与人物展示

**Files:** 修改delivery-game/assets/scripts/map-sample/MapSample.ts，复用批次资源模块；若需要可拆出纯展示模块。

**Consumes:** 任务1资产映射；现有openMaps地区列表、头像HUD、dialog与scrollContent。
**Produces:** 游戏内可见城市海报/地标与只读人物展示入口。

- [ ] 在现有地图地区页放入五地区展示图与对应地标，文字仍引擎绘制；县城现有点击语义保持，其他地区明确未开放，不添加切城行为或放宽条件。
- [ ] 展示图伪字/留白问题用保留主体的裁切处理；无法处理项用地标或原底回退并报告。展示图不得替换配送路网。
- [ ] 现有头像可打开只读人物展示：初始已接受主角全身、当前真实等级/评价等现有资料；P01–P03作为明确标注的造型预览，不应用任何未确认成长阈值、不提供实际换装、不改变头像身份/数值/存档。按用途保持光晕在独立展示底内，不贴上旋转地图。
- [ ] P04独立NPC身份错误留待重制；P05无NPC业务则只登记待对应阶段，不虚构当前顾客/招募角色。招募入口仍保持原禁用。
- [ ] 展示入口/返回不改变当前配送状态；沿用安全区+16、短屏滚动与既有接单后底栏隐藏规则。

### Task 3: 构建与启动交付

**Files:** docs/reviews/existing-art-integration/implementation-report.md、asset-manifest.json及构建日志。

- [ ] 记录本轮改前副本、增量与实际接入清单，区分可见接入/复制备用/待修。
- [ ] 运行必要构建：npm run build:map --prefix delivery-game。保留原始日志和子进程诊断，不附带测试。
- [ ] 复用或启动http://localhost:4181/服务，静态HTTP交付记录当前产物，不执行游戏行为。
- [ ] 向PM报告实际可见入口、未接项、构建结果与启动状态，标“已实现，未测试，待阶段集中测试”。PM随后按用户本次指令打开该游戏供其体验。

## Acceptance and stop

验收目标是实际资源进入当前游戏并提供可打开构建，不是再出网页/拼贴概念稿。用户自行看效果和操作；本次不代填审美验收，也不宣称无测试缺陷。没有测试任务、没有新阶段经营功能、没有发布操作。
