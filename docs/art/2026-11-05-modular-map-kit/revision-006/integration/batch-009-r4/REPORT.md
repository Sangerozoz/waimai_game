# 第四批：八种楼型的真实源址候选已进入同一Cocos地图

本批40源址/40视觉模块和197地面已增量接入，无拒绝、无额外道具/补面。以已完成的life-street103物件/265面为基线，没有回放visible94。三个有用近景分别看U院真实内门/空腔、连拱顶市场前场和B05/B06住宅门路；关系图仅说明西北5候选与原路的相对位置，不把远处小点当完整街区。143静态节点均实际载入并读回，40不等于40处均逐件视觉验收。

## 可打开的同一viewer与实际画面

- [第四批西北局部关系](http://127.0.0.1:4186/revision-006/viewer/?view=r4-relations) / [真实截图](cocos-r4-relations.jpg)：5个新源址、原路关系；边缘仍可能看到既有场景局部。这是有限关系视图，不是全县或40源全景。
- [U院近景](http://127.0.0.1:4186/revision-006/viewer/?view=r4-0176) / [真实截图](cocos-r4-u-court.jpg)：院口、透明空腔、窄路径、真正门阶及原路同框。
- [市场近景](http://127.0.0.1:4186/revision-006/viewer/?view=r4-market) / [真实截图](cocos-r4-market.jpg)：B08曲面连拱顶、正面门阶、接肩步行面；未明显穿墙/压车行道。
- [住宅院落近景](http://127.0.0.1:4186/revision-006/viewer/?view=r4-residential) / [真实截图](cocos-r4-residential.jpg)：两B05坡顶与两B06错落体量；原路、门前窄路和有限院地可辨。

四张均为实际运行Cocos页面截图直接复制，未拼贴/生图。拍摄embed=1只隐藏预览工具条。较宽关系镜头居中修正的初始截图/读回保存在iterations/，没有覆盖旧批及life-street原截图。没有逐物截图矩阵。旧life-street/rest/N1/N2/S1/005/suburb/U院镜头全部字段保持；本批另有`?view=r4-XXXX`逐源有限镜头和`r4-tall-u`关系近景入口。

可编辑Tiled：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/integration/neighborhood.tmj`。新增一个第四批group，原所有层/组偏移/对象/图框/顺序字段与tilesets逐值一致；原nextobjectid/nextlayerid只向前追加。重放add_fourth_009.py会拒绝，不init、不重置。

## 数量与真实源绑定

当前143静态实例/462面；旧103/265完全保持，本批40/197。累计69个视觉替换映射、69唯一source index，所有sourceIndices/sourcePolygonsMap数组保留；没有把候选停靠关联变成经营地址或既存source楼-POI绑定。B01=9/B02=5/B03=2/B04=2/B05=8/B06=9/B07=3/B08=2。B03为窄高层、B04邻里公共前场、B08市场、B07 U院，未替换成住宅名称；B09/B10/B11/B12/B13/T04/T05均未加。

原source楼数据、原POI名称/node/经营类型/导航边、配送路线/业务/存档不改。原画面本来不画source载体多边形，因此没有创建后再删除占位层，实际抑制原source显示对象数0；其他源对象仍明确未覆盖。自身source carrier才豁免，其他原source楼/蓝边/水/旧场景/同批地脚均作为障碍。

下表面积比是native候选手估占地/source原地块面积，并非测绘等形重建；小于1明确表示楼＋原地块余地。铺地/草地有限，仍有未组织场地，不能由面积比声称整块已丰富完成。

|sourceIndices|persistentId|资产|正比例|候选用途|设计接近关联node|占地面积比|
|---|---|---|---|---|---|---|
|[694]|009r4-src-0694|B04|0.9|neighbourhood public forecourt|1623821046|0.511|
|[114]|009r4-src-0114|B07|1|U-shaped residential court|9657208284|0.621|
|[131]|009r4-src-0131|B03|0.9|vertical mixed office frontage|9657208284|0.256|
|[587]|009r4-src-0587|B08|0.9|covered market forecourt|9657208284|0.518|
|[212]|009r4-src-0212|B07|1|U-shaped residential court|1623821046|0.136|
|[73]|009r4-src-0073|B04|0.9|neighbourhood public forecourt|1623821046|0.185|
|[186]|009r4-src-0186|B08|0.9|covered market forecourt|1623821046|0.191|
|[1515]|009r4-src-1515|B03|0.9|vertical mixed office frontage|9657208284|0.042|
|[176]|009r4-src-0176|B07|1|U-shaped residential court|9657208284|0.670|
|[1411]|009r4-src-1411|B01|1|street shop forecourt|3387450109|0.226|
|[1739]|009r4-src-1739|B06|0.9|residential wing and courtyard|3387450109|0.293|
|[1737]|009r4-src-1737|B05|0.9|compact residential garden|3387450109|0.590|
|[391]|009r4-src-0391|B02|0.9|office/service forecourt|6438106307|0.243|
|[464]|009r4-src-0464|B01|1|street shop forecourt|3387477852|0.163|
|[1735]|009r4-src-1735|B06|0.9|residential wing and courtyard|3387450109|0.466|
|[571]|009r4-src-0571|B05|0.9|compact residential garden|6438106307|0.178|
|[1497]|009r4-src-1497|B02|0.9|office/service forecourt|1622902678|0.651|
|[1412]|009r4-src-1412|B01|1|street shop forecourt|3387450109|0.169|
|[1736]|009r4-src-1736|B05|0.9|compact residential garden|3387450109|0.413|
|[1513]|009r4-src-1513|B06|0.9|residential wing and courtyard|9657208284|0.550|
|[2377]|009r4-src-2377|B02|0.9|office/service forecourt|1622795593|0.296|
|[2238]|009r4-src-2238|B01|1|street shop forecourt|1626058763|0.236|
|[519]|009r4-src-0519|B06|0.9|residential wing and courtyard|3387477852|0.418|
|[596]|009r4-src-0596|B05|0.9|compact residential garden|6438106307|0.237|
|[1511]|009r4-src-1511|B02|0.9|office/service forecourt|9657208284|0.261|
|[518]|009r4-src-0518|B01|1|street shop forecourt|3387477852|0.351|
|[417]|009r4-src-0417|B05|0.9|compact residential garden|3387477852|0.353|
|[2239]|009r4-src-2239|B06|0.9|residential wing and courtyard|1626058763|0.874|
|[1355]|009r4-src-1355|B02|0.9|office/service forecourt|3387450109|0.168|
|[1399]|009r4-src-1399|B01|1|street shop forecourt|3387450109|0.082|
|[458]|009r4-src-0458|B05|1.1|compact residential garden|6438106307|0.254|
|[113]|009r4-src-0113|B06|0.9|residential wing and courtyard|3387450109|0.786|
|[389]|009r4-src-0389|B01|1|street shop forecourt|6438106307|0.121|
|[443]|009r4-src-0443|B06|0.9|residential wing and courtyard|12185944958|0.256|
|[572]|009r4-src-0572|B05|0.9|compact residential garden|6438106307|0.082|
|[445]|009r4-src-0445|B01|1|street shop forecourt|6438106307|0.283|
|[1729]|009r4-src-1729|B06|0.9|residential wing and courtyard|3387450109|0.236|
|[574]|009r4-src-0574|B05|0.9|compact residential garden|6438106307|0.246|
|[103]|009r4-src-0103|B01|1|street shop forecourt|3387450109|0.200|
|[1730]|009r4-src-1730|B06|0.9|residential wing and courtyard|3387450109|0.203|

## 一次比例、实际UI和真门

规划worldSizeUnits/anchorMap/footprint/entryMap已为最终世界值；uniformScale只记录canonical库的正标量。Tiled用最终图框，运行node scale全为1，未二乘成0.81/1.21；anchorUV/原生PPU不变。40件 actual-40-ui-scale-node-frame-check.json逐件给UI、世界图框、坐标、index、源SHA和file；实际投影32px/单位，最大坐标差约0.000001340px。

|实例|资产|单次标量|canonical图框|实际世界图框|真实UI像素|node scale|
|---|---|---|---|---|---|---|
|009r4-src-1739|B06|0.9|14.910986915×14.443605121|13.419888224×12.999244609|429.436423157×415.975827487|1/1|
|009r4-src-0176|B07|1|22.456607606×22.964884732|22.456607606×22.964884732|718.611443378×734.876311438|1/1|
|009r4-src-0458|B05|1.1|10.180863560×11.651547818|11.198949916×12.816702600|358.366397322×410.134483202|1/1|

原103的UI尺寸与node scale逐件等于life-street实际读回，原相对顺序和editorRenderOrder全保持。新40在Tiled按真实地脚投影深度排序；新旧原生整图框无交叠，未把新图置顶盖旧图；同批前后由静态index确定。运行preview145项含143静态＋D/影子；__mapPreviewOrder与UI/Frame全量读回分别保存在四份*-runtime.json，D内存路线仍原蓝内路径。

B07三件均用更正后的8点凹U实体与4点void，门11[704,609]、阶12[713,626]，未用旧假门[746,825]。PPU43.283474381889086、22.456607606×22.964884732图框/UV保持，门像素换算逐值核对；路径起点距可见门约0.489m，是门阶至路径的有限候选连接，控制点/台阶高差仍非导航验收。0176放大图中路径进入真实空腔，终点接可见内侧门阶，未看见横穿U侧翼。隐角4/8仍人工推断、2m保守候选预留，不称精密测绘。

本批B06/B08中心线路径与本栋人工脚线最大取样接触约0.06/0.12m；原控制不确定性约25px，市场/住宅放大图未见明显墙内穿行。own-door-approach-review.json逐件给中心线采样证据，只记录本栋估线接触，不扩展为其他楼/原车道/水/POI豁免，也不证明台阶可导航。40件原门像素从真实calibration换算，source停靠node保持单独元信息。

## 地面适配、保护与预算

新197面多边形/owner均来自冻结输入，未改形状。新增基底先、种植口袋后、原1.5m步行面最后，原路绘制覆盖全部地面；这样草地基底不会盖掉自己的门路。排序差分只发生新增group。neutral-grass的#9fb788/#a7bc92明确适配为G11/G12受控地面色；S01继续使用既有铺装，即使源字段另带color也不冒称新纹理。没有新纹理、假白盒、可行车捷径/导航边，未改变旧265面或life小物地脚。

逐件对实际103地脚/旧265面（含life9新物与15处新增/改地面）、其他原源楼、原水/车道/POI/蓝边/同批实体复核，无拒绝，最小值见clearance-summary.json。旧74中少数无更近控制者仍保守使用billboard逆投影包络，证据明确，不伪造精密脚线。所有40个真实native副本/tool来源SHA相同，源原生PPU/UV来自既有校准，sourceNativeSHA256已写派生buildings与runtime绑定，父输入不回写。

运行只含实际引用27张唯一PNG，总2,127,723字节，全长边<=280；新增PNG0字节。库验证打印31张是只读候选库，实际viewer包/运行Image读回均27。__mapTextureStats实际27 image、25 nativeFrame、2 canvasFrame（当前地面+D影子）；所有同file+SHA实例含0.9/1/1.1共用Frame，未按实例复制纹理。runtime-resource-statistics.json列每文件SHA/尺寸/字节。

|实际镜头|当前地面canvas|画面引用面/原路|单份RGBA理论字节|
|---|---|---|---|
|r4-relations|1536×1363|26/5|8374272|
|r4-u-court|1536×1363|6/1|8374272|
|r4-market|2048×1817|5/1|14884864|
|r4-residential|2048×1817|18/3|14884864|

新镜头每次只激活一个有限地面区域，近景边长<=2048、关系<=1536；逐源query也是按需引用，不常驻40块或全县巨图。完整原路节点数组仍在scene，绘制仅按有限bounds选引用/clip，不裁写源道路。理论RGBA不是实际总内存；未测FPS/内存，不能宣称性能通过。

## 固定SHA与复现

- parentOriginalSHA256：`51c783395231d246898f715141f74c31cc153ac795f7d7de1b602c69a0fe16d5`
- derivedSHA256：`f01e31ebf047bb7c716886d9d7451606fccd3f5672b9487ddbe7d3f037824516`
- baselineSceneSHA256：`31a33ff6d27d92f609d7c56ea15769ea51d967fd19fabd7dbf05cbb791335bbf`
- baselineTiledSHA256：`9bb69f441c43bde7d1d766c59fdd715871fc0564073f5416c5fedbcebe01880d`
- finalSceneSHA256：`9f7adf3e269fc320830b3b5b422797faed5014b453a99d199efd0c76d546bf8f`
- finalTiledSHA256：`1b730a98aec96741cd3ce0655b1085301ac2449819a876729aa8be4b03812585`
- sourceCitySHA256：`536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20`

652只读保护文件SHA不变。旧103所有block字段/坐标/世界图框/静态值/相对顺序、旧265面字段及顺序、所有旧镜头/地面region、source绑定、资产别名/PPU/UV、D路线均逐值保持。原94条引用道路606完整节点已逐条对原city顺序/坐标/宽/方向和projection核对；原city/水/POI全未写。

实际已执行：

```sh
python3 docs/art/2026-11-05-modular-map-kit/revision-006/integration/prepare_fourth_009.py
python3 docs/art/2026-11-05-modular-map-kit/revision-006/integration/add_fourth_009.py
python3 docs/art/2026-11-05-modular-map-kit/revision-006/integration/neighborhood_export.py export
python3 docs/art/2026-11-05-modular-map-kit/revision-006/integration/verify_fourth_009.py
```

前两步已有增量后拒绝再导入；后续保留用户手调，仅export。实际读回及截图用capture_fourth_009.py从已授权4186页面取得，未新建/暴露服务或探测端口。verify是本独立数据/实际节点审计，不跑游戏tests/typecheck/回归/渲染矩阵/FPS。重复导出scene/manifest/TMJ字节稳定，重复apply已实际被拒绝。

## 实看未解与阶段边界

U院内门/窄路、市场台阶、两种住宅门前均在近景可见，无明显墙体阻断；本批40全部数据准入、全部节点运行载入，只有这些代表区域实看，不能称40件逐一视觉验收。B03在关系图里较小，另有r4-0131/r4-1515与r4-tall-u可放大查看，未为凑矩阵再截40图。

本批场地仍很稀疏，种植边仍受控色块，公共/市场前场较空，住宅同款重复，未形成40个完整生活街区。U院隐地脚/台阶高差、B08曲面与深轴软边/暖玻璃、族图与个别原路夹角仍有残差。未新增树/道具来掩盖这些空白；已完成life-street整理保留。没有用户验收/全县覆盖/经营接线/车辆导航或性能完成结论。B12/B13待标定比较与其他hold素材本批不碰。
