# ORDER-LAYOUT 开发报告

生产已冻结，入口 freeze-ready.json；仅 CompactOrderInfo.ts 与 MapSample.ts 有本轮生产修改，before/和before-sha.json保存真实修改前基线。无提交、清理、存档操作或资源生成。

根因：presentationMetrics按CSS可读字号放大，金额列却固定210；320×480真实Cocos标签字号70，浏览器同字体测量¥19.84宽232.0459，超过列宽。red-font.log与green-font.log记录同视口前后：改后241宽，字号70不变。amountLayout用SampleUI相同字体测量，优先扩金额列，保留图88、间距24及菜名至少100；达到列宽预算才降低长金额字号，测量和绘制使用同一尺寸。long-font.log记录¥123456.78在388列宽、字号66实测375.665。未用禁止换行或裁切隐藏溢出。

结算标题独立在卡中心x=0、center对齐并保留对称宽度，右上关闭不变；所有结算正文center。其他弹窗保留既有位置。经济、格式、存档和流程代码未修改。

验证：npm test --prefix delivery-game、npm run typecheck --prefix delivery-game、npm run build:map --prefix delivery-game实际完成，串行包装退出0。tests.log为27+190+20+4=241通过；typecheck.log无错误；build.log在08:55:44 Finished，保留原始引擎诊断，不混称原始Cocos进程无异常。

新独立样板4193：复制最终构建，沿用经交接授权的Storage四API拦截及生产start/update/save截断，在创建CountySaveStore前替换为内存Book；不访问用户游戏。render-results.json、screenshots/覆盖720×1280、360×560、320×480、320×740安全区的大厅、当前卡、正常和带影响结算。浏览器脚本render.cjs/check-render.cjs与原始日志保留。引擎setItem('storage')探针被拦截并记录，不能称零访问。该开发矩阵不代替测试独立双入口/长备注/转单覆盖，也不代填用户手感验收。

final-source-sha.json、build-manifest.json为最终指纹。4181原端口无人监听，本轮为最新静态构建启动纯HTTP服务，仅请求静态文件；核对记录见4181-static-check.json。用户实际页面体验未操作、未验收。

## Revision 2：结算金额完整单行（本节取代上一版结算结论）

PM补充验收后确认：independent-extra及independent-after的结算收益整句换行可把小数拆开；第一版测试仅断言订单字段单行，未覆盖结算金额。revision2-red-receipt.json保存真实引擎失败记录，包括¥654.32被拆为“本单收益 ¥654.”/“32”。developer-art-discrepancy.md是补充要求前的范围判断，不能作为当前验收结论。

最小返修仅MapSample.openReceipt：收益标题与金额独立两行且均居中；金额使用实际字体测量，在inner-8宽度内逐级适配字号，货币格式与金额数值不变。订单卡生产代码没有二次修改。revision2-before/保存返修前代码；freeze-ready-v1.json、final-source-sha-v1.json、build-manifest-v1.json保存旧冻结。

旧结算截图及旧构建总SHA不再代表最终版，原始证据保留。当前唯一冻结为freeze-ready.json revision=2；独立测试需重新复制after构建。新构建08:59:17 Finished，完整241项回归/typecheck/构建串行包装退出0，日志revision2-tests/typecheck/build.log。4181静态index及主包与新构建逐字节SHA一致，revision2-4181-static-check.json。

开发新图和真实引擎行数分别在revision2-screenshots/、revision2-render-results.json及revision2-long-screenshots/、revision2-long-render-results.json；普通/长金额两套覆盖720×1280、360×560、320×480、320×740安全区、280×420安全区的大厅/当前/正常结算/影响结算。独立测试、美术和用户体验验收仍由PM收口。
