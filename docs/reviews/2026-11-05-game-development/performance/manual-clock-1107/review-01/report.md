# 受限手动时钟事务

本批评估从手动、双defer、无待广告回调和未消费亲送事件的时钟推进中，移除整档序列化/恢复。所有钱包、车队、奖励、Dispatch、版本、port与时钟门禁仍运行；只暂存并更新frame/rebase，后置异常回滚，其他路径保留原transact。

**当前候选尚未部署。** 窄测20/20、默认187/187和typecheck0已通过，Creator36/Finished、774输入无漂移；独立复审正在进行。PM自查发现options getter的可观察读取次数差异，冻结源保持不变并已通知B，须修订后重新绑定和核验。不能将本阶段当作最终交付。

## 证据与选择

前包`v2-owned-restore-1107`实际长历史事务约109ms，Dispatch每帧仍反复恢复整个历史。更广的共享草稿或历史验证缓存会触及多种经济/错误路径，本批只处理严格限域的手动时钟。设计与约束见[规格](../../../../superpowers/specs/2026-11-07-manual-clock-design.md)。

## 原始失败与测试

原源码上新增19项测试，RED为14pass/5fail，均因符合条件的手动时钟仍构造完整序列化草稿；其他语义/坏档/异常用例原本即通过。[原始RED](red.log)。实现后19/19通过，再补自定义arrival accessor必须继续走原事务，真实RED为19pass/1fail，限制普通自有函数属性后20/20。[port RED](port-boundary-red.log) · [GREEN](green.log)。

首轮编译误给Dispatch的check传了第二个错误文案参数，严格编译拒绝；已改为显式throw，失败日志留在`compile-attempt-01/`。它不是业务RED，也没有覆盖原始失败。

最终窄测覆盖kg/slots、前后台/暂停、回退、重复、实际restore时钟重基、自动/待广告/未消费补额的原路径、停止自动但保留权益、变更port、混合钱包、伪造历史、错误奖励/版本/rebase及后置失败回滚。默认187/187包含这20项，不能相加。[默认回归](default-regression-receipt.json) · [typecheck](typecheck-receipt.json)。

## 同输入对照与尚未关闭的发现

四类Game输入40次完整结果字节一致：空档、已有150分钟模型原终态、真实动作派生行驶态、唯一原软锁档。常规中位数约为长期取餐130.952→118.484ms（9.52%）、行驶130.600→117.994ms（9.65%）；这里只是Node内存候选事务，未含真实存储与绘制。31种直接Dispatch情形、85步比较结果、错误类型及完整状态字节一致，错误文案不在等价声明中。[全部数据](benchmark-result.json)。

PM追加公开参数探针发现：manual下原代码不读取`deferAuto` getter，当前候选的前置资格判断会读取一次；结果及状态字节相同仍不代表调用者观察完全相同。[探针](options-accessor-probe.cjs) · [已观察结果](options-accessor-probe-result.json)。冻结请求及B补充说明见[请求](review-request.json)、[说明](review-options-note.txt)。当前包保留未部署，后续通过真实RED/GREEN收口。

U01整体、真机FPS、原自然档跨包原字节恢复、广告SDK和98%验收均保持原未通过状态。未访问用户真实浏览器/存档，不改地图、路由、生产价格、速度或30Hz。
