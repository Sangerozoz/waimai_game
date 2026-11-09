# B07宽院：同一地图小规模比较实交

2026-11-06。郊区三楼/菜畦/V02核心已先完成实拍回报，本次只在同一006/neighborhood.tmj追加B07宽院group。**现57静态实例、115地面**；原56实例及102地面保持。未init、重置、新建引擎、改原路或生成新图。

## 实际入口与证据

- U院整体：http://127.0.0.1:4186/revision-006/viewer/?view=ucourt — [真实截图](cocos-b07-ucourt.jpg)，院口、窄路径、门阶、原路同框。
- 内院门阶放大：http://127.0.0.1:4186/revision-006/viewer/?view=ucourt-door — [真实截图](cocos-b07-door.jpg)。图框只280像素，放大有软化，不称高清细节母版。
- 仍为原主入口006/viewer。郊区suburb/garden/market、旧rest/N1/N2/S1/005/overall及门槛镜头的cameraViews全部逐值保留；没有把核心与约70m外U院硬缩成一个远景。

## 本次新增

1个B07 sprite、13个父核准地面多边形，零其他楼/车/道具新增。地面为8个窄人行面/转角、院口外4m前场及4小块绿地；不导出reservation诊断底色，不铺整个U形透明中庭，不新增车行路/POI/导航边。新场是28×28候选宽院，距核心地块约70m；原路仍149665990-0同一完整14节点引用。

只更新未入场B07的006候选库校准：门11 `[704,609]`、阶12 `[713,626]`，两者按原像素/PPU换算后与固定扩展Map坐标差小于1e-8。旧`[746,825]`实读alpha=0，被标为rejected，未用于门/铺地。更新了U形真实轮廓、void、编号4/8隐角与可靠性，未复用旧普通矩形或假门。

原生PPU **43.283474381889086**、anchorPixel `[627.5,766]`、anchorUV `[0.4984567901234568,0.6237424547283702]`、图框worldSizeUnits **22.45660760557405×22.964884732449182**全部保持。未缩成小屋/非等比压图/旋转/镜像。11.808墙高是236px编号竖边纠正旧320px估点，未通过缩放把16强压成10。

## 实际路径检查与未通过事项

真实门阶放大图中铺地接到右内院可见门阶，路径位于空腔，未见明显大面积墙体遮挡、墙内穿行或门被其他物件盖住。左内院门不是本次选定连接口，未把玻璃/透明点擅当新入口。

用校准U形polygon重新投影并复算所有8个窄面，对occupiedU最小候选静态净距为**0.272394m**，与父规划相同。投影world U与校准LocalTN转换误差小于1e-8。可见点本身为人工估读，该数不是毫米级测量；0.272m不代表误差以外的通行净宽或导航验收。

void面积候选约84.52；全部13面在void内的裁切面积相加上界约18.14，约**21.46%**（转角重叠重复计入，为上界），剩余仍未满铺。绿色小块和窄人行面在实图可区分，没有一块不透明大院板冒充空腔。

编号4/8隐藏脚点仍为推断，2m预留polygon不是测绘物理足迹；台阶高差、最后门槛、不可见背面、精密地脚/导航均未通过。本次仅允许宽场地局部同场比较，未用户验收/全县完成。B09/B10/B11保持hold，未因本楼可比较而放行。

## 画布、节点与包

新增b07wide008独立有限地面画布**2486×2205**；原legacy006/suburb008两块画布bounds、85/17面和各自3/23路引用保持，不跨两场70m间隔烘图。三块地面均在sprite下方，SiblingIndex地面偏移自动按3处理，不遮旧物件。

实际__mapTextureStats：uniqueAssetImages=27、nativeFramesCreated=25、canvasFramesCreated=4（三地面＋骑手阴影）；57静态＋D骑手＋阴影＝59读回节点。editorOrder与导出对应，原56相对顺序/位置保持，最大坐标差1.34e-06引擎单位（投影常数舍入，核对容差1e-4）。D骑手原路径、原车/树/旧门位/通道未变。

最终**27张唯一PNG均长边≤280，共2,127,723 bytes**；viewer56文件、5,836,356 bytes（含引擎）。本次只新增B07运行派生PNG91,452 bytes，未包原生/25图/source-context全城快照。按file+SHA共享image/Frame，不每实例建纹理。道路仍25条/178完整节点，未重复添加同一路或裁改源节点。

## 文件、SHA与保护

Tiled：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/integration/neighborhood.tmj`。增量脚本add_b07_wide.py已有门禁文件即拒绝重入；正常手调后只运行neighborhood_export.py export。pre-b07-neighborhood.tmj/scene/library/calibration/export-report保留此前基线，旧截图文件未覆盖。

- 固定父扩展：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-008/planning/b07-extension/b07-extension-plan.json`，SHA `5e5c40725da225cb5fa45c129c0ab04951f76a9f562d519911f8acc44922fa76`。
- 固定新校准：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-008/calibration/footprint-review.json`，SHA `feab3dcbbcbd10e93fe0430af51383b2a981016c29a846485770f558b6626e75`。
- 核心next-district-plan.json SHA仍`a5412d65a4a9149051f98f43026b8d9e00d4b2e111d3c9366b998a2e4f230758`。
- 派生b07-runtime-subset-plan.json SHA `83c190f3121ccd63bcc78e0a822dab58714a3f1aeaa6c9950c6ec4d7f40657f7`，单独记录规则/引用，未冒充父原SHA。
- b07-source-protection-before/result.json核对**457项只读源SHA保持**；原city/005/007/008 planning-calibration/原生不写。原56Tiled对象字段逐项相同，原102地面逐值相同，旧镜头参数一致。
- 原生副本与实际tool源SHA再次相等。运行实拍/节点/Frame/画布读回在browser-b07-ucourt.json、runtime-b07-readback.json，终核见export-report.json、verify_b07_delivery.py。

仅执行授权的静态像素/多边形换算、独立地图外观与节点Frame核对；未游戏tests/typecheck/回归/渲染矩阵、存档/业务/提交推送，未启动/杀服务器或暴露/探测端口。实际显示不替代用户或导航验收。
