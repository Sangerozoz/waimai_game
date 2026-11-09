# 本批产品测试：当前证据与范围

2026-11-07，PM已接收[原B20～41补充收据](b/codex-handoff/final-supplement-receipt.json)，并恢复原4182/4196至已测`v2-loadmap-fix-1106`。[服务身份收据](pm-preview-admission-1107.json)记录每端入口及12个脚本的HTTP SHA与磁盘一致；本次没有新构建或新浏览器操作。

## 已有且保留的验证

- 纯V2隔离套件95/95，失败0、跳过0、exit0；[原最终日志](a/v2-suite-final-complete.log)是11-06运行证据，不是95条完整玩家路径，本次未重跑。
- 全产品typecheck exit0；[最终日志](typecheck-post-ui-fix.log)。原始122条、配置修正后1条和最终通过过程均保留。
- 资源适配13/13、内存存档适配15/15；受控网络/cc和内存存储不等于远程引擎或用户档验收。
- Cocos产物容量调用：原RED 4例3失败→修复GREEN 4/4。唯一修改为`Array.from(batchLoads.values())`，严格单位/容量校验保留；[原修复证据](planned-iterator-fix-receipt.json)。
- 原B真实UI完成`v2-road-268`：planned→travelling→pickup→service→ready→travelling→service→finished，手点取餐/继续，自动交付，100→120金币、已送0→1、批次清空。
- ready观察等待122,982ms期间位置和行程钟不变，不用此等待估计普通玩家操作时长。100ms投影115样本全部follow；单窗404个rAF间隔p95约16.7ms，不能称真机FPS。
- B33/34拖动关闭跟随、定位恢复；B36自然reload/继续保留120金币、已送1、位置/资产/follow。B35截图是加载画面，不单独证明恢复。
- B37～41在finished后真实水补给1金币，最终119；账单收入20/支出1/净赚19。水后未再reload，不声称119已通过重载。原自有headless session已closed，不接管或重造档。

原B根`report.md`和`test-results.json`是RED检查点；不覆盖原文，以补充收据说明后续事实。当前机器可读汇总为[test-results-current.json](test-results-current.json)。

## 数值与未通过项

整数格、新费用/属性与当前试玩已整束集成；旧kg已签合同保留。首10单买车/15单招NPC预算有领域证据，A现已完成[首轮合法策略模型](../../balance/2026-11-06-balance-round-01/a/report.md)。PM本次离线复核41条保存结果的资金、额度和36项输入，无新模型重跑；B独立只读复核进行中。

当前游戏供给模型的小队优先常规11.04分钟、慢操作21.58分钟配齐3NPC，这是明确点击等待假设。唯一旧车先借NPC会耗尽额度并被旧合同占车，尚未修复；候选C仅隔离对照、未批准；长期二八时间仍未验证。

U01整体性能、多单同店浏览器/30NPC/完整购买保位矩阵、真实SDK、远程五类图片与真机性能仍开放。U30万元近似仅展示规则held。未达到/测得98%，未全产品或用户验收。产品线不制作地图，不碰真实用户浏览器/进度、不清档/注资或伪造广告成功。
