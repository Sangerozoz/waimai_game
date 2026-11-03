# 车辆商城效果稿落地 Implementation Plan

> **For agentic workers:** 执行subagent-driven-development的分工/依赖记录方式，按项目AGENTS复用固定开发/美术会话，同checkout保留全部未提交。用户明确禁止过程测试、独立复验和渲染矩阵，不执行技能默认测试/提交/新worktree/新角色步骤。

**Goal:** 将已获用户许可的商城v2画风、构图和页面职责落实为可试玩车辆商城，同时把主角配车统一到骑手页面，并修正D/D+混同。

**Architecture:** 固定开发单写业务代码；PM用内置生图产干净背景与无字共享UI皮肤，固定美术核对既有车型与接入说明。商城按车型浏览/购买，骑手页按独立车辆配置，沿用VehicleOwnership/OrderBook交易与保存边界，不新增NPC经营。布局/加载可独立为VehicleShopPresentation等局部模块，不重构无关地图/经济。

**Tech Stack:** Cocos Creator 3.8.8、TypeScript、现有资源加载/车辆库存、PNG背景与皮肤、节点补间。

**2026-11-01交付状态：** Task1资源生产交接、Task2商城与统一骑手入口、Task3可试玩构建与文档交付均已实际完成；代码细节与构建证据见docs/reviews/vehicle-shop-20261101/implementation-report.md，资源交接见docs/art/vehicle-shop-production/asset-handoff.md。未测试、未渲染复验、未代用户体验验收，未操作用户存档。最新构建build-scene-adjustment.log保留原诊断。首页只生成概念图，未改场景代码。下列复选框为派工原清单，实际交付状态以本段和证据为准。

## Global Constraints

- 依据spec `docs/superpowers/specs/2026-11-01-vehicle-shop-and-assignment-design.md` 和用户本次“按照效果图去做，该生成素材生成；D/D+不一致要处理”。用户补充“主角的换车也在骑手里边，主角也是骑手”。
- 视觉目标 `docs/art/vehicle-garage-concept/vehicle-shop-screen-v2.png`；风格图5、左上暖光、车库磨损材质/深炭灰/暖橙。不能退回普通矩形资料列表。
- 不使用整屏概念图作交互页面或裁其中车辆；10档侧45母版分别复用。D圆大灯/旧漆/旧橙箱，D+方灯/更整洁/不同车体；不得同图复用、镜像或靠换色区分。
- 不改变价格、库存上限、阶段解锁、schema/存档语义，不启M3–M7/NPC收益/招募。购买不自动装备；无使用中/主角座驾/占用姓名出现在商城。拥有数旁不放金币。
- 现有D升D+ ¥200入口保留在骑手现用车辆详情；商城D/D+购买仍¥500/700，不能混价。
- 主角是骑手页中的玩家角色。底栏原招募入口改为可打开现有骑手信息的“骑手”，头像可指向同一页；不设平行主角换车页面。仅主角真实已有，不能虚构其他骑手/配车/收益。
- 用户未说阶段完成：不跑测试/typecheck/回归/独立渲染；允许必要的可试玩构建。不得操作用户玩法/存档。不提交、推送、清理或覆盖其他工作。

## Task 1：资源生产与车型复用说明

**Files:**
- PM创建 `docs/art/vehicle-shop-production/` 下无字环境与皮肤源图、实际prompt、生成metadata。
- 固定美术创建同目录 `asset-handoff.md`、`manifest.json`，只维护本目录资源文档；开发负责导入资源。

**Interfaces:**
- 消费商城v2，仅背景/材质参考；D与D+等分别取既有原图。
- 交付至少：1干净车库背景，1深色面板皮肤，1普通卡框皮肤，1暖橙按钮皮肤。卡框选中态可叠橙边，页签可共享按钮/面板；使用同质感组件，避免重复生图。

- [x] PM使用imagegen制作无车/无字/无UI车库环境，确保连续地面与明确接地点。
- [x] PM使用imagegen制作透明无字可拉伸皮肤，保边角留白，原图不覆盖。
- [ ] 美术核D/D+精确路径、灯形、漆面与结构，说明所有十档复用路径；不重绘车型。
- [ ] 美术记录源图尺寸/透明/九宫格候选安全边与开发接入方式，标生成实物和未测状态。

## Task 2：商城与统一骑手入口

**Files:**
- 固定开发修改 `delivery-game/assets/scripts/map-sample/MapSample.ts`，按需要新增局部展示模块、资源key；仅开发导入 `assets/resources/map-sample/anime/vehicle-shop-20261101/`。
- 复用 `VehicleSideArt.ts` / `CartoonArt.ts` 车辆映射；仅为本轮布局/皮肤加载需要做局部修改。
- 保留 `VehicleOwnership.ts` / `OrderBook.ts` 经济与保存行为；默认无需迁移。

**Interfaces:**
- 商城读取VEHICLE_*、book.vehicleInventory、book.player.cashCents，调用原`book.buyVehicle(tier)`。
- 骑手页主角配车调用原`book.selectPlayerVehicle(id)`，现用D升档沿原`book.upgradeVehicle()`；保存经原`act`/pending处理。

- [ ] 商城上半区车库/大车、名称档位/速度载重、真实余额/购买按钮；浏览车型独立于实际装备车。
- [ ] 下半区“全部车型/已拥有”按车型聚合、三列收藏优先；10档滚动，名称/状态可读。短屏分配展示与列表空间，安全区默认内16CSSpx，完整购买热区不得被遮挡。
- [ ] 使用真实母版按可见车体统一尺度及接地；D/D+映射显式不同；初始浏览可以是现用车型，但商城不显示归属标记。
- [ ] 点击车型更新预览而非立即开通装备；购买沿原确认/冻结/资格/上限/余额，成功刷新数/余额并保正在浏览车型和筛选。未来档可预览但禁购。
- [ ] 统一“骑手”入口，主角信息内显示真实已配车与配置按钮；配置列表按具体ID、用可读编号，不出现购买入口；主角当前配置可识别，其余真实空闲车可选。
- [ ] 移除商城所有装备/换车操作；主角配置成功释放旧车、刷新真实主角和地图车。已有升级D+功能移到骑手现用车详情，不丢现有能力。活动单期间沿原禁止更改规则。
- [ ] 皮肤提供轻按压/选中/车预览过渡；热区稳定，旧异步加载不能回盖新选择，离页取消补间，不要求序列帧或骨骼。

## Task 3：可试玩交付

**Files:**
- 开发报告 `docs/reviews/vehicle-shop-20261101/implementation-report.md`，记录变动/资源路径/来源SHA/构建证据/未测试。
- PM更新角色交接与阶段报告，记录下一个首页任务仍先效果图。

- [ ] 资源就绪后，开发一次必要`npm run build:map --prefix delivery-game`产出试玩构建。失败只处理构建阻塞，保原诊断；不借构建附带测试。
- [ ] 保留原4181服务，确认实际服务指向当前产物属于交付动作，不开展玩法/存档操作。
- [ ] 如实交付“已实现、可试玩构建已生成、未测试，待阶段集中测试与用户体验”。用户实际查看自行点击，不代用户验收。
- [ ] 首页后续先整屏效果，不在本轮顺手改首页代码。
