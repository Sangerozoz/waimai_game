# FOOD-RISK-IMPLEMENT-B-1106：UI源码候选交回

**已实际改源码；未测试、未typecheck、未运行TS、未构建、未部署。等待A/B统一集成及独立复审，不自判PASS。**

唯一源码：`delivery-game/assets/scripts/map-sample/V2GameUI.ts`。

- before SHA-256：`8fd5df4ee2cc7ca85cecd9488eec7cdd89fc08c374e8580d6bdcbc0b8336cd9c`
- after SHA-256：`81f54afb7d835c996a7305bb6075c7a3577c25fe33d5d928196d6a3530f80263`
- [实际精确diff](candidate.diff) · [接口证据/新旧映射/静态边界/未执行cases](implementation.json)

该源为untracked，精确diff来自本轮SHA匹配后保存在内存的完整起始字节，不用空git diff充当证据。原提案位于`layout/food-risk-contract-1106/ui-proposal.json`（冻结合同第3行明确指向）；实施目录内同名提案不存在，已读原件而非复制或重写提案。

## 实际接线

- `V2GameUI.ts:28-41`统一展示解析。大厅候选读Game新增food；版本3严格own food→`parseV2FoodRisk`→`foodPresentationById`，类别与可信目录不一致即拒绝。没有重新hash新单，也没有未知菜名落首菜。
- `:536-543`只读一次既有t快照，按本批每个id找同id Trip订单，再将展示结果存入局部Map。本批/在途卡`:601-620`和ETA`:559-571`复用同一Map，不为每个方案重选食物或额外clone整份行程。
- Trip2只走保持原字节的旧hash菜名/图展示。标记“旧批”，并在本批摘要下明确“旧批规则 · 沿用原普通风险；菜名和图片仅为旧展示推测”；每单ETA也写旧批普通风险，绝不将当前目录fragility当旧单真实类别。
- 新规则品类仅按真实字段映射“脆弱/普通/耐放”。严格ID获取的当前规范name才进入原foodImage；原FoodImages、loader、裁切、manifest、图片不动。
- 结构parse与目录一致性只是UI防错，**不等于canonical orderId绑定验证**。候选/Trip数据来自Game已验证读模型，Game仍负责canonical匹配、版本配对与存档边界。结构合法但替换为另一订单食品的伪造合同须由A的Game拒绝，不能拿UI parse当安全凭证。

## 高度和可读边界（静态，非实屏验收）

- 被动标记72×34、字体20、文字区64宽，仅四种固定两字内容；不用SHRINK或极小字。大厅标记中心(-224,-45)，范围x[-260,-188]/y[-62,-28]，完全位于原146×128餐图槽。本批中心(-265,-13)，范围x[-301,-229]/y[-30,4]，位于原112方图槽。不新增点击处理，不改原餐图源或其他热区。
- 菜名仍紧跟真实o.weightKg，原大厅名称314/地址370宽、本批名称340/地址422宽均不变；报价、期限、取送条和状态原字节保留。卡高/步长仍大厅164/178、本批190/204，因标记在原图槽内而无需挤压正文。
- 每个路线方案现在3条元数据＋每单3条文本（身份/规则/估算）。单行规则字体20、宽660，textHeight为37，连同间距每单增加43。原height求和及累计Y自动包含所有行，未slice或限制首几单。
- Trip2公共说明按textHeight计算，当前文字高37，加12间距使legacyNoticeHeight=49；routeTop与ScrollView内容height同步加49。摘要下间隔12，到路线标题的逻辑框间隔13.8，不把说明塞回原118高摘要。
- 内容高`164+legacyNoticeHeight+routeHeight+batch.length*204+108`；orderTop由同一routeTop/routeHeight得到，末尾说明中心以下仍有84余量。`orders:trip`稳定key、508/-340视口和固定控制栏保持，两者逻辑间距8。

这些是源码框与既有textHeight估算，不是设备字体/长文本无截断或图上标记可读性的运行证明；真实排版仍待授权外观核对。

## 精确保留及边界

静态完整字节段比较：类体从@ccclass至食品helper前不变；原foodThumbnail不变；update至EOF不变；固定配送控制、选择路线按钮及禁用、原ETA取整/late/safe、金额重量地址、专送占位、大厅汇总与选择行为不变。覆盖已过审补给三分支及原图、其他页面/骑手held/万元规则、routeMotion/跟随/HUD/币图清理，未夹带G04或地图工作。

冻结合同、提案和本轮记录的只读公共依赖SHA无漂移。A同时修改FoodCatalog/Trip/Game，已只读核对新增精确导出；Trip SHA在本轮观察窗口变化，详见JSON。它们属于A的在途源码，**本交回不是A完成、可编译或集成构建凭证**；B没有向这些文件打补丁。

仅做静态源码/精确diff/SHA/设计单位算术；patch自动反馈per-file tsc skipped，不是编译通过。不执行tests/typecheck/TS/回归/Creator/浏览器/游戏/业务/真实或合成档，不commit/push、不派Agent/Codex，不改权限、不重做50图、不读加工地图。目录50项不代表50张新原生图片齐备。

JSON列出12项未来cases，全部not-run；包括候选→冻结一致、三类别、新旧版本、非法上下文与伪造canonical、全部路线行滚动、阶段状态、真实字体/图层和原补给/控制回归。本轮没有创建或运行这些游戏场景/档案。

**交回即释放源码及报告写lease并停止写入，由父PM恢复原Default；不继承本批Accept Edits。PM等A/B交回后统一独立审查与必要构建。未关闭反馈、未报告98%。**
