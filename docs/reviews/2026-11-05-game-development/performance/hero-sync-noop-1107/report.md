# 配送性能：已消费亲送事件的同步空操作

本批减少一类已复现的重复事务：当全部亲送完成事件已补入经营额度时，Fleet先保留完整组合`validate()`，再跳过无变化同步的钱包事务。只有事件游标与真实事件数**精确相等**才走此分支；存在待消费事件仍走原完整原子事务。改动仅一份生产源码，不改30Hz、速度、计时、补额金额、存档版本、旧合同或Runtime保存后发布流程。

最终状态：窄测11/11、默认回归156/156、完整typecheck、独立规格与质量复审通过；Creator36/Finished，772构建输入无漂移。原4182/4196已更新`v2-hero-sync-validated-1107`，每端入口及全部14份JS共30项HTTP哈希一致；全部524份打包resources与上一应急借车包逐字节相同。[最终核验](final-verification.json)。

[主试玩](https://sanger--4182.getbb.app/?v2=1) · [备用试玩](https://sanger--4196.getbb.app/?v2=1) · [主试玩next](https://sanger--4182.next.getbb.app/?v2=1)。BB分享地址已实际读回；远程鉴权后的网页内容未另跑浏览器。

## 复现与修复

原同步函数无条件执行`atomic`。新增测试先在未改源码上运行，6项因“10次已消费事件同步仍序列化钱包10次”失败，2项非法恢复测试通过；原始[RED](red.log)和[收据](red-receipt.json)保留。第一候选只有相等早退，8/8通过，但独立复审发现公开`replaceFrom`及`Economy.enableSlots`会在事件数相等时形成混装版本，原校验不能跳过。

补充三条公开API拒绝用例在第一候选真实RED为8pass/3fail，失败均为缺少预期异常。最终在no-op分支保留完整`validate()`，GREEN11/11；有新事件仍执行原atomic。[补充RED](review-followup-red.log) · [最终GREEN](review-followup-green.log) · [收据](review-followup-green-receipt.json)。原候选、七项冻结文件、原测试/测量和未部署构建收据全部归档[review-01](review-01/frozen-archive.json)；最终[独立复审](independent-review-result.json)将Important/Minor全部关闭，未发现新问题。

kg与slots均覆盖空历史、已消费历史、真实恢复后的落后游标、后续新增事件及重复调用；每笔新事件仅补一次60000ms，现金与完整组合状态保持。越界游标、不一致完成数、双向钱包替换混装及未协调的直接Economy升级均被拒绝。序列化计数包装转发真实方法，不替换领域逻辑；无耗时阈值型单测。

## 同输入性能对照

[可重跑脚本](benchmark.cjs)分别在内存加载冻结before和实际after源码。现有长期模型终态为771笔亲送、884笔NPC成交；不重跑150分钟模型，不制造资金或更改存档。行驶态仅由同一终态经真实`pickup`、短tick、`continueTrip`导出，两版导出字节一致。原终态只读保留。

每个输入预热2对、记录8对，交替交换before/after运行顺序；每次均执行完整`restore → tick(1/30秒) → serialize → 完整restore`，然后逐字比较结果。四种输入共40对全等，其中8对预热、32对保留计时。偶数样本中位数取中间两个值的算术平均；第一轮上中位数数据保留为历史，以下均为最终候选的常规中位数。

| 输入 | before完整事务中位ms | after完整事务中位ms | 降幅 |
| --- | ---: | ---: | ---: |
| 空新档 | 0.328 | 0.278 | 15.37% |
| 长期终态取餐 | 166.569 | 146.029 | 12.33% |
| 同源导出行驶态 | 167.245 | 145.454 | 13.03% |
| 原signedZeroQuota终态 | 1.501 | 1.297 | 13.55% |

长期行驶样本的tick部分为100.086→78.905ms；完整事务仍高于33ms。以上是本机Node内存候选事务，未计真实存储提交、UI绘制、GPU或远程网络，**不是FPS提升，也不关闭U01**。[全部最终原始样本与指纹](benchmark-followup-result.json) · [执行收据](benchmark-followup-receipt.json)。

## 验证与交付门禁

| 门禁 | 本轮结果 | 证据 |
| --- | --- | --- |
| 新增领域窄测 | 11/11，exit0 | [收据](review-followup-green-receipt.json) |
| 默认V2回归 | 156/156，exit0；包含上述11项，不能相加 | [收据](validated-default-regression-receipt.json) |
| 完整typecheck | exit0 | [收据](validated-typecheck-receipt.json) |
| 输入完整性 | 772项捕获输入，仅Fleet和本任务新增测试的修订变化，其余770一致 | [核对](validated-input-integrity.json) |
| 独立审查 | Spec PASS、质量PASS，0项未关闭发现 | [最终结论](independent-review-result.json) |
| Creator | exit36/Finished，772输入无漂移，550输出/14JS | [收据](validated-build-receipt.json) |
| 原试玩两端 | 入口及全部14JS，各15项，共30项HTTP哈希通过 | [收据](preview-deployment-receipt.json) |
| 原打包resources | 524份逐字节一致 | [比较](packed-resource-compatibility.json) |

本批未重跑既有浏览器借还流程；默认回归仍覆盖既有Runtime自动借还测试。未打开浏览器、操作用户档或制作地图，上一批浏览器借车证据保持原包来源。原自然源码终态跨Creator包直接读取的mapKey差异仍BLOCKED，无迁移机制变化。U01整体、真机FPS、广告SDK、远程五类图片、长期二八、候选C及整体98%继续开放；40用户项/9工程项、正式关闭0保持。

主终端`restart`首次返回HTTP409，但已经创建替代终端，主端短时503、备用仍可用；[原失败](deployment-attempt-01-failure.json)保留。PM核对真实替代终端后恢复4182，再明确关闭/重建自己的4196服务。最终终端为4182=`term_x7yhrey8tc`、4196=`term_twhjpcyi28`；均完成最终HTTP核对，未将409假称成功或操作用户档。

生产before SHA256：`25bb29bbe67739022e1330865bf9c5a06557808c1e65fcc1f7bd4af07facc43e`；最终after：`2851ebfbe1eb89135161d896150a6d06f42f04ef1ba4d8aa563edca68a0949f8`。完整新增测试与精确差分绑定见[最终冻结请求](review-followup-request.json)。
