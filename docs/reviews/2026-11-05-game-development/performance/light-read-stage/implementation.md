# P0 轻量路线读取——暂存实现交接

状态：**源码候选已实现，仅暂存，未应用、未测试、未构建或部署**。实现线程 `thr_j9izunn7qx`，父PM `thr_axf6i4e89t`，环境 `env_e54zrbdgxt`。仅本目录为本次最终独占写集，原 `assets` 四源未编辑。外部旧暂存的 UI 原始副本及 SHA 清单保留不删。

## 产物与应用前置

- 四份完整候选：`delivery-game/assets/scripts/map-sample/{V2RouteSession,V2GameSession,V2RuntimeController,V2GameUI}.ts`，保持原相对路径及导入，不复制依赖来伪装可运行工程。
- [apply.v4a.patch](apply.v4a.patch)：标准 `*** Begin Patch` / 绝对原路径 `*** Update File` / `@@` / `*** End Patch`，供父PM通过 `patch(mode='patch')` 应用。4文件、8个hunk，+21/-11行。
- [source-sha256.json](source-sha256.json)：初始/静态收尾原SHA、四份候选SHA及补丁SHA。
- [static-review.json](static-review.json)：逐项文本保留检查、调用点计数、内存中精确hunk重建记录。

**应用前必须重新计算全部四份原SHA。任一不匹配即停止，重新读取变动文件并重基/复审；不得盲套、模糊套补丁或用完整副本覆盖已变原文件。** 当前实现者自检不替代父PM规格审查和独立质量复审，不关闭反馈项。

初始原SHA-256（共同目录 `delivery-game/assets/scripts/map-sample/`；静态收尾四值仍相同）：

| 原文件 | SHA-256 |
| --- | --- |
| V2RouteSession.ts | `73d4daea391b506dd38f0fcd25fb04d9ae387e5aa07a148b42bf2699c7839a5e` |
| V2GameSession.ts | `0101ac3eac40b82432d14c2bbb47dde4cdf8913fdb31ddb65fac362697c9af37` |
| V2RuntimeController.ts | `bb6dc40f960f5867b96bf9eeaad218d8d6a9d2aa648b53ce34aa0afcff892d81` |
| V2GameUI.ts | `a33f933e5dc1e41827ac5cfbfaee1563d494d0acceae5fdaebec9321d10a1e96` |

## 精确接口及最小变更

- Route候选 `:15-16,57,59`：新增 `V2RouteProgress`（`Readonly<Pick<V2RouteSnapshot,...>>`）与 `V2RouteMotion`。`progress` 每次仅返回全新 `{tripId,phase,cursor,serviceCharged,serviceSeconds}`，不调用 snapshot/JSON/position。`motion` 返回这些标量加 `position`，只调用一次既有 `this.position`，再复制为 `[position[0],position[1]]`。无 setter；Point保持原可写元组类型以兼容既有消费者，但坐标绝不指向内部数组。
- Game候选 `:18`：`routeMotion` 直接委托 `this.route.motion`。`acceptBatch` 的 tripId、`routeChoices`/`supply` 的标量门禁及 `tick` 各phase/charged读取换为 `progress`；分支顺序、短路语义、advance回调、自动余秒和所有业务动作未改。
- Runtime候选 `:130`：`routeMotion` 仅 `return this.live?.routeMotion || null`。除这一行外整文件逐字相同；无storage、候选、序列化/恢复或时钟读取，30Hz、生命周期、唯一写者及 validate→commit→publish 原样。
- UI仅 `update` 改动：逐帧读 `routeMotion` 调真实 `setRider`；仍以 `tripId:phase:cursor` 判路线变化，变化时才取完整 `routeSnapshot.legs` 并 `setRoutes`。原 `captureView → setRoutes → restoreView`、新trip出发跟随判定和定位顺序保留；不新增拖动后的强制跟随。人物刷新仍在0.5秒HUD门禁之前。
- HUD控制键仍需要权威stop成员；在原0.5秒门禁后显式读取完整快照交给 `pickupGroup`，不伪称此路径已去clone。服务进度标签、订单详情、其他全对象消费者继续原接口。UI的update之外（含车辆、肖像、金额、标题）逐字相同，任何资源均未改。

## 根因与静态前后计数

来源：核心质量报告 `KNOWN-ROUTE-SNAPSHOT-CLONING`；Route原 `snapshot()` 是完整 state 的 JSON 往返，包含legs。计数为**源码调用点/读取策略，不是运行次数、耗时或FPS**，由纯文本脚本生成：

| 范围 | 原 | 候选 |
| --- | --- | --- |
| Game全文件 Route/candidate完整snapshot调用点 | 11（10+1） | 2（serialize与旧routeSnapshot） |
| Game.tick直接 Route.snapshot调用点 | 6 | 0（6处改progress） |
| UI每次有效update的无条件完整路线读取 | 1 | 0（改routeMotion） |
| UI路线视图键变化时读取完整快照 | 复用上述无条件读取 | 1处条件读取 |
| UI节流后stop成员的额外完整读取 | 0（复用上述无条件读取） | 1处，仅HUD门禁通过后 |
| UI全文件routeSnapshot引用点 | 6 | 7（频率分离，并非总调用点消失） |

Game的9处纯标量读取改为progress（本体8处、candidate 1处）。自动blocked分支保留原两次短路读取位置，未另加缓存或改变动作边界。

## 保留的完整clone、验证与静态证据

- Game `serialize` 与完整 `restore` 段逐字相同；原公开 `routeSnapshot` 和 `Route.snapshot` 不改。`A-QUALITY-01` 的 `t.action && r.phase==='service' && charged` 拒绝断言完整保留。
- Route只有两类型和两getter新增；原position、merchantKey的“经营资格+权威配对唯一”、同店分组、ready/continue、legacy门禁和权威legs全集验证逐字保留。expectedLegs缓存未变，不拿它冒充clone已消失。
- 原Route/Dispatch/Trip恢复、序列化、事务候选/提交及其他JSON复制均仍存在。Runtime的30Hz事务仍承担其原完整读写/验证成本；本补丁不声称消除此成本。
- 全部8个hunk在内存中按唯一精确文本上下文重建后，与四份完整候选逐字相等；没有向原文件执行补丁。13项文本保留断言均成立；这是实现者静态自检，不是测试或独立审查结论。

## 引用、时钟风险与未执行案例

追定义：原 `MapTypes.ts:1` 的Point是二元组；`RoadRouter.ts:59-69` 的零segment回退会直接返回 `route.points[0]`，故新motion必须再复制坐标，不能仅返回既有position。`CityMap.ts:281-297,338-348` 表明setRider保存传入Point、setRoutes清follow、capture/restore保存视图、触摸取消follow；这些消费者及原位置算法未修改。

- progress/motion为分离对象但不做运行时freeze；修改返回标量/坐标按源码不应回写内态，仍待运行验证。旧position/routeSnapshot接口的既有引用语义未顺手改变。
- motion只读最后成功发布live状态，不读wall clock、不插值/外推/改速；不会把30Hz事务发布变成渲染帧推进。每次需要phase刷新时仍重新读progress，未跨accept/begin/continue缓存旧phase。
- 待阶段集中验证（均**未执行**）：返回对象/坐标隔离，尤其零长度腿；真实沿路/取消边中位置；新trip同phase同cursor换腿；拖动取消跟随与服务/ready边界视图恢复；HUD未满0.5秒时人物仍刷新；同店多成员扣点/ready/continue/自动余秒；Game1–4合法恢复及互斥非法组合、legs篡改拒绝；事务失败不发布/生命周期/唯一slot。未制造任何真实或合成存档。
- 未运行tests/typecheck命令、TS游戏函数、故障注入、游戏浏览器、Creator、构建或部署。编辑工具自动返回暂存文件因相对依赖未随副本复制而产生的LSP诊断；这不是原工程typecheck结果，未为此改导入、复制依赖或启动编译修复循环。早先外部UI副本写入的自动npx可用性探测返回skipped/not usable，也没有成功的类型检查结果。
- NPC帧内补额度时点不在本任务；不接地图制作/素材/几何/边界，也未向地图线派工。没有commit/push/新子Agent。未测量性能、不声称卡顿清除、帧率通过或98%达标。
