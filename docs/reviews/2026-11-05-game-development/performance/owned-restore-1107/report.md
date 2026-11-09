# 恢复器私有JSON复制优化

本轮删除三个恢复器在`JSON.parse`后对私有对象图的重复复制。每次恢复仍独立解析输入字符串，完整原验证体、版本门禁、Fleet与钱包一致性比较、时钟和事务保存边界保持。公开state/snapshot继续深拷贝，两个独立恢复对象互不共享可变状态。生产仅三行赋值变化：Economy.snapshot、Fleet.value、Dispatch.orders/batchIds/frame。

交付状态：新增11/11、默认167/167、typecheck0；独立规格与代码质量复审PASS、0项缺陷；Creator36/Finished且773构建输入无漂移；实际候选包隔离配送及性能对照完成。原4182/4196均已更新`v2-owned-restore-1107`，入口及全部14JS共30项HTTP哈希一致。[最终核验](final-verification.json) · [独立复审](independent-review-result.json) · [部署](preview-deployment-receipt.json)。

[主试玩](https://sanger--4182.getbb.app/?v2=1) · [备用试玩](https://sanger--4196.getbb.app/?v2=1) · [主试玩next](https://sanger--4182.next.getbb.app/?v2=1)。分享URL已由BB实际读回；远程鉴权后内容未另跑浏览器。用户当前无法测试，本轮由PM自主完成隔离验证，不以等待用户测试阻塞开发。

## 来源与RED/GREEN

先在原试玩包`v2-hero-sync-validated-1107`重现了长历史卡顿，详见[实际运行诊断](../runtime-profile-1107/report.md)。取餐等待窗口约93%的时间在Runtime事务计算；存储提交约3ms/次，地图/UI消耗较少。

新测试先对未改的三源运行，RED为5pass/6fail，失败点为重复编码已私有解析的Economy、Fleet聚合和Dispatch历史。观察包装只转发真实JSON.stringify调用，不替换业务、不以耗时阈值断言。[原始RED](red.log) · [收据](red-receipt.json)。

只改三行赋值后，GREEN11/11。kg与slots均验证独立恢复、公开投影不污染内部权威；另测replaceFrom隔离/失败原子性、混装钱包拒绝和伪造已完成收入拒绝。默认167/167含这11项，数量不能相加。[GREEN](green.log) · [默认](default-regression-receipt.json) · [typecheck](typecheck-receipt.json)。

## 同输入模型对照

使用当前三源精确before和after在内存加载，完整执行`restore → tick → serialize → 完整restore`；四类输入共40次完整字符串比较一致，其中预热8对、保留32对计时。常规中位数取中间两值平均。输入为既有长期终态、真实Game动作导出的行驶态、空档、原唯一软锁终态；未重跑长期模型或修改原夹具。

| 输入 | before事务中位ms | after事务中位ms | 降幅 |
| --- | ---: | ---: | ---: |
| 空档 | 0.306 | 0.296 | 3.24% |
| 长期取餐 | 148.383 | 130.038 | 12.36% |
| 长期行驶 | 148.006 | 129.670 | 12.39% |
| 原软锁终态 | 1.278 | 1.216 | 4.86% |

这是本机Node内存事务，不是实际浏览器或FPS。[原始全部样本](benchmark-result.json) · [脚本](benchmark.cjs) · [收据](benchmark-receipt.json)。

## 实际候选包隔离对照

Creator候选`v2-owned-restore-1107`共550输出/14JS，773输入无漂移；524份打包resources与before包逐字节相同。[构建](build-receipt.json) · [资源核对](packed-resource-compatibility.json)。

新无头浏览器、390×844触屏模拟、同一长期模型原件、同一已知mapKey运输适配、每origin一次初始化后真实继续。打开时与before一样为主角771/NPC1197/现金2847832分/额度0；原1786565ms额度由Runtime正常离线结算，没有时钟编辑或注资。相同包装采样实际取餐、ready停留、主动继续及真实交付至772单。

| 采样窗口 | before单次事务平均ms | after平均ms | before rAF中位ms | after rAF中位ms |
| --- | ---: | ---: | ---: | ---: |
| 取餐等待 | 121.24 | 108.67 | 133.3 | 116.7 |
| ready等待 | 119.73 | 107.71 | 133.3 | 116.6 |
| 继续后的混合行程 | 122.39 | 109.74 | 133.3 | 116.7 |

单次事务平均耗时约降10.0%～10.4%；每窗采样次数不同，所以不能比较累计ms直接报降幅。混合行程包含点击前ready、行驶、交付和下一取餐点；before/after是一次有界顺序采样，暖机、调度和包装有开销，不是统计充分的FPS保证。每tag保留最多80个耗时样本，累计次数与总耗时覆盖全部已观测调用；原样本、位置和计数另存于[browser目录](browser/input-binding.json)。[结构化比较](browser-comparison-receipt.json)。

两包都真实完成771→772单、现金与账本加总一致、订单ID无重复、follow观察保持。Runtime lastError为空；各有一条尚未定位的资源404，不宣称零控制台错误。两次成功浏览器均已关闭，用户真实浏览器与存档未访问。采样后的正常NPC继续结算另留最终状态，不把它算进窗口收入。

**长历史仍明显不流畅。** after约109ms的事务成本仍远高于33ms，主要重复恢复与完整历史验证仍存在，U01保持开放。未改速度、时钟、30Hz、生产数值、地图、路由或唯一slot规则；原自然档跨包直接恢复仍BLOCKED，真机FPS、广告SDK、长期二八、候选C及整体98%仍未验收。

三个before文件及11份冻结文件均由B独立重建差分并核SHA；772项原输入中仅三份授权源变化，其他769不变，新增一份测试。最终构建、输出、HTTP身份与浏览器关闭状态又由PM核对，不将独立审查范围扩大为整产品验收。原before浏览器的工具失败与阶段日志保留，不重写成成功。
