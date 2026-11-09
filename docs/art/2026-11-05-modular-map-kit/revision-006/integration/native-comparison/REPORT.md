# 三件新原生：低住宅／低街铺／灌木有限实景比较

从第四批真实143静态／462地面续接，新增B12、B13各1件及T05灌木1簇、有限地面4块，当前146／466。旧143全部block字段/图框/位置/相对顺序、旧462面与镜头/D路径/source/POI/nav保持。没有回退103/94，也没有重apply第四批。

## 两张实际Cocos交付图

- [低住宅与既有双层住宅对比](cocos-native-low.jpg) / [同一viewer](http://127.0.0.1:4186/revision-006/viewer/?view=native-low)：B12源1731与第四批B06源1730隔原路同框，单层低墙/大瓦顶与双层错落体量可辨；真实门阶接有限窄路与原路肩，未改原B06或道路。
- [灌木、乔木、长椅与门路的层次近景](cocos-native-shrub.jpg) / [同一viewer](http://127.0.0.1:4186/revision-006/viewer/?view=native-shrub)：T05在现612住宅小院中清楚可见，大小低于旧树，未藏楼后；原楼门/步行面/树/长椅及部分商业休憩角仍在。该细节镜头自然裁到旧楼屋顶，旧life-street全景保持。

只交上述一张有效低层建筑对比和一张灌木近景，均实际Cocos页面取图后直接复制，未生图/拼贴/扭曲。embed=1只隐藏原预览工具条。B13也已打开`?view=native-shop`实际观察：单层展示窗/玻璃门/外突台阶与长窄步道接原路肩可见；只保留native-shop-inspection-readback.json，不另交第三张比较图或逐物矩阵。没有把HTML载入当Cocos显示成功。

可编辑Tiled：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/integration/neighborhood.tmj`。当前主库asset-library.json／asset-calibration.json只追加3个新条目，所有既有条目逐值保持；本子集校准为[asset-calibration.json](asset-calibration.json)。这三件仍comparison-only，未准许批量铺场。

## 原件与控制点复核

B12/B13真实母版、运行图（B13用clean）和T05真实母版/运行图均已实际打开。native-provenance-check.json逐件记录实际tool绝对路径、母版/派生SHA与尺寸，tool原图字节等于native副本。所有原生/原runtime/provenance及原008/007/005证据只读。T04-v1/v2都hold，未接入/重生；B09/B10/B11及其他新物未加。

B13 clean实际SHA为`f97a525034c83998be5782fc21572e60ca937b05629a646db63e459d9892bb7c`，262×280画布与原件相同。独立逐RGBA复核1055改变像素恰等删除mask、原alpha均1、变后RGBA0，保留像素逐值一致。未重新裁边/缩放/平移。它沿原.runtime的sourceSize/cropBox/runtimeSize映射；原metadata没有先验PPU/anchor，本次用同一手估校准供原版和clean通用，clean不另设缩放或anchor，不称新款。仅clean进运行包，原生/原runtime永久保留。

B12可见直墙脚W1→W2=-25.403809°、W3→W1=+51.023993°；B13为-23.684674°/+52.920740°。按原native-control-points.json独立算角，端点约±3px，不拿数学小数当精密坐标。全宽基脚补充点/隐后角约±20px手估；隐角只作保守外轮廓，不称可见实测。屋顶R点没有混入地脚。

B12门槛取真实T1/T2中点[841.5,935.5]，外阶取S1/S2中点[877,1001.5]；B13为[601.5,1103.5]和[625,1151]。路径从真实外阶候选接原路肩，门没有移动到source停靠点或长边假中点；楼内台阶落差未证明可导航。

## 单一PPU、图框和体量残差

全宽基脚候选按B12 6.4×4.6／B13 6×5游戏米做单一正标量最小二乘，得到约6.563×4.348／6.341×4.544的实际候选体量，不非等比压平来命中矩形。整张PNG不平面旋转/镜像/拉斜。裁边worldSize=(crop宽高)/nativePPU，anchorUV=(原像素anchor-crop起点)/crop宽高；运行node scale1，PNG缩成280没有缩物体世界尺寸。

|资产|原生PPU|原anchorPixel|裁后anchorUV|候选worldSizeUnits|真实运行UI像素（32px/单位）|
|---|---|---|---|---|---|
|B12|106.223596038607|[624.0, 837.0]|[0.4959514170040486, 0.6697154471544715]|9.301134935×9.263478518|297.636317909×296.431312573|
|B13|117.950002987172|[631.5, 873.5]|[0.5062984496124031, 0.6897644927536232]|8.749469893×9.359898025|279.983036572×299.516736798|
|T05|316.376402893781|[660, 930]|[0.535175879396985, 0.8385964912280702]|2.515990424×1.801651434|80.511693562×57.652845892|

B12高瓦屋顶、B13较高的单层立面在实际大小下仍明显。粗估可见墙升分别230px/330px，按同一PPU约4.69m/6.06m，超过原候选低墙/3.6m设想；这个估点不是精密檐高，保留为体量风险，不能因此说普通小楼高度比例已通过。本次只准许小规模同场比较，不把墙压矮或再自动生图；新素材画笔厚度也比旧库明显。若后续判为过高，应回到原生/候选体量决策，而非图像各向异性修正。

T05不是缩小高树。三个低叶团顶面/叠层在运行中可辨；根原点确被叶簇挡住，只能推断[660,930]，候选±70原像素（约0.221单位），不是透明孔的实测根。单一PPU316.376402894来自候选1.8×1.2×0.9叶团投影总包络的宽高标量拟合，仅定合理游戏大小；没有用叶缘证明相机轴。保守接地/冠基包络用2.2×1.6候选，后脚未知，无绑土底/树池。

## 源址、场地和净空

B12仅source1731，anchor[-1659.4075,-833.76]；B13仅source1383，anchor[-1428.0200206705174,-668.4034155751125]。两者均使用各自真实用途合同，未强套旧预留/改名现楼，整体平移也为0；actual native地脚全部在原合同保守reservationPolygon内。B12地脚28.420候选平方米、原carrier162.820，明确为小楼＋原地块余地；B13地脚28.464、原carrier26.386，说明它并非原源footprint等形恢复，部分使用合同已留安全余地，但未压其他源或道路。

新增2块原carrier有限院地/铺装＋2条宽1.5m外阶到原路肩步行面，共4面，基底先画、窄路径后画、原路最后覆盖；旧462面没有颜色/形状/顺序修改。没有复用上次特定10面调整权限。原始sourceIndices/sourcePolygonsMap/sourceSHA与sourceDataChanged=false保留，新增2个装饰源绑定使累计71，不是新增2个经营地址。原画面没有source占位多边形，因此抑制原显示数0，没有创建后删除占位楼。

T05放现009r3-src-0612住宅院草坪[-1250.5,207.5]。第一次[-1245.8,207.6]碰长椅铺装而拒绝，第二次[-1250.5,208.1]超草坪拒绝，最终只动新灌木；全保守包络落在旧草坪内。距原143地脚/接地保护最小1.813、旧铺地2.268、原车道12.996候选单位，未占主门路/长椅支路/旧树根或商业桌凳。

三件/四面均重核蓝边、原source其他楼、旧143地脚与462面、原车道/POI、水polygon；还核了全部492原waterway折线，以3m候选半宽再留5m，最小安全剩余14.561m（B13步道）。complete-waterway-and-reservation-check.json给全量结果，不能用原usage静态旧快照代替。只自己的source载体豁免。T05支撑草坪是既有地面允许叠物，铺装路径没有豁免。

旧143整图框与新B12/B13没有遮挡；T05使用82.166666667的fractional editor rank，位于原612楼82与原树82.333/长椅82.667之间，未改旧rank或全置顶。实际近景中低灌木完整可见，树/椅/门未被盖。T05根部/叶缘有轻微贴地与细边残差，未把推断根宣称实测接地通过。

## 实际读回、资源与保护

native-low-runtime.json／native-shrub-runtime.json为真实__mapPreviewOrder、__mapUIDimensions、__mapFrameSharing、__mapTextureStats读回；新三件另列new-three-runtime-node-frame-check.json。146静态＋D/影子共148运行项，坐标/UI/world frame/scale/order全核，最大位置浮点差约0.000001340投影像素。旧143尺寸/位置/全部block字段/固定顺序与第四批实际读回一致；D路线/旧镜头、旧source绑定、原POI/业务/nav均不动。

运行30张唯一PNG，共2,425,880字节，新增3张298,157字节，全部长边<=280；B13用clean，原生/25图/全城分析快照不进包。所有同file+SHA引用共享image/Frame，实读30 images／28 nativeFrames／2 canvasFrames（当前地面＋D影子）。T05只放1簇，没有复制图档。候选库34 PNG与13楼型含hold库，不能当运行30图/10种实用楼型都已验收。

新镜头仍只激活一块有限地面：低住宅2048×1817、灌木1655×1468，B13单独比较2048×1817；保留完整源道路节点，只作视图裁切，不新增可行车路/导航边。当前95条原路引用619完整节点逐值对原city宽/方向/坐标/顺序/projection核对，旧94条保持。未做FPS/实际内存测量。

686个只读源/旧证据文件SHA未变。主asset-library/calibration两个容器有意追加，各既有条目及B01/T01的PPU/frame/anchor完整保持，不把容器SHA变化说成源变化。旧143对象、462地面、所有既有Tiled层/tiles、旧镜头、原city/source/水/POI/nav均保护。新3个tiles只追加，group offsets=0、正比例、可见/index可编辑；重apply拒绝，重导出字节稳定。

- baselineSceneSHA256：`9f7adf3e269fc320830b3b5b422797faed5014b453a99d199efd0c76d546bf8f`
- baselineTiledSHA256：`1b730a98aec96741cd3ce0655b1085301ac2449819a876729aa8be4b03812585`
- comparisonPlanSHA256：`8858320e4a7b15e1184a58d194e7b99b78fa6bf10477e5daf087297189ed2159`
- finalSceneSHA256：`64e00ad3a2d6654858233fe623d4fba1b81754bdc8b47f4d4676d6851ce51a5c`
- finalTiledSHA256：`f46f851d6834ff3a2811de918c5db1194922620afd7e31f12d49138fd3b68bf4`
- sourceCitySHA256：`536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20`

## 执行与阶段边界

已执行prepare_native_comparison.py → add_native_comparison.py → neighborhood_export.py export → verify_native_comparison.py。现在prepare/add拒绝重放，后续只export现有手调图。脚本只写006/integration、viewer和009/pipeline；未改规划/原生/其他工作线。全县仍未完成，普通场地大部仍空且色块式种植边未全面解决；没有因3件比较宣称生活层完整或用户验收。

没有新图、新Agent、新工程/服务/端口、游戏tests/typecheck/回归/渲染矩阵/FPS、存档、业务/UI/经济代码或提交。T04-v1/v2继续hold；B12/B13/T05只保留这次有限实例，不自动扩量。
