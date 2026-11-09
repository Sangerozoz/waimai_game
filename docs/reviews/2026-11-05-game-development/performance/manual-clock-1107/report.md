# 手动时钟性能增量

本批已修复options getter兼容问题；独立Spec/代码质量复审PASS（Critical/Important/Minor均0），默认回归、同输入对照、最终候选构建及隔离浏览器检查通过。**4182与4196现已更新`v2-manual-clock-final-1107`，首页及全部14JS每端15项，共30项HTTP哈希一致。** 用户当前无需操作，PM继续处理U01。

同checkout：`/Users/sanger/Documents/ChatGPT/taptap 2`。生产改动仅Economy、Fleet、Dispatch三源；Runtime、Game、Route、Store、地图、价格、速度及30Hz保持。应急借车与旧合同历史验证继续由默认回归覆盖。

## 改动与失败修复

仅在两个defer参数均为自有普通数据属性true、manual、无待广告、亲送事件cursor精确同步、arrival为自有普通函数属性时，时钟推进省去Dispatch整档序列化/恢复。完整钱包、车队、钱包组合、奖励、Dispatch、版本、port、rebase及前后置校验保留；失败回滚frame/rebase，其余输入保留原transact正文。

原19项RED为14pass/5fail，失败均为额外编码草稿。后续port accessor RED为19pass/1fail。PM探针和B首审又确认options getter新增读取0→1，结果/状态相同不足以证明兼容；首审BLOCKED及完整冻结材料保留在[review-01](review-01/review-result.json)，首个已构建候选未部署。

在首审三源不变时追加5项真实RED，20pass/5fail；改用属性描述符后25/25。覆盖getter读取次数、deferAuto抛错与经济命令重入、deferFleet抛错的原事务与原子拒绝、继承参数回退。首次TS2554编译失败另存，不算业务RED。

最终默认**192/192、无跳过**，其中已包含窄测25项，不能相加；完整typecheck exit0。[RED](options-boundary-red-receipt.json) · [GREEN](options-boundary-green-receipt.json) · [默认回归](final-default-regression-receipt.json) · [typecheck](final-typecheck-receipt.json)。

## 结果一致性与模型计时

四类已有Game输入：空档、150分钟模型取餐态、经真实Game/Route动作派生的行驶态、原signedZeroQuota。40次完整输出字符串一致，其中8次预热，保留32对计时。另有41种直接Dispatch兼容/损坏边界、95步，比较结果、错误类型及完整状态字节；options读取次数也纳入结果。错误文案不是该等价声明的一部分；广告权益来自明确的隔离领域事件，不代表SDK成功。

常规中位数（偶数样本取中间两数平均）：长期取餐132.613→119.581ms（下降9.83%），行驶132.985→120.159ms（9.64%）。这些是Node内存完整restore/tick/serialize/restore事务，不是实际FPS。[完整数据](final-benchmark-result.json) · [冻结复审请求](review-02-request.json)。

## 最终包与实际浏览器

独立包`v2-manual-clock-final-1107`：Creator36/Finished，774输入无漂移，550产物/14JS，524份打包resources与前包逐字节一致。原773输入只允许三源变化，其余770一致，加一份新测试进入构建输入。[构建](final-build-receipt.json) · [资源身份](final-resource-identity.json)。

全新headless浏览器与独立临时origin，复用原150分钟模型；输入只调整`/route/mapKey`以适配打包运输，原city、prepareCity、路由几何三层SHA相同。原源快照无改，单slot仅初始化一次，随后点击真实“继续游戏”。**该输入持续标注packed-transport-long-history-model，原自然档跨包原字节恢复仍BLOCKED。** [输入绑定](browser/input-binding.json)。

使用与前包相同的转发式轻量观测和窗口：

| 窗口 | 前包事务均值 | 本包事务均值 | rAF中位数（前→后） |
|---|---:|---:|---:|
| 等待取餐 | 108.669ms | 98.829ms | 116.7→100.1ms |
| ready停留 | 107.714ms | 99.633ms | 116.6→100.1ms |
| 真实配送及续批 | 109.743ms | 100.950ms | 116.7→100.1ms |

这是同输入的先后有界观测，包含观测开销，不是物理设备FPS或统计性能保证。取餐28次Runtime事务仅28次Dispatch事务/84次恢复；前包26次对应52/104，移除的重复草稿已在实际包生效。

真实动作经过ready→travelling→service→下一pickup，亲送771→772、跟随开启。结束时现金2,876,217分，与账本逐笔复算一致，ledger及settled身份唯一；slot等于最后已发布字节，当前slot完整restore成功，无Runtime错误及观测到的领域异常。后续NPC付款属于正常时间推进，不能用截图晚些余额反推窗口收入。

浏览器仍观察到1条未定位资源404，与前次相同；不能称控制台零错误。实际截图已检查，浏览器及临时服务器均已关闭。[全部窗口和对照](browser/comparison.json) · [截图](browser/screen-1.jpg) · [关闭回执](browser/close-result.json)。

## 独立复审与试玩身份

复审B独立重建完整/增量差分，确认20/20冻结文件、3/3原始源码及14/14首审归档匹配，原事务体逐字未变，options Important关闭。复审仅读取源码与已有证据；最终包、浏览器和HTTP由PM分别执行，范围不混用。[复审结论](review-02-result.json) · [原始输出](review-02-output.json)。

原两端口仅切换本PM拥有的预览服务，保留旧构建；新终端为4182 `term_chbxhghr82`、4196 `term_fwr4du4xp4`，与最终构建逐项核验。运行入口：[4182](https://sanger--4182.getbb.app/?v2=1)、[4196](https://sanger--4196.getbb.app/?v2=1)；next入口：[4182](https://sanger--4182.next.getbb.app/?v2=1)、[4196](https://sanger--4196.next.getbb.app/?v2=1)。[部署收据](deployment-receipt.json)。

BB分享链接按插件说明仅供持有owner getbb.app会话的访问者使用。补充的未登录HTTP请求两端均返回403 Forbidden，因此未声称远程响应哈希核验成功；未借用用户会话或改账号/访问设置。本机30项包身份已核，分享URL由bb真实返回。[原始远程结果](public-http-check.json)。

## 接续边界

当前事务仍约99–101ms，显著高于30Hz的33ms预算，U01继续开放。下一步依据实际热点减少重复历史验证和状态复制，须保留唯一slot、保存后发布、拒读坏档与旧合同兼容。真机FPS、原自然档跨包恢复、广告SDK、长期二八、候选C与整体98%均保持未验收。用户当前无法测试，由PM继续自主隔离验证；本轮没有访问用户真实浏览器/存档。
