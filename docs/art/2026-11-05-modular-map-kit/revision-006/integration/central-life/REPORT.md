# 中央街巷：住宅庭院＋商服休憩的实际整理

[完整街巷候选](http://127.0.0.1:4186/revision-006/viewer/?view=life-street) · [休憩细节](http://127.0.0.1:4186/revision-006/viewer/?view=life-detail)

本次处理593/610/612三个第三批地块，冻结94对象全部保留。593是带短院界和树的住宅小花园；610是连门路的灯箱、圆桌双凳休憩角；612是有支路连通的树下长椅庭院。没有每栋复制一套道具，未加菜畦/油罐、未新增楼或业务点。相同B01楼体保留，差异来自有限场地的用途、铺地与真实物件层次。

## 两张真实Cocos画面

- [较宽街巷](cocos-life-street.jpg)：三处新组织地块及既有邻楼/原路同框；住宅短围栏、两株树、商服角和树下长椅可见。
- [连门路的商服休憩细节](cocos-life-rest-detail.jpg)：原门、原1.5m步行面、短连接、灯箱、圆桌、两凳与独立短段可见。主路侧保留有限绿带，休憩角没有成为孤岛瓷砖。

这两张均由实际运行Cocos页面取图后直接复制，未拼贴/重绘。拍摄URL带`embed=1`仅隐藏预览工具条，楼/路/小物未裁掉或改位置。细节镜头自然裁到楼屋顶，较宽图保留该楼完整体量。只交这两张最终图，未跑逐物渲染矩阵。

## 具体调整与前态

可编辑Tiled：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/integration/neighborhood.tmj`；稳定设计数据life-layout.json SHA `f2458945a69d8348a4a8b1692a887bdbbcd2556ba0e01e99ff53eb0c3e62fa97`。pre-life-scene/TMJ/manifest保留94/260完整前态，与父visible94字节基线核对；life-layout-v1/v2记录实看修正前态。actual-ground-diff.json逐surface给前/后世界polygon、材质、Tiled对象、层ID/index及理由，不覆盖原规划/原生。

|调整surfaceId|材质变化|其他调整|
|---|---|---|
|009r3-src-0593-planted-edge-0|G09-r3-planted → G02-planting|材质/颜色|
|009r3-src-0593-planted-edge-1|G09-r3-planted → G02-planting|材质/颜色|
|009r3-src-0610-carrier-court-610|S01-paving → G10-r3-courtyard|形状＋底层顺序|
|009r3-src-0610-planted-edge-0|G09-r3-planted → G02-planting|材质/颜色|
|009r3-src-0610-planted-edge-1|G09-r3-planted → G02-planting|材质/颜色|
|009r3-src-0610-planted-edge-2|G09-r3-planted → G02-planting|材质/颜色|
|009r3-src-0612-carrier-court-612|S01-paving → G01-lawn|形状＋底层顺序|
|009r3-src-0612-planted-edge-0|G09-r3-planted → G02-planting|材质/颜色|
|009r3-src-0612-planted-edge-1|G09-r3-planted → G02-planting|材质/颜色|
|009r3-src-0612-planted-edge-2|G09-r3-planted → G02-planting|材质/颜色|

仅上述10面发生候选修改：2块无用途的大白砖载体底面改成有限草地，截短无用途的后侧条带、角点削斜；8个选中种植边改受控深绿。没有换蓝黄、没有声称新原生地面纹理。2草地放在自己的原walk-0前面绘制，保留原门路可见；其余未选第三批面、前164面逐字段保持。

实际第一轮发现草地在旧walk后绘制会遮住部分连接，已修正草地层次，**原3条1.5m门路坐标/宽度/对象字段都没有改**。610外摆初次只有窄角接触，另加短1.5m连接，使访问关系清楚，未改原车道或导航边。

新增5个面：

- life-central-593-private-lawn：沿593原载体缺口边界的有限草地，在原walk和种植边下。
- life-central-610-rest-terrace：削角的小型休憩铺地。
- life-central-610-rest-connector：与原walk同材质的短1.5m接近面。
- life-central-612-bench-pad：长椅小落脚面。
- life-central-612-garden-connector：从原门路接到椅旁的小支路（候选宽1.1m，视觉庭院地面，不生成导航）。

## 新物用途和实际接地

|persistentId|准入素材|局部用途|
|---|---|---|
|life-central-593-tree|T02|private garden|
|life-central-593-short-fence|P06|private garden|
|life-central-610-sign|P01|public commercial resting corner|
|life-central-610-table|P04-v2|public commercial resting corner|
|life-central-610-stool-a|P05|public commercial resting corner|
|life-central-610-stool-b|P05|public commercial resting corner|
|life-central-610-short-fence|P07|public commercial resting corner|
|life-central-612-bench|P03|quiet residential bench garden|
|life-central-612-tree|T02|quiet residential bench garden|

共9件，全部用原校准图框/PPU/UV和真实原生地脚/柱脚估点，正等比1，无旋转、镜像或拉长。P04只用v2中央柱版，两个P05是本P04同场桌凳语境，不改全局素材准入。P06/P07各只放一个独立原生短段，实际长度不同、不闭环、不称无缝标准套件。T02是原同族自然树变体，根部候选0.4单位框是人工根点保护盒，不冒充测绘树池或新树种。

life-layout中的每个物件给groundContactPolygonMap与staticCheck。9件地脚距旧94楼/物最小1.272候选单位、原1.5m门路最小0.664、其他原源楼最小2.293、未选地面最小2.265、原车道边最小4.800、原水polygon最小42.206、原POI节点最小29.476。只豁免其本地块对应的源载体，其他源/蓝边/水/原业务节点仍核；圆桌/凳/围栏互相地脚也留空。两株树的冠形遮挡已在较宽图实看，未遮住所选门，612树在长椅后绘制，椅面/腿可辨。

## 前后顺序与真实读回

原94对象的坐标、图框、全部block字段、固定editorRenderOrder和相对顺序保持。Tiled在原R3静态对象间增量插入新物，不重置/全scene替换旧对象；运行新物用80～83之间的fractional editor rank，位于593/610/612及其前后旧物之间。旧94原整数排序值不改，新树/家具不全置顶。详情final-verification.json与runtime-detail.json；动态D依原内存路线/原排序插入，不新增业务。

实读103静态节点＋D/影子共105项，节点坐标/尺寸/静态顺序核导出，最大位置浮点差约0.000001340投影像素。旧94实例的UI尺寸和运行资源别名也逐项相同。new-prop-frame-references.json逐件给实际file/Frame，P05/T02重复件及旧同图实例共用Frame。

运行仍27张唯一PNG、2,127,723字节，全长边<=280，新增PNG字节0；__mapTextureStats=27 images/25 nativeFrames/2 canvasFrames（本局部地面＋D影子）。仅实际引用派生图进viewer；原生母版/25图/全城分析快照未打包。当前只挂一块有限2048×1817地面，24面/3原路引用；没有FPS/内存实测结论。

## 保护与SHA

- 94基线scene：`51d53b3eebe803355770ddbd7f26fee5184f613d48f6a3e5efed9923fbcd8ebc`
- 94基线Tiled：`d4a604151166c3c5c787ca79690e58f54067a09be485ca2ddb1988f8c0438d0e`
- 当前scene：`31a33ff6d27d92f609d7c56ea15769ea51d967fd19fabd7dbf05cbb791335bbf`
- 当前Tiled：`9bb69f441c43bde7d1d766c59fdd715871fc0564073f5416c5fedbcebe01880d`
- 原city：`536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20`

640个只读源/原生/校准/旧证据文件SHA不变。旧94对象全字段/图框/排序值及相对顺序，前74/164地面，未选第三批所有面，旧镜头、D路径、source绑定/原路72条485完整节点、原水/POI均保持。源city及所有规划原文件未改；这只是局部地面艺术整理，不是source楼几何/导航变更。数据重导出字节稳定，重复apply拒绝；现有用户手调不会被init覆盖。

执行入口prepare_central_life.py（初始布局）、add_central_life.py（按最终life-layout增量）、neighborhood_export.py export（当前重复导出）。当前增量已存在，仅export；实际前/后差分与迭代数据保存在本目录，pipeline/applied-central-life.json指向最终记录。当前合计103/265仅作审计，不作为丰富度或验收指标。

## 可见未解

楼体仍有B01重复，草地/种植面仍是受控色块，尚无合格灌木/地被层；个别院落仍有留白。P04中央柱/底盘透视与其他原生软边残差保留，围栏是小短段，灯箱面未新增文字图案；较宽图的小凳较小，近景已核可见。原路与楼原生边仍有角差。当前仅三处场地形成不同用途的局部候选，没有宣称全县丰富完成或用户验收。

没有生成新图，没有游戏tests/typecheck/回归/渲染矩阵/FPS、存档、业务/经济/UI代码、提交或新服务/端口操作。
