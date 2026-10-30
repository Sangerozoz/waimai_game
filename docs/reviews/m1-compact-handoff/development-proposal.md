# COMPACT-HANDOFF 已落实的版本与接口

依据最终spec与用户“取餐前免费取消”答复实施。48份before/SHA保留。

- 新接取活动升级schema4；handoff={version:1,phase:planning|toPickup|awaitPickup|picking|awaitDeliveryStart|toDropoff|arrived}，服务耗时沿pickupWaitElapsed保存，移动沿elapsed保存。ruleVersion仍表示原1/2经济时钟，mode供原外层集成。独立validateHandoff校验阶段、移动、服务一致性。
- 旧schema1/2/3先按历史规则校验，现有自动活动不加人工边界；无活动旧档下一次接单才进入schema4。所有未回答door到达按true执行，已done旧回答/回执不重算。schema4与地图catalog4分别管理。
- 取消只允许planning/toPickup/awaitPickup；开始picking起业务拒绝。候选内容/顺序/ID、钱/评价/XP/额度不变。路中保存road/from/to/fraction，下一路线origin前缀保存真实锚点/合法出口与部分距离时间，后续全是真实节点；方向、坐标、总计严格按地图复算，无虚拟地图节点。
- pickupPath统一用于预览、路线、候选排序/筛选/生成；单行只走合法出口。取消后原池不可达/超限订单保留并禁用，不让大厅整体抛错；刷新新单必须从实际锚点可达。
- 去店/2秒服务/待送均各自截断大dt，等待/服务不新增游戏分钟；动作按phase守卫，出发只抽一次餐损，结算唯一。
- 上层以接单尝试内orderId/phase去重；每次成功建立新接取立即清空旧提示键（包含相同ID重接），纯重建不清空。到店/待送/完成主动覆盖查看页；重载等待态呈现一次。后台不推进且恢复首帧丢弃补偿dt。
- pendingSave阻断后续动作和移动，保留同一确定结果并重试；保存错误持续可见，重试成功才放开关键呈现。不是跨会话原子CAS，不宣称完整M2并发安全。
- CompactOrderInfo共用测量/绘制；保持字号、压缩行距和重复标注。规划卡横排最多三条真实路线，普通含备注目标屏零滚动，长文本才回退滚动。规划展开收起灰站点/定位，收卡/行驶恢复。
- 结算引用同一纯报价；I0/I1/I2只读逐分分解，不创建对照钱包、不二次扣款；弹窗按真实内容求高。未来版本主档或备份无法恢复时写保护，原字节保留。
