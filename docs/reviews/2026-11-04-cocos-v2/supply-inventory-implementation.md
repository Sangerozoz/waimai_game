# V2第五批：完整补给目录、库存与累计自动策略

状态：源码与待执行用例已写，静态阅读；未运行tests、typecheck、构建、游戏、实际存档或SDK，不代表运行验证通过。遵从阶段集中测试限制，未使用TDD技能要求的执行步骤。

依据：正式V1第6节补给表；最新资产经济曲线未覆盖补给单价。纯净水1币/20/1实秒30游戏秒，泡面3/70/3秒120，瓶装饮料4/40/1秒30，快餐9/90/2秒60，奶茶7/60/1秒30，高档餐食15/100/1秒30。新增V2SupplyCatalog.ts/.meta。高级按最高已购地图1/1/2/2/3/4开放，回低级地图不关门，便宜品永久保留；没有把取消人物/车辆/地图购买资格扩大到补给。

休息保留：有活动批次10现实秒/恢复20/600游戏秒，无活动批次20现实秒恢复满、不推进订单钟。组合恢复拒绝活动订单使用无单休息，允许取消后完成已付出时间的原动作。满体力在扣款、扣库存前拒绝。补给启动一次消费，source、costCents、kind、elapsed、effect完整保存；恢复仅续动作不重复消费；取消不退已消费内容。

## 库存与领取边界

tripState.inventory和inventoryUsed为六种物品数量与累计使用量，初始全0；库存消费不调用经济扣款，使用相同效果和耗时。数量不引入背包格子、自动送入库存或购买囤货。恢复校验每种库存+累计消费等于已批准grant合计，负数/小数/多余键/重复grant或奖励键拒绝。

claimSupplyReward(grantId,rewardId)只接受固定批准表中已有奖励键，不接受客户端传种类/数量/金币。相同grantId和rewardId重试返回false；同grant换奖励拒绝；同奖励换grant也拒绝（一项任务奖励一次）。V2_SUPPLY_REWARDS当前为空，因此新档无任务赠品、没有任何可成功领取的事件，也没有现金任务奖励。未来实现任务时必须先有获批准的任务奖励表，并在可信任务完成路径校验完成条件后才调用；当前接口不宣称任务系统已实现。

## UI/Runtime契约

- V2GameSession.supplyOptions(): catalog各项加unlocked、quantity、actualRestore。
- supply(kind, source='purchase')，kind为water/noodles/drink/fastFood/milkTea/premiumMeal/rest，source为purchase/inventory。rest仅接受purchase输入，持久action.source标rest；消费库存持久source为inventory/costCents=0。
- configureAutoSupply({enabled,budgetCents,allowPaid?,useInventory?,kind?})。allowPaid/useInventory缺省false，旧kind仅兼容字段，按缺口自动择物不固定品种。关闭再开启、重配预算均保留spentCents，不允许预算低于历史已花。默认不付费、不消耗稀有库存；库存明确授权后优先库存，同source内依次按溢出少、有效恢复多、动作快、价格低选择可用物品；只在blocked且服务尚未确认时自动补给，预算或余额不足保留自动权益。
- tripState.batchAccounting: {orderIds,supplySpentCentsStart,inventoryUsedStart}|null。统一Trip.begin设置，手动/自动接批一致，最后交付/取消冻结end:{supplySpentCents,inventoryUsed}，finished/cancel保留到下一批。回执优先用end减基线，避免批后主动补给混入历史回执。批次供给现金为当前supplySpentCents减起始值，库存为inventoryUsed逐种差；不使用cash balance作为净赚基线，避免NPC并行收入混入。初始及旧版迁移为null，旧批次未知成本不能显示伪0。
- 游戏补给现金通过Dispatch.chargeSupply(cost,{supplyId,quantity:1})进入独立账目；库存无需扣金币。经济/Dispatch透传由ledger代理负责。

## 持久兼容

组合版本3 + Trip版本2；组合version2仅接受Trip1并迁移，老库存按不存在初始化0，旧pending动作按已购买/休息续进度，旧自动付费授权收紧为false，不静默扩大权限。组合version1仍只允许无在途订单安全初始化。未知未来版本或组合/Trip版本不配拒绝；原路线/交付一致性校验保留。未读写真实存档。

## 待执行验证

delivery-game/tests/v2-supply-inventory.test.cjs覆盖六项表值/锁定、满体力/无库存拒绝、未知奖励拒绝、自动授权/预算不重置、动作恢复/source篡改拒绝、测试专用批准表中的grant幂等与库存消费、批次基线。测试专用奖励表仅在测试局部替换导出并finally恢复，不向产品添加奖励。原v2-trip-rules.test.cjs显式付费自动用例补allowPaid:true。未执行；runner登记交PM统一处理。
