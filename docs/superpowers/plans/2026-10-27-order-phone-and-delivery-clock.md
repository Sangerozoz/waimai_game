# T01-R2 Implementation Plan

> Execute the user's authorized revision inline, preserving existing uncommitted work. Use executing-plans and the existing codex/food-delivery checkout. R1 snapshot is `.merge-backups/2026-10-27/map-sample-delivery-v1.zip`.

**Goal:** 主动通过模拟手机接单，在更多真实道路地址之间配送，以真实分钟显示、最多 12 秒播放，并默认跟随骑手。

**Architecture:** 离线地图给出可达地点池；RoadRouter 保留原始行驶时间；DeliveryClock 独立完成显示时间和动画时间转换；OrderBook 持有订单、骑手位置与当前配送；Cocos 消费状态并绘制地图、路线卡和手机浮层。

**Tech Stack:** 现有 Cocos Creator 3.8.8、TypeScript、OSM 离线数据、Node 测试。

## 全局约束

- 用户要求：30 分钟约 5 秒，动画最多 12 秒；时间与路径插值一致。
- 真实道路、虚构地名；不虚增米数来制造长单。
- 当前处于 T01 返工；不接入未验证的经济/评价/存档，不改原 Main 场景或已有 DeliverySession 工作。
- 保留 R1 恢复快照；每项记录检查结果，真机不能以浏览器代替。

## Task 1：多地点、真实距离与两套时钟

文件：转换脚本、地图来源与 city.json；修改 RoadRouter.ts/MapTypes.ts；新增 DeliveryClock.ts 和测试。

接口：RoadRouter.find 返回实际道路行驶秒数；deliveryTiming(travelSeconds) 返回 displaySeconds/animationSeconds；deliveryProgress(travelSeconds, elapsedAnimation) 返回路径插值时间、游戏剩余秒数与比例。

- [x] 保存 R1 恢复边界，获取较大范围路网，选择强连通地点池，验证导入可重复。
- [x] 先写 15/30/60/90 分钟换算、12 秒上限、半程位置与剩余时间检查，确认旧代码不具备能力。
- [x] 最小实现独立时间转换；原始路径秒数不提前压缩。
- [x] 检查多地点可达、地图实际距离和长短单时间差异。

验收：30 分钟为 5 秒、90 分钟为 12 秒；动画半程同时对应路径半程与游戏时间半程；数十个地址来自有效道路节点。若大范围数据服务不稳定，记录来源失败并使用可验证的正式提取，不拼造直线道路。

## Task 2：持续订单与完整接单状态

新增 OrderBook.ts、订单逻辑检查；修改地图取餐标记与跟随接口。

接口：OrderBook.list(page)、accept(id)、routes、depart(index)、advance(dt)、pause/resume、complete/cancel；唯一状态含当前骑手节点、已接订单、选路与动画进度。订单只在完成后替换，手机开关不刷新订单。

- [x] 先写固定随机源下多终点生成、一次一单、接单前不动、取餐+送餐路径、暂停及到达补单检查。
- [x] 实现生成、路线组合、状态转移，维持五单页面和多页浏览。
- [x] 完成后更新骑手位置并补单；出发开启跟随，拖动可解除、定位可恢复。

验收：连续多单出现超过三个不同终点，保留其他待接订单；骑手不瞬移，取消选路回到原订单；暂停不走表，到达只处理一次。

## Task 3：模拟手机与可试玩交付

修改 MapSample.ts/CityMap.ts，新增 OrderPhone.ts，复用 SampleUI.ts。

- [x] 地图初始显示接单按钮和待命信息，点击打开有手机外框、状态栏、订单列表、翻页与关闭操作的浮层。
- [x] 订单点击接单后收起手机、进入路线卡；显示分钟/小时与距离。
- [x] 出发后跟随、游戏剩余时间、到达反馈及返回接单接通。
- [x] 类型检查、算法/订单检查、Cocos 构建、浏览器实际点击和截图验证；独立审查并修复影响本轮的问题。
- [x] 更新当前任务状态、验收记录和恢复快照，交用户体验。

当前状态：2026-10-28 技术检查通过，待用户体验。18 项检查、Cocos 类型检查和构建通过；浏览器接单到送达路径已走通。黄色主题按用户补充要求实施。后续仍按完整 T01 的经济与存档验收推进，R1 的三个固定订单不再作为产品需求。验证记录：`docs/reviews/2026-10-28-order-phone-and-delivery-clock.md`。
