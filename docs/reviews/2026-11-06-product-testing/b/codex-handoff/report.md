# 开发B接续：已有真实测试证据最终补充收据

2026-11-07，开发B `thr_29f6fcihz6` → 新PM `thr_4xmqy6fzdm`，同 `env_e54zrbdgxt` / 同checkout。原始测试作者为旧B `thr_tviezvnwds`，不改其来源。本次仅离线审阅原始记录、查看截图、核SHA与算术；没有新增游戏测试、购买、接单、reload或浏览器接管。

**结论：可接收本次iterator窄修复后的B补充证据，交PM核正式试玩包身份。** 新包确实完成了原planned单、ready手动继续、自动交付、非零自然续档和水补给/账单闭环。U01整体性能、98%与全产品仍未验收。

结构化入口：[final-supplement-receipt.json](final-supplement-receipt.json)，包含要求的 `realPassCases`、`limits`、`source` / `buildHashes`、`normalSaveContinuity`、`goldenEvidenceFiles`、`remainingUserIssues`、`publishGateRecommendation`。其中9项为有重叠的范围内证据结论，并非9条完整独立玩家路径；40个稳定用户问题均保留，未直接关闭或改写全局清单。

| 原始证据 | 已核结果 | 范围 |
| --- | --- | --- |
| B20/21/22 | `v2-loadmap-fix-1106` 实际main已执行；原 `v2-road-268`、trip 1、100金币/已送0继续，planned路线/出发入口显示，合同2/2格 | 原单恢复；没有造档或重接单 |
| B23/24 | 315×851、DPR2的planned页可见；恢复390宽后仍planned、行程钟0 | 仅该页缩宽观察，不是全部315宽流程 |
| B25～31 | travelling→pickup→service→ready→travelling→service→finished；手动取餐/继续，自动交付；100→120金币、已送0→1、批次清空 | 一笔保护期安全普通单 |
| B28/29 | ready同位置 `[-2713.34,-590.39]`，行程钟同为156.7971326552058；观察差122,982ms；截图SHA相同 | 停等不是常规玩家操作时长 |
| B31/B32 | 115个投影样本、38个travelling；全部follow，偏移居中；active窗404个rAF间隔，p95≈16.7ms、max≈16.8ms、>50ms为0 | 100ms投影/采样窗，不能称真机FPS或每个GPU帧 |
| B33/34 | 真实拖动后follow=false，定位后follow=true；完成位置不变 | 完成后的手拖/定位 |
| B35/36 | 自然reload/继续后120金币、已送1、finished位置/行程/资产与follow保持 | B35图仍是Cocos加载画面；恢复画面和完整状态由B36证明 |
| B37～40 | 实际水购买100分，120→119金币，体力96.216→100；真实账项+2000/-100，收入20、支出1、净赚19，余额119 | 补给发生在finished后，是当日账单；没有伪记本批内支出 |
| B41/关闭收据 | 最后119金币、已送1、finished、批次空；该截点无记录异常/网络失败；原自有session已closed且读回一致 | 119是最后观测，水补给后未再做reload |

原始B记录均在上一层目录，时间为2026-11-06；B20为当日23:06（UTC+8），B41为23:29。本次整理日期不改写旧测试日期。旧 `report.md` / `test-results.json` 及 `red-checkpoint-*` 副本保持原文：它们是RED检查点，不代表B20～41未发生。旧 `actions-trace.json` 仍只有B01～19；补充结论来自逐个原始记录，三次出发/取餐/继续tap以B31/B32保存的actionMarks为据，不虚构其余输入轨迹。原修复收据中的 `sameTestCheckpointReplay=pending` 也已被B20～41的后续事实覆盖。

源文件 `V2GameUI.ts` SHA256为 `dd0054b6f15f1bca07c886217a8197796138a951223fb8bde935a23717bbe3c2`。唯一参数替换为 `loadSummary(Array.from(batchLoads.values()),capacity)`，精确逆替换得到原SHA `cea071606d173007ca8ce8acde05c74748e3243d2c4091390aedcdfcef550ed9`；`loadSummary` 与严格 `V2LoadRules` 没有放宽。后者SHA为 `447cd3183ec93c1e25a3cab09c680bd81050aadc77cd99e1ce5581b8b33f9644`。

已测构建为 `delivery-game/build/v2-loadmap-fix-1106`：`index.html` SHA `0b6a467549a2717bb49a0644ecb96c9db44b2e2e6d2ca0590ffccfcc8f165927`；实际main `assets/main/index.ab2ce.js` SHA `fbd0ca86721c9f67e50a94be4c6b3c5db3cf1f26f8f27ded8db9415ab2166a4d`。记录中的12个JS HTTP SHA与本次磁盘核对一致。原构建Finished/exit36及SIGTERM/版本诊断保留，不宣称环境全面健康。原产物回归RED 1/4→GREEN 4/4、独立窄复审PASS、A原始95/95日志已重新读回和核SHA，本次没有重跑这些测试。

视觉进展继续使用既有成果：本次还查看了B04/05、B06/09、B10/11、B12/13的原始画面，骑手排版、肖像、车辆独立场景/车型切换、既有地图卡与餐图都有实际证据。新包B22显示2格和路线入口，B40显示非零收入去币图。源码/已实施项不重置成待静态确认；万元近似取整U30单独held。旧包菜单截图与新包截图在JSON中分别标来源，不冒充全部菜单已重新渲染。

边界仍明确：VehicleTopView探针115次active=false，不能用该探针固定坐标证明车辆精灵可见；实际中心标记另有截图。B31的115与B32稍后152个motion计数是不同截点，不能累加当配送次数。未覆盖多单同店/30NPC、已招募NPC持续入账、购买/招募/升级后的完整保位矩阵、10车型/hover、完整引导、真实手机/远程分享。广告SDK未接，不伪造成功；地图制作完全不在本任务写集。原8张认可图及98%目标保留，当前不通过。

离线核验命令为：

```sh
python3 docs/reviews/2026-11-06-product-testing/b/codex-handoff/verify-existing-evidence.py
```

核验exit0：迁移保护清单224/224一致，原B顶层89文件保持，37张截图SHA一致，其中20张为B20～40；B20～41共22个JSON逐个读入。全部20张修复后截图已实际查看。可复核 [evidence-audit.json](evidence-audit.json) 与 [original-evidence-manifest.json](original-evidence-manifest.json)。离线脚本首次把B04/B05的JavaScript调试数组当JSON解析而exit1，已针对两条已知debug标签保留原文，结构化状态继续严格解析；该过程如实记在 [verification-history.json](verification-history.json)，不算新增游戏失败，也未改原始records。

发布建议只交PM：接收本补充后，现场核4182/4196服务root与实际执行main；若更新原试玩入口，使用上述已测修复包并读回index/main身份。最后已知4182/4196为旧tick-follow、4198为新修复，本次未探测或更新服务，不把候选写成已上线。后续新增游戏测试须PM具体指令后开新隔离上下文；原session已closed，不接管或重建其存档。本批报告写集已交回，临时编辑租约由PM恢复Default。
