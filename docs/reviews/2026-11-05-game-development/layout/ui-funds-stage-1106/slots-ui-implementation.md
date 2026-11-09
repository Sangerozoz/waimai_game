# Slots＋资金刷新UI：隔离实现交回

**已实现stage候选，未应用live；等待A+B联合规格/独立质量门禁。不是编译、运行或视觉PASS。**

## 恢复与双基线
- 恢复确认及最终源码：`7c9a6115e2758f2394cf6ecd6419942f1e202b61f22f471b9733cf6536f0a6c9`，`74012` bytes。本次恢复未回退/重做源码，没有新增源码补丁；完成剩余静态收口和交付物。
- d2资金起始：`d2da7f2a95d1c36bf49ffb39457e557d26312ef512784eaaa3e8a23dc298fcc3`。
- live前后：`9c9484b24bbd36ea25da10c0cbf6d8080dcd7e5d78a9195603dffeaf423617dc`，字节未变。
- A manifest：`fc850a1498894f70e77b3ff4e5b010c2b249d8b7a6f60adeaa1fb23e5db11c29`；A source.diff：`bb741b346e452a91c57e8cf0ff35038adf5af6ad33fab7a82eae716ecebf10d1`；十份A源码逐个匹配清单。
- `slots-ui.diff`：d2→最终稿增量，28 hunks，SHA `b711204337b72bf44194d6d2cdb8134cfb616f4932aa7087303717332a080f6b`。
- `slots-ui-live-full.diff`：live9c→最终稿完整逻辑替换，27 hunks，SHA `a5cd6fb729dcf522f37b1a1e3e4b7801babadd13947ad070c33b10a1776d9446`。
- 两份补丁都在内存逐hunk核对原行/上下文/行数并精确重建最终源码，未应用live。旧资金报告及补丁保留。

## 实际消费点
1. 48–68行：明确单位格式、严格signedOrderLoad。slots读真实load并对照terms；kg只读原weightKg，不取整、不补1格。capacity同样按version展示整数格或原kg。
2. 211–238行首页：活单用Runtime.deliveryEffects；下一批用nextBatchEffects；签约总占用来自真实订单。无车明确显示，不伪造容量。
3. 693–841行大厅/本批/在途/ETA：同id食品与占用复用。菜名后紧跟占用；chosen仍是原候选对象，保留load/sourceOfferId/food/端点传回。全部行与唯一出发/禁用保持，无分页、装箱预测或8/50持单上限。
4. 493–605行车辆实例/商店/升级：只用显式slot效果/quote，商店level1模板不调不存在拥有ID的Runtime getter；原所有权/旧批占车/主角busy限制保持。
5. 390–445行骑手：新hire.costCents；新slot效果和升级quote；培养增益由incomeFactor/baseIncomeFactor表达，未读取不存在trainingIncomeFactor。31双列的姓名紧邻Lv、肖像下状态、独立价格、纯招募与动态行高保持。
6. 7/70–76/608–623行：新profile配置与地图/车辆购买quote；首页沿旧目标metadata，但展示价格/差额全部来自新profile helper，不沿旧价格。
7. 197–208/317–329/541–580/864–867/883行：d2资金机制保留，确认层现金/报价变化原地刷新，旧按钮与重复提交/取消/销毁保护保持；不因每笔收入render整页，不自动执行业务。

## kg与食品版本是两条轴
- slots-v1＋Trip3：真实格子与冻结食品。
- kg-v1＋Trip3：原kg与真实冻结食品并存，不因kg退回旧菜图或普通类别。
- kg-v1＋Trip2：原kg；独立旧批食品提示与原hash展示推测，不把目录fragility当历史风险。
- 缺terms/load或跨单位失败，不默认1格、不静默降级。parse只是UI防错，完整可信身份/扣款/合同权威仍由A处理。

## 布局与读模型
餐名保持28/26字号，按textHeight增加局部标题/card/row step和累计contentHeight；取送地址、期限、报价、receipt随该增量下移。ETA沿原测高列出全部行。新增本批效果行的summaryGrowth同时进入summary/legacy/routeTop/内容高度。首页效果行底固定-295、向上增高，与原动作框顶部-301留6设计单位；实屏字形仍未检查。

render在setPaused后读一次snapshot并把state/数据传给页面。31卡只调纯helper，不逐卡Runtime克隆；HUD共用其一次snapshot。词法snapshot读点7→5、this.state读点18→6；render调用4→4、scheduleOnce2→2、normalCandidates2→2、quoteCandidates2→2。报价仍在用户触发render按有限候选（最多50）及所选批读取，不移入逐帧/资金刷新。不是实测性能结论。

## 静态证据与边界
`slots-ui-implementation.json`含逐项真实API来源、消费点迁移、新旧分支、所有输入SHA与S01–S15未运行用例。56个相对命名导出已按A覆盖束＋live解析，未发现缺名；未编译。food Trip2/3 parser、showUpgrade资金身份/提交机制、scroll helper、riderLine/Action/Identity、运动在HUD前路径等逐字保持。补给仅复用读到的state/snapshot与初始资金绑定，三种期限分支未改。

自动LSP缺模块/推断信息不代表编译失败或通过；未改配置/复制引擎/运行tsc。未找到所称计划md，未冒称已读；本交付按完整PM任务与实际A合同/定义核对。

未tests/typecheck/运行TS/App/Creator/浏览器/业务/真实或合成档/构建/部署/commit/push/Codex/子Agent；未改live/A/参数/地图/存档/资源/骑手样式或万近似/G04。PM须A+B作为一束独立审查并重核基线后统一应用构建，不能单发新writer或本UI。交回即停止写入，由PM恢复Default。
