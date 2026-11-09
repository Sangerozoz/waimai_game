# SLOTS-FIX01：实际只读API与UI接缝（stage-only）

本补充只适用于fix01-manifest.json的新stage SHA。原contract.md及既有PASS/FAIL保留历史身份。以下方法已落盘，不是提案；未编译、未运行DTO或游戏。

## Economy实际定义

`assets/scripts/domain/V2EconomySession.ts:14,225-242`：

- `V2DeliveryEffects`：profileId:string、speedRelativeToStarter:number、incomeFactor:number、capacity:V2Capacity。
- `get hasEquippedVehicle():boolean`：从验证后的私有hero.vehicleId读存在性标量，不返回车辆。
- `get nextBatchEffects():V2SlotVehicleEffects|null`：当前主角配车的新profile效果；无车null。
- `deliveryEffectProjection(quoteId:string|null):V2DeliveryEffects|null`：quoteId是Dispatch从原pending选择规则取得的标量ID；非null须对应私有activeQuotes。slots活单直接读取已验证、已冻结terms的profile/speed/income，显式新建capacity对象。kg活单沿原vehicleEffects旧公式，不借新表重估。null代表当前无pending，按当前资产的新slot效果；无车null。
- `vehicleEffectProjection(vehicleId:string):V2SlotVehicleEffects|null`：拥有实例当前slot效果，不存在null。
- `riderEffectProjection(riderId:string):V2SlotRiderEffects|null`：已拥有NPC当前slot培养效果，不存在或hero为null。

`this.snapshot.state`是类内权威对象，不是调用公开state/snapshot/serialize取得的副本。上述接口不创建draft、不读时钟/存储、不推进、不draw、无全局缓存。唯一查询开销仍包括实例/订单数组查找与纯参数求值。

## Dispatch与Game实际委托

`V2DispatchSession.ts:58-62`提供同名hasEquippedVehicle、deliveryEffects、nextBatchEffects以及两种EffectProjection委托。deliveryEffects保留原`orders.find(pending && batchIds.includes(id))`选择顺序，只把id交给Economy；不假设Economy.activeQuote与Dispatch数组首项在所有合法组合中同序，不克隆历史订单。

`V2GameSession.ts:29-35,107`将效果委托给Dispatch，两个Game效果getter无车仍抛原文“主角未配车”。普通候选无车仍[]、专送仍null、自动推进仍停止；三处存在性判断走布尔投影。容量/候选/价格、食品、ETA、补给、时间与恢复校验不变。

## Runtime/UI公开形状保持

`V2RuntimeController.ts:163-169`仅改读取链，未改方法名、参数、字段：

- deliveryEffects：{profileId,speedRelativeToStarter,incomeFactor,capacity}，未就绪/无车null；旧活单capacity.version仍kg-v1，新活单slots-v1。
- nextBatchEffects：{profileId,capacity,capacitySlots,speedRelativeToStarter,incomeFactor}，未就绪/无车null。
- vehicleEffects(id)：同V2SlotVehicleEffects；未就绪/未拥有null。
- riderEffects(id)：{profileId,incomeFactor,baseIncomeFactor,fixedServiceReduction}；未就绪/未拥有/hero为null。
- vehicleUpgradeQuote/riderUpgradeQuote及quoteCandidates代码一字未改；成本与current/next/nextLevel及新profile的fromLevel/toLevel/profileId保持原实装。满级/null/异常行为未调整。

UI输入锁定为layout/ui-funds-stage-1106/assets/scripts/map-sample/V2GameUI.ts，SHA240bb6bc07de7add31482e1cd330a886e46e705695a01f1a7cdbab0b45bf4c46。已静态追:697的deliveryEffects及:825的nextBatchEffects.capacity，未修改页面或再绑UI。字段兼容依据为原/新源码与Profiles接口对照，不是执行DTO证明；PM/B需对新依赖做窄重绑，旧UI PASS不自动赋给新依赖。

## 嵌套脱离与合同身份

冻结slot capacity使用对象字面量新建，不返回quote.terms.capacity。旧kg capacity同样新建。当前/拥有资产投影调用保留原SHA的Profiles.slotVehicleEffects:31-36，该函数每次新建外层及capacity，读取参数表仅取标量；slotRiderEffects:38-40也新建标量对象。没有返回vehicle/rider/参数行、共享状态数组或缓存对象。Readonly类型不是隔离证明，本次依据是这些实际构造与完整未变的验证入口。

没有新增持久字段/存储版本/价格策略/时钟或迁移规则；新slot活批按原冻结条款，旧kg活批继续旧解释，下批才读当前资产新效果。
