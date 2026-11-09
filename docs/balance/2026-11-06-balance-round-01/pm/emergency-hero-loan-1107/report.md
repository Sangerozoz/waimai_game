# 受限应急借车交付（2026-11-07）

用户选择的受限应急借车已实现，经独立规格和代码质量复审、默认回归及定向界面验证，已更新原4182/4196试玩。主角可主动借用基础2格车，通过真实亲送补经营额度，保留并结清原NPC合同；实车释放后完成当前整批，再明确取回实车并归还应急车。实现与验证不改变金币、体力、永久车数量或旧签约价格。

本轮浏览器使用明确标注的 `packed-transport-terminal` 隔离输入。源码原终态在Creator包直接读取时因地图JSON字段顺序导致mapKey不同而被拒绝；该原始失败仍保留，不能将适配后的界面通过扩大为任意来源旧档跨包恢复通过。具体边界见下文。

[主试玩](https://sanger--4182.getbb.app/?v2=1) · [备用试玩](https://sanger--4196.getbb.app/?v2=1) · [主试玩next](https://sanger--4182.next.getbb.app/?v2=1)。地址由本线程 `bb connect expose` 实际读回，面向已有BB授权访问者；远程鉴权后的内容没有另行运行验证。

六份生产改动为Economy、Fleet、Dispatch、Game、Runtime和UI，新增三份测试。独立借用记录与明确合同来源保留归还后的历史报价；首次借用升级Economy/Fleet/Dispatch至3、Game至7，归还不降版。未借旧档保持原容器。应急车不进入真实车辆库存，NPC配置、升级及成长资产计数继续只使用实车。借还沿原唯一slot事务，完整候选验证且保存成功后才发布，写失败、writer/epoch/原文冲突保持原状态。

| 门禁 | 实际结果 | 证据 |
| --- | --- | --- |
| A领域初交 | 35/35＝新增17＋原防新增18 | [交回](domain/handoff-receipt.json) |
| 审查补测 | 32/32＝领域20＋Runtime12；新增自动完整路径与三个现金边界 | [补测交回](domain/review-followup/handoff-receipt.json) |
| 最终默认回归 | 145/145，exit0，767项运行输入无漂移 | [原始收据](default-regression-followup-receipt.json) |
| UI行为 | 11/11，真实render/导航/update，绘制端口替代 | [收据](ui-regression-receipt.json) |
| 完整typecheck | exit0；此后仅扩两份CJS测试，六生产源保持同SHA | [收据](typecheck-receipt.json) |
| B独立审查 | 后端Spec PASS、质量PASS；前轮Important/Minor关闭；UI复审亦PASS | [后端](backend-review-result.json) · [UI](ui/independent-review-followup-b.json) |
| Creator | exit36 / Finished，721输入无漂移，550输出文件、14JS | [构建](build-receipt.json) |
| 预览身份 | 每端index＋全部14JS均HTTP200且SHA与构建一致，共30项 | [部署](preview-deployment-receipt.json) |
| 交付完整性 | 原764项仅批准六源变化，其他758项不变；550输出、30HTTP项再核对通过 | [最终核验](final-verification.json) |

各测试集合有重叠，表中数量不能相加作独立玩家路径数量。UI11项是行为测试，实际渲染证据另存于浏览器目录。所有原始RED、失败诊断和成功日志保留；本轮补覆盖没有改生产源，也没有倒改源码制造RED。

实际Creator界面通过真实触屏完成：首页入口、借车确认及取消、领取、普通接单、选路线、沿路行驶、主动取餐、ready停留、重载继续、主动去配送、实际交付。第一次应急亲送只补60000ms，旧批最后一笔尚未结清，仍可继续亲送。第二次亲送后，原NPC两份合同按原due与报价各付一次，实车成为可取回；大厅阻止新应急批次。随后验证归还取消、明确归还并装回starter-1、归还后重载，以及使用实车新签并完成一笔普通配送。

隔离最终账目为现金10000分（100金币）、主角累计4单（含夹具原有1单）、NPC2单、永久车1辆、借用已归还。新增两笔应急亲送和一笔实车亲送各2000分，原两笔NPC合同各2000分；现金从夹具0到10000分全部由上述五次真实结算产生，无重复订单账目。唯一slot与epoch保留，未增加借车存档key。[流程收据](browser/receipt.json) · [最终画面](browser/20-final-ui-ledger-1.jpg) · [归还确认](browser/17-car-released-gate-2.jpg) · [隔离最终存档证据](browser/final-isolated-slot.json)。测试浏览器和内部4208服务均已关闭，用户真实浏览器与存档未访问。

自动路径由真实Runtime/Game/Route/Store测试另行覆盖：自动在途实际open重载，恢复自动后推进旧合同；实车释放时原主角批次保持并完整送完，归还前持续不签下一批，显式归还后用实车自动续批并实际完成。已有自动权益来自明确标注的隔离事件输入，不能记为线上广告SDK成功。现金兼容输入分别29999/30000/30001分，仅现金及账本opening守恒字段不同；不将这些合成边界称为额外自然终态。

运输适配保留了唯一自然终态的全部车辆、人物、资金、额度、合同、路线腿、进度与历史，只将 `/route/mapKey` 从源码顺序指纹换为打包资源顺序指纹。源码与Creator侧的原city、prepareCity全数据及筛选路由几何，按对象键排序后的三层SHA均一致，数组顺序不变；正常restore仍执行完整已签腿校验，未跳过validator。B独立递归差分确认唯一变化并核对一次初始化写入。原127.0.0.1隔离origin的失败slot在最后仍保持原字节SHA，适配副本只在另一个localhost隔离origin初始化一次。[适配回执](browser/transport-adaptation-receipt.json) · [几何与内存restore核对](browser/07-transport-validation-result.json) · [原失败slot最终未变](browser/21-preserve-original-origin-result.json)。

原自然终态的源码→Creator直接读取仍为 **BLOCKED**，没有新增生产mapKey迁移机制。本批未修改地图、路网、V2RouteSession或参数；此前已发布防新增包与本包的全部524份打包resources逐字节相同，[资源比较](packed-resource-compatibility.json)不代替任意来源旧档兼容承诺。

构建首次受沙箱环境影响SIGABRT、exit -6且无输出，原[失败收据](creator-build-attempt-01-receipt.json)保留；同冻结输入的受控重试经自动审批后成功，未调整全局权限。浏览器01漏既有v2入口开关、03原mapKey拒读、10脚本误写页面枚举名的失败全部保留，后续各自注明原因，没有覆盖失败或替换原origin进度。

本轮仅交付受限借车及相应预览。40用户项、9工程项、正式用户验收关闭0保持；U01整体性能、真机FPS、广告SDK、长期二八、数值候选C和整体98%未获本轮验收。原B20～41、前批防新增、长期150.076223分钟有界结果均保持原证据，不以本轮替代。A/B已停止本批编辑；会话原生权限字段未暴露，不虚报Default切换。
