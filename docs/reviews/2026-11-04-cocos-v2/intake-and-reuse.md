# 本轮开发授权与旧实现复用盘点

用户明确允许地图仍生成时先写其它Cocos功能。采用最新二八版参数，不恢复38分钟小队或均匀扩员旧候选。

## 已有实际调用链

Creator 3.8.8，delivery-game/assets/scripts/map-sample/MapSample.ts加载地图数据后建立CountySaveStore，调用OrderBook.restore或new OrderBook。CountySaveStore负责单写者权限、提交封装、旧档备份和未来版本保护；OrderBook管理订单、路线、玩家、账单与车辆。

OrderBook当前序列化schema7（兼容1—7），有旧途单playerBefore/receipt/ruleVersion。VehicleInventory已保存具体实例及主角配车。当前buyVehicle仍限制tier<=2，存在拥有数量限制；旧车型tier1既作初始车又作商店车型。CountyRules包含旧评价收入倍率，不可仅更新报价表就宣称新版经济已生效。

现有订单仍围绕一个AcceptedDelivery运行。V2普通容量组批、NPC并行经营、广告专送独占批次及600秒自动控制，不能从现有单单运行状态直接推断已经实现。

## 本轮接续方式

先实现正式TS逻辑和显式适配入口；经济开发拥有现有业务适配范围，奖励开发仅新增独立目录。先保护旧档，避免直接改低层常量后让旧途单追溯新价格。旧图、道路与美术工程不参与这次改动。

未接正式场景/SDK/UI的部分一律列出；代码写入不等于编译通过、游戏测试通过或存档迁移验证通过。用户仍要求“阶段完成”后集中测试，这轮只写对应待执行检查用例。

## 会话与模型

用户再次强调约20轮换新会话，工具调用不计一轮。用本目录实现报告和计划文件做简短交接，不复制全段聊天。复杂经济/旧档用Sol high，奖励状态模块用Sol medium；禁止GPT-6-astra。没有独立工作的简单资料不额外拆Agent。
