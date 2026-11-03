# 结算背景订单卡生命周期修复

**已实现，未测试，待阶段集中测试。** 仅修改MapSample.ts呈现生命周期，保留整暂停按钮0.5、AU03、50餐品、取餐整按钮进度及所有M2/取消配送改动。未运行测试/typecheck/回归/渲染核验或独立复验，未操作用户游戏/存档，未commit/push。

根因：原renderPanel在done时仍创建DeliverySheet并绘制“配送完成/结算详情”底卡，然后在卡片构建过程中打开结算弹窗；openReceipt只创建遮罩/回执，没有移除底卡，重建也会重复创建。

本次renderPanel在发现active.mode=done时，处理正常结算触达后立即返回，不再创建DeliverySheet、完成信息行或结算详情按钮。统一removeDeliverySheet先removeFromParent再destroy已有卡节点，并清timer/tripLabel/progressFill/pickupServiceButton等节点引用，不靠加深遮罩或单纯active=false。save在done状态也先清卡，覆盖到达结算刚发生但提交失败的窗口；openReceipt在任何弹窗创建前再次清卡，pending或读档入口门禁也不会留下旧底卡。

resize/rebuild/主动到达最终都经renderPanel的done早返回；活动done读档继续入口下没有底卡，点击继续后仍展示保存回执。原地图视口/取景公式未扩大修改；本轮目标是移除卡片节点而不重排其他UI。

业务active/receipt没有在清卡时改变；仍由原finish+save处理结算X/遮罩，以及确认继续接单。ReceiptPresentation的触达去重继续只控制弹窗，不参与结算奖励。导航新增pendingSave守卫，避免finish变更已在内存完成、但快照尚未提交时因重建提前恢复底栏；保存成功后原重建路径恢复首页。原结算弹窗的BlockInputEvents继续拦截背景操作，pending提交及入口继续门禁保留。

交付命令npm run build:map --prefix delivery-game包装退出0，build.log记录2026-10-30 14:51:06 Finished，产物delivery-game/build/map-sample。4181静态index/主包HTTP200并与本构建SHA一致，见static-http.json；仅静态HTTP，不打开游戏。

before/、before-sha.json记录真实改前范围；production.patch为差异；final-source-sha.json、build-manifest.json及delivery.json记录最终指纹和构建结果。用户截图在reference/保留。本轮未通过截图或运行场景验证清卡、resize、读档和失败恢复，不能把代码实施/构建完成当成视觉或功能测试通过。
