# M1订单体验独立定向核验

日期：2026-10-30（Asia/Shanghai）。结论：11组独立断言通过，未发现本范围产品问题；不是用户体验验收。

## 执行与证据

- 实际命令：`node docs/reviews/m1-order-experience/fresh-audit.cjs > docs/reviews/m1-order-experience/fresh-audit.log 2>&1`
- 最终退出码：0；耗时约0.42秒；日志最终为 `RESULT 11 independent checks passed`。
- 审核者自写断言；仅复用 `map-hud.test.cjs` 首个test之前的fake引擎骨架，没有执行开发测试；补正fake Node.addChild为唯一父节点语义。
- 真实当前/before TypeScript通过transpileModule递归加载；before未收录的domain/GameConfig沿用现版（此轮无修改）。
- 使用81节点直线合成地图、新建内存OrderBook；未访问4181或其他浏览器页、用户存档和Storage。
- 所有写入限本目录fresh-audit.cjs/.log/.md；未改生产、开发测试或其他角色文件。

## 已验证

1. 三个固定种子：新旧生产模块生成的10候选去除新增元数据后逐字段相同；ID相同；RNG调用分别365/365/366次，新旧完全一致；首单direct，新来源按ID稳定。
2. 用before生产模块实际生成idle/routes/running/arrived/done快照，当前restore后整个序列化对象一致：旧source仍缺失，food、重量、候选、费用、期限、端点、routes、进度和结果均保留；restore均不调用RNG。
3. before的running快照由新旧实现继续到达，玩家及回执相同；完成快照恢复后重复settle无第二次记账，finish回idle。
4. direct/transfer × normal/urgent四种组合分别接取、运行中恢复、完成；来源与履约类型均保留，重复settle无第二次发奖。另实际生成的转单CC-6按ID接取、恢复及结算通过，不仅依赖人工设置source。
5. 初始全部10候选preview.deadlineSeconds与实际accept.deadlineSeconds一致；代表普通600秒、加急300秒。
6. candidate和active各拒绝9种非法可选字段：未知/null来源，0/小数/161/字符串份数，数字/null/301字符备注；旧food尾部3份可解析，无法解析、0份或小数不猜1且显示未提供；无需求不编备注。
7. 无单中央入口打开真实OrderPhone，关闭保持候选和刷新状态；有单入口只重开本单卡，无新大厅。
8. 卡X未调用cancel，完整序列化状态不变；车辆/地图/账单三弹窗在卡可见与收起两态往返及rebuildLayout，卡显隐、已接单、候选、选择保持。
9. 唯一“去取餐”实际按钮只调用一次depart；运行态无再次depart按钮；车辆弹窗可打开但点击按钮不升级；收卡/重开不重置进度。
10. 账单打开时update推进到arrived仍停留账单；关闭后可达交付弹窗；点击真实“按要求放门口”完成；点击回执真实X调用finish后idle，无底卡、modal或active残留，玩家奖励不重复。

## 源码与验证边界

- `.log` 的 `SOURCE_SHA256` 记录本次读取的当前模块、before模块与复用harness的SHA-256。
- 本次读取且列于final-source-sha.json的7项均与冻结SHA相符；仅核对本次输入，不替代固定测试最终全清单指纹收口。
- `MapSample.ts`：`fb58ca1b172f85d4ca49c3f4367106494bccab448bd0b21e32a350e80abfcf2e`
- `OrderBook.ts`：`f57bc0c7472ca0d0e00e536073447f497d51d367182999ffd249634a8d6d9570`
- `CountySnapshot.ts`：`2f451b6c7ea08338221aa016ae3164efb80755eb453eba5a546876db74cad7b7`
- `OrderPresentation.ts`：`541d11ec650364dfab41132a0dea9242ba6f5dca48113062b43274764ca38d86`
- before实际产物为schema3。本轮未另造schema1/2历史快照；合成图单路线，选路只验证index0保存及回调，不声称覆盖多路线几何切换；长线相机、手动拖动/定位和真图由PM及固定测试证据承担。
- fake引擎只证明模块状态/回调；不替代真实Cocos触摸、帧率、手感或用户操作验收；未加载或更新用户数据。
- 未重复222全回归、typecheck或build；仅读取verification.json：test总222退出0，typecheck退出0；构建wrapper退出0但保留child `code:null, signal:SIGTERM`诊断，不将其表述为无诊断构建。
- runner前两次退出1均为审核脚本问题：before缺少domain文件加载路径；误用不存在的answerDoor方法。均已改runner，后者改为点击真实交付按钮；最终全组退出0。没有为通过验证修改生产或测试。
