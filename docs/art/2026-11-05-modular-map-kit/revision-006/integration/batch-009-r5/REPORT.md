# 第五批v2：市场与住宅两个邻区的真实增量

从已发布146静态／466地面（含B12、B13、T05有限比较）继续，10新源/10模块/31面全部准入，0拒绝、0额外道具/面，当前156静态／497地面／81唯一源绑定。没有回放143/103/94快照；旧146对象全部字段/图框/位置/固定顺序与旧466面完整保持。B12源1731、B13源1383、T05仍原各1比较实例，未扩大准入；T04和其他hold未接入。

## 两张最终实际Cocos画面

- [市场邻区近景](cocos-r5-market.jpg) / [同一viewer入口](http://127.0.0.1:4186/revision-006/viewer/?view=r5-market)：第四批原B08市场与第五批260/261/262/264四个源址楼群、原道路和门前连接可辨。市场到新簇仍有约90～108m实际源址间隔，未擅自移动填密，不能称紧密商业街已完成。
- [住宅邻区近景](cocos-r5-housing.jpg) / [同一viewer入口](http://127.0.0.1:4186/revision-006/viewer/?view=r5-housing)：新U院1423、公共楼1363、坡顶1364/1738与已存在1739、邻近旧住宅行列同框。小庭院/前场与原路关系可辨；较外缘1359可见，1377未放入这张有限近景，节点实载不等于逐件视觉验收。没有为了塞10个同框而变成跨两区巨空远景。

两图均从实际Cocos运行页面取得后直接复制，未拼贴/重绘；embed=1仅隐藏预览工具条。第一次新地面bounds仅按选中polygon计算，在宽屏边缘出现旧邻楼缺部分地面；随后只将新r5镜头的地面引用bounds按实际1280×633视口候选2.1宽高比扩至有限范围，旧楼/旧地面不改，初始截图与读回保留iterations/。最终只交上面两张，不做逐楼矩阵。额外实际放大检查1423空腔，只保存数据读回和人工观察笔记，不另交第三张截图。

同一可编辑Tiled：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/integration/neighborhood.tmj`；新增一个r5 group，既有所有层/对象/tiles/组偏移/相对顺序逐值不动。旧life-street、rest、N1/N2/S1、郊区、宽U院、第四批及native-low/shop/shrub镜头字段保持。可选`?view=r5-housing-front`看新1359/1738与旧住宅前排，`?view=r5-1423`看部分内院；这些是同一场景有限镜头，不另工程。

## 固定输入、schema与原路适配

唯一消费第五批v2，父原SHA `f2d391dccd4efb32ea0d1868db8f53abbdecf8df3772f617f6bf79ba3a0bf5e1`。e9ec首版仅历史，未导入/回写。原31面数据不改；派生只补真实sourceNativeSHA256、实际筛选/基线/合同证据。父原SHA、派生SHA、基线SHA分开记录。

本批root是`scenes`，没有sourceMappings；明确保留为round5Scenes并以每件visualReplacementOf数组导出绑定，没有读旧单键失败后当空源。programme显式适配sceneProgramme，regionId/landUseIntent保留，场景用途不改原业务类型。源绑定统计兼容旧sourceIndex及sourceIndices数组：旧71包含1731/1383，新10无重复，当前81绑定/81源，绝不是156个业务地址。

6条输入原路全部已在当前场景引用。149396322-0旧B13桥接记录只含几何字段，v2多带kind/speed/roughness/bridge；独立对原city验证nodes/sourceNodeIds/width/direction/projection一致，保留旧road字典全部字段，不补写/覆盖；v2完整输入记录在round5InputRoadRecords单列。其他5条全记录相等。没有改业务速度、桥梁、导航或新路。当前95原路引用619完整节点，旧道路数组及顺序保持，仅视图绘制有限clip。

## 逐源准入与一次比例

|原sourceIndices|persistentId|资产|邻区|单次标量|实际world frame|设计接近关联node|
|---|---|---|---|---|---|---|
|[1359]|009r5-src-1359|B01|housing1735-1739|1|7.936234×9.940515|3387450109|
|[1738]|009r5-src-1738|B05|housing1735-1739|0.9|9.162777×10.486393|3387450109|
|[1423]|009r5-src-1423|B07|housing1735-1739|1|22.456608×22.964885|3387450109|
|[260]|009r5-src-0260|B06|market0587|0.9|13.419888×12.999245|6438106307|
|[262]|009r5-src-0262|B02|market0587|0.9|11.935356×14.291019|6438106307|
|[1363]|009r5-src-1363|B04|housing1735-1739|0.9|14.738865×13.839310|3387450109|
|[261]|009r5-src-0261|B01|market0587|1|7.936234×9.940515|6438106307|
|[264]|009r5-src-0264|B06|market0587|0.9|13.419888×12.999245|6438106307|
|[1364]|009r5-src-1364|B05|housing1735-1739|0.9|9.162777×10.486393|3387450109|
|[1377]|009r5-src-1377|B06|housing1735-1739|0.9|13.419888×12.999245|3387450109|

B01=2/B02=1/B04=1/B05=2/B06=3/B07=1，六种已准入楼型，无新PNG。全部worldSizeUnits已canonical×uniformScale一次，运行nodeScale1、anchorMap不再缩放；本批7件0.9、3件1，无新1.1，旧1.1实例全部保持。actual-10-ui-scale-node-frame-check.json逐件记录真实UI像素、world frame、nodeScale、坐标/index与Frame文件SHA，不能只核X/Y。PPU/anchorUV来自原校准不变，原门像素回投影entryMap误差<1e-8候选单位。

原source polygon/数组/sourceSHA/sourceDataChanged=false绑定保留，不将原始source停靠node强压为图门。两个原node关联是设计接近，不是原楼业务绑定的证据；没有改名称、经营类型、POI/node/路线、存档或新增导航边。原viewer未画source载体占位polygon，因此没有创建后删除占位楼，抑制原source显示对象数0；其他源对象未覆盖。

全部native副本与实际tool源SHA逐字节一致，sourceNativeSHA256已补入派生及运行元数据；原生、校准、运行PNG未改。整张PNG无平面旋转、镜像、非等比缩放。没有把B12/B13/T05混入本批楼型或给它们再加实例。

## U院v2的实际复核

1423仍用PPU43.283474381889086、原22.456607606×22.964884732图框/UV、8点凹U实体与4点void。真门11[704,609]、阶12[713,626]，未用旧[746,825]假门，也未用外框把中庭判实楼。

v2只新增12平方米partial-inner-court（实际浮点面积11.99999999994），四角都在真实空腔，距实体1.914308043m，与009r5-src-1423-walk-0相接；未导出v1 source-court/entrance-apron两面。实际放大Cocos画面中小方铺装接在院内窄步行面上，U内余地保持空白、路径接可见门阶，未见侧翼穿墙或大遮挡。U1423-actual-inspection-readback.json保留实际718.611×734.876 UI和22.4566×22.9649 world frame；manual-visual-notes.json明确是人工观察，未伪造API视觉结果。台阶高差、隐地脚与导航仍未验收。

## 最新基线与静态保护

prepare_fifth_009.py在真实146/466基础构造原地脚证据：旧103+第四40+B12/B13实际地脚+T05保守推断根包络，共146；不是只拿visible143/旧69绑定当全保护。新10楼和全部31面逐项核原其他source楼、蓝边、水polygon、全部492原waterway（3m候选半宽＋5m安全）、原道路、旧146地脚/旧466面（含life与新三件）、原POI及同批真实实体。只有本source carrier豁免，无全体障碍豁免或删楼/移旧物。10楼/31面均无冲突，最小值见clearance-summary.json：

- actual146Gap：2.897813
- actual466GroundGap：0.949879
- actualLife9FixtureGap：110.166308
- otherSourceGap：0.185026
- roadEdgeGap：0.030000
- waterPolygonGap：59.683971
- completeWaterwayCentrelineMinus3mGap：19.938860
- nearestOriginalPOINodeGap：50.467301

旧早期少数无近控制者仍用明确标记的保守billboard逆投影包络，不伪称精密地脚。新旧整图框没有交叠；新10按真实地脚深度静态排序，旧146的整数/小数editorRenderOrder及相对顺序全保持，不靠新sprite置顶遮旧。门槛小接触只记录本栋人工估线/原台阶，不扩展到他楼/车道/POI。

## 地面、资源和真实读回

新31面：原source-court/前场基底先、步行面后、原路最后。neutral-grass #a5b990显式用G13-r5-garden受控颜色，S01用原既有铺装；不是新原生草纹。原1.5m连接polygon逐值保留，U只放12平方米部分铺地，不填满void；没有额外三角凸包/道具/树/POI或连接成可行车道路。旧466面所有颜色/形状/字段/顺序全不动。

156静态＋D/影子共158项真实读回，所有坐标/UI/world frame/scale/index逐项核导出，最大浮点差约0.000001340投影像素。旧146实际UI尺寸与上一轮native-shrub读回逐项相同。重复file+SHA共用同一Frame，__mapTextureStats实读30 images、28 nativeFrames、2 canvasFrames（当前地面＋D影子）。

运行仍30张唯一PNG、2,425,880字节，全部长边<=280，新增PNG0字节；库34图是只读候选库，不混成运行统计。runtime-resource-statistics.json给每文件SHA/尺寸/字节，原生/25图/全城分析快照未入包。B13仍仅clean、T05仍1簇，旧素材准入状态不因本批改变。

|真实镜头|当前单块地面canvas|有限引用面/原路|单份RGBA候选字节|
|---|---|---|---|
|r5-market|2048×1817|21/5|14884864|
|r5-housing|2048×1817|40/5|14884864|

每个新镜头只激活一块<=2048地面，范围按局部实际视口候选拟合，市场约167×167m／住宅约197×197m；不是跨两区大canvas或全县常驻。完整原道路节点保留，选引用/clip只影响绘制，未测FPS/实际总内存；RGBA仅像素预算，不能当性能通过。

## 固定SHA与执行记录

- parentOriginalSHA256：`f2d391dccd4efb32ea0d1868db8f53abbdecf8df3772f617f6bf79ba3a0bf5e1`
- derivedSHA256：`fe8a96fc4214e7d9afb62be315e823a6e8bc07f23fa1ea8599aa45a585a31cad`
- baselineSceneSHA256：`64e00ad3a2d6654858233fe623d4fba1b81754bdc8b47f4d4676d6851ce51a5c`
- baselineTiledSHA256：`f46f851d6834ff3a2811de918c5db1194922620afd7e31f12d49138fd3b68bf4`
- finalSceneSHA256：`69ee3cb14645be306500d5db09a46a3eac4b5c75c8154eaacb586a90a23e6cc8`
- finalTiledSHA256：`861adb2bb3f5ca0b227e96496cc18b561ece6ec7f06a264b8e73938ad208dc21`
- sourceCitySHA256：`536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20`

690个只读保护文件SHA未变。当前新增10个tile实例、31面进入新group，既有所有Tiled层/tiles全字段保持，未init/替换scene快照。重复add_fifth_009.py实际拒绝，neighborhood_export.py export重复后scene/manifest/TMJ字节稳定；未来只导出现有手调图，不重apply。本次实际执行prepare_fifth_009.py、add_fifth_009.py、neighborhood_export.py export、capture_fifth_009.py两区域、verify_fifth_009.py，均只写006/integration、viewer和009/pipeline。

## 真实未解

场地仍疏、市场距新簇有明显空白，B02/B04前场大铺装仍缺用途细节，矩形绿边仍为色块且同族住宅重复；不以能放/节点数代替丰富度。两个近景验证代表邻区关系，1377等未被强行塞进照片，不能宣称10件逐一视觉验收或完整两个街区，更不是全县完成。B12/B13偏高候选墙高与T05推断根的上轮风险继续保留，没有借本批洗成正式准入。

无生图、新Agent、新工程/服务/端口操作、游戏tests/typecheck/回归/渲染矩阵/FPS、业务/UI/经济/存档改动或提交。未用户验收。
