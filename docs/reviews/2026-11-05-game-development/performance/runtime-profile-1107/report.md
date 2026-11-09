# 当前包长历史运行诊断

在全新无头Chrome中，用已有150分钟模型终态恢复当前`v2-hero-sync-validated-1107`包，已重现明显的长历史计算阻塞。主因在Runtime完整事务中的恢复、复制和验证；本次样本的存储提交、地图移动绘制耗时较少。此结论仅覆盖隔离的当前包，不代替真机FPS或U01整体验收。

## 输入与隔离

唯一输入来自已有`a/long-term-1107/run-01/end-state.json`：771笔亲送、884笔NPC成交、12名NPC。完整JSON原件SHA为`0aaec212918f92bb723a605d4db143108fd50bd39b2425f0b925ec2537052444`，未修改、未重跑长期模型。

源码与包的原city、prepareCity和筛选路由几何三层排序SHA一致。只在隔离副本将`/route/mapKey`适配为既有packed值，完整正常restore通过；无余额、合同、路线腿或时钟编辑。标签为`packed-transport-long-history-model`。[运输输入](transport-input-receipt.json)。原档跨包原字节恢复仍BLOCKED。

新浏览器先确认slot为空，经过无损gzip分段输送并校验解压SHA，再仅初始化一次slot，通过真实“继续游戏”打开。Runtime按原规则重基时钟并仅消耗已有1786565ms额度：打开时主角771单、NPC1197单、现金2847832分、额度0。这是原NPC合同自然结算，不是注资。

## 运行采样

最终成功采样为`capture-04/`。原始方法包装只转发调用，保留返回、异常和状态，采集嵌套耗时与self耗时；外部窗口计时、rAF和Long Task观察额外引入开销。公开UI执行到店取餐、ready等待及主动去配送，最终实际交付一单，主角771→772，下一取餐点仍正常停留，follow观测保持true。

| 窗口 | 时长ms | Runtime事务次数/累计ms | slot提交累计ms | UI update累计ms | rAF典型间隔 |
| --- | ---: | ---: | ---: | ---: | --- |
| 取餐点等待 | 3010.7 | 23 / 2788.6 | 85.1 | 26.5 | 约133.3ms |
| ready原地等待 | 2538.1 | 20 / 2394.7 | 63.7 | 24.9 | 约116.7～133.3ms |
| 主动继续后的混合行程 | 4848.9 | 36 / 4405.9 | 108.9 | 93.7 | 约133.3ms，最大300ms |

第三窗口包含点击前ready、行驶、交付及下一取餐点，不冒称纯行驶全窗。约93%的取餐等待窗口消耗在Runtime事务；同窗口Economy.restore self为769.5ms、Economy.state复制为350.5ms、Dispatch.validate self为527.7ms，不能把各嵌套累计耗时直接相加。

逐项包装样本、帧间隔、位置、follow及Long Task在[window-0](capture-04/window-0.json)、[window-1](capture-04/window-1.json)、[window-2](capture-04/window-2.json)、[window-3](capture-04/window-3.json)。每tag最多保留80个耗时样本，累计次数和总耗时覆盖所有已观测调用。[实际触屏动作](capture-04/12-service-travel-result.json) · [运行画面](capture-04/long-history-screen-1.jpg)。

最终检查现金3005822分与完整账本逐笔加总一致，ledger和settled订单ID均无重复，Runtime lastError为空。采样后继续等待产生的正常NPC结算已记录，不能把最终余额当作窗口结束时余额。控制台有一条资源404，未定位具体资源；不报零控制台错误。[最终状态](capture-04/final-state-result.json)。

## 工具失败与结论边界

首次入口尚未加载city，诊断直接get返回null；改为只读加载既有资源后成功。首次大脚本超过128000字符在执行前被拒；随后无损分段输入成功。capture-02/03导出过大的采样结果导致工具JSON截断并停止会话，原失败全部保留；没有把新会话写成原会话连续进度。capture-04改为小摘要及逐窗口导出，成功保存明细与画面并关闭浏览器。

诊断阶段772项输入均无漂移，未访问用户真实浏览器/存档，未改生产源码。[完整性](diagnosis-integrity.json)。本诊断后，三个恢复器的重复私有JSON复制作为下一项窄优化，另见[实现与验证目录](../owned-restore-1107/)；后续成果不得倒改此before证据。
