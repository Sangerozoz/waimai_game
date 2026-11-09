# 当前补充：B07宽院已加入局部比较

在既有56实例/102地面基础上追加1栋B07和13个核准地面，现57静态实例/115地面。[U院真实截图](cocos-b07-ucourt.jpg) · [门阶放大](cocos-b07-door.jpg) · [本轮报告](REPORT-B07-wide.md)。PPU/UV/图框不变；门11/阶12已更正，隐藏角及高差/导航仍待审。27张唯一≤280 PNG，共2,127,723 bytes；下文56/43等为此前阶段历史，最新统计见export-report.json。

# 当前补充：008郊区核心已接入同一地图

原43实例/85地面保持，追加13实例/17地面，现56静态实例/102地面；两个区域独立有限地面画布。[郊区实拍](cocos-008-overall.jpg) · [住宅菜园](cocos-008-garden.jpg) · [市场后勤](cocos-008-market.jpg) · [完整报告](REPORT-008-suburb.md)。当前26张唯一≤280 PNG，2,036,271 bytes；下文43/39/36阶段为历史，最新统计见export-report.json。

# 当前补充：休憩角已接上步道

2026-11-06在原39实例上新增圆桌v2、两凳及独立短围栏，当前43静态实例、85地面；新增1.2m×约7.5m人行连接铺装，原楼/树/车/原路与1.5m通道不动。[真实近景](cocos-rest-near.jpg) · [本轮报告](REPORT-rest-corner.md)。当前22张唯一≤280 PNG，共1,744,658 bytes；以下39/36实例条目为此前阶段历史，最新统计见export-report.json。

# 当前补充：生活细节已显示

2026-11-06新增P01灯箱、P03长椅、P10双桶各1实例；[真实细节截图](cocos-life-props.jpg)、[增量报告与校准/读回](REPORT-life-props.md)。当前39静态实例、84地面、19张唯一≤280 PNG（1,548,577 bytes）；P05留库，P04继续hold。基础街段原截图/基线保留，下文36实例/16图为细节添加前的交付记录，当前统计以增量报告及export-report.json为准。

# 006实际接入交付：005原样板＋N1/N2/S1有效子集

2026-11-06。已运行Tiled导出器，并在现有4186服务真正打开Cocos；总体、N1、N2＋005、S1均已实看。**显示完成的是下列筛选子集，未代表11楼型全部接入、用户验收或阶段游戏测试完成。** 不等道具、不接B10在写修订、不改任何005/规划/原city/业务/存档。

## 打开与证据

- 默认近景：http://127.0.0.1:4186/revision-006/viewer/ （N2＋005原样板＋V01停车车）
- 总体：http://127.0.0.1:4186/revision-006/viewer/?view=overall
- N1新B06住宅：http://127.0.0.1:4186/revision-006/viewer/?view=N1
- S1南段：http://127.0.0.1:4186/revision-006/viewer/?view=S1
- [总体实拍](cocos-overall.jpg)、[N2＋005＋停车近景](cocos-near.jpg)、[N1新住宅近景](cocos-N1.jpg)、[S1门前铺地与原路](cocos-S1.jpg)。均为本Cocos运行截图，未用原生图或几何稿冒充。
- 总体画面中：N1在左下，N2在中部偏左，原005五楼在中部偏右，S1在右上。总体仅说明空间关系，细节以分段近景核对。
- Tiled绝对路径：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/integration/neighborhood.tmj`。
- 派生子集：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/integration/runtime-subset-plan.json`。
- 导出脚本：`neighborhood_export.py`；稳定输入适配/筛选：`adapt_access_v2.py`。

## 最终实际显示

36静态实例＝005原22＋新楼6＋新增树灯7＋V01-v2停车车1。另有原D骑手内存节点和程序阴影，读回总38节点。

005五栋B01～B05及其全部树灯原位置、worldSizeUnits、anchorUV保持；22原实例逐项核对，不移动B01/T01、不重复建一套原样板。005原有两株T03只作为明确保留的比较实例（comparisonAssets=['T03']），本次未新增T03。

|新增实例|楼型|
|---|---|
|N1-03-B05|B05|
|N1-04-B06|B06|
|N2-03-B02|B02|
|N2-04-B04|B04|
|S1-04-B05|B05|
|S1-05-B03|B03|

因此全场11栋，最终可见楼型为B01～B06六种；新增原生身份是B06非对称坡顶＋平顶住宅，其他为已认可族的邻段复用。B08确实尝试实测地脚筛选，未能进入本批，不能宣称市场已显示。N1/N2/S1各保留2栋。6栋新实例的库比例均为1，没有缩扁、拉斜、镜像或旋转。

83个地面多边形导出；旧地面、保留候选庭院与已审批1.5m步行铺地在原路下方绘制，原路最后覆盖。草地是受控颜色，铺装/路面是已有材质，没有新生纹理或假白盒补楼。保留的6条门前连接不变；将整栋新sprite的锚点平移到固定原生门像素与已批准门起点重合，未编辑门位/搜门偏移，位移及各项间隙见placement-screening.json。原生手估足迹有误差，此不替代精密地基/导航认证。

## 没有强塞的实例

- N1-01-B06：real native footprint intersects source road/source building/accepted or prior placed building/corridor；roadEdgeGap=2.806, sourceBuildingGap=0.0, priorNewBuildingGap=95.382, walkVsPriorNewGap=100.988
- N1-06-B01：real native footprint intersects source road/source building/accepted or prior placed building/corridor；roadEdgeGap=37.287, sourceBuildingGap=4.568, priorNewBuildingGap=7.755, walkVsPriorNewGap=0.0
- N2-01-B08：real native footprint intersects source road/source building/accepted or prior placed building/corridor；roadEdgeGap=-1.8, sourceBuildingGap=4.931, priorNewBuildingGap=38.969, walkVsPriorNewGap=46.817
- S1-01-B10：parent requires hold B10 pending separately notified revision
- S1-car：actual candidate vehicle length/width cannot fit original planned individual slot/court/clearance；roadEdgeGap=10.825, walkGap=29.96

其中B08按库的真实门与原生地基拟合后碰车行路，roadEdgeGap约−1.798m；N1-01-B06碰源楼；N1-06-B01会碰先保留楼的铺地。仅剔这些实例及其专用parcel/walk地面，不修改planning原版。B07/B09/B11原规划已经剔除，仍未加回；B10待父会话另行通知稳定修订。

V01-v2按可见近侧轮接地中点锚点放入原计划N2单车位，候选车身4.1×1.75可放入原4.2×1.8槽；保留路肩/铺地净空。V02-v2候选5.8×2.05超过原S1单车位，已从现有TMJ增量删除（incremental-edit-record.json），没有扩大车位、缩车或重置地图。两车仍在库，最终viewer只引用V01。停车是静态美术比较；车辆导航/交通AI/配送/商城均未实现。

## 运行包与读回

最终viewer只含实际引用的**16张唯一PNG，长边全部≤280，共1,332,488 bytes**；全包45文件、4,961,460 bytes（含Cocos引擎）。未装入B07/B08/B09/B10/B11/V02原图或运行图，未装原生母版/25图/source-context全城快照。资源库仍独立保留22张候选图；库大小不能当作运行包大小。

真实`__mapTextureStats`：uniqueAssetImages=16、nativeFramesCreated=14、canvasFramesCreated=2。按file+SHA共享image，按image共享Frame；36静态实例未各建独立纹理。材料只供程序地面使用，另外两个程序Frame为地面/阴影。

真实`__mapPreviewOrder`核对36个persistentId全部载入，editorOrder连续0～35；动态D骑手/阴影插入不改变静态相对次序。逐节点坐标与TMJ导出对应，最大差1.19e-07引擎单位（核对容差1e-5，来自壳投影常数舍入）。详runtime-readback.json、browser-overall.json、browser-near.json、export-report.json。

## 规划来源、编辑与完整性

父批准固定输入：`planning/next-neighborhood-plan-access-v2.json`，实读SHA：
`f14674986d26a205177bd50798230ed3ef37d404ec68ca65996a7049c2e708df`。

子集SHA：`4ff6861cfdd65ce36ed0308f09b7e1f8c899162c20eb6bccad6836a3db0faf60`。plan-gate.json单独记录父原SHA、派生规则和runtimePlanSHA，不把子集SHA冒充父批准原件；approved-plan.json为导出快照，独立核快照SHA。未读取仍在变动的规划别名。

3条完整原道路、29节点，ID去重后与005同路集；全部节点顺序/坐标/宽度/方向与完整原city逐值相等，projection与005逐值相等。只读底图/source/005等300项保护文件SHA终核保持，005原截图未写。真实完整道路仍存在JSON，显示地面bounds只裁视图，不裁改道路节点。

`python3 integration/neighborhood_export.py export`（从006执行）重新读本TMJ，仅更新本派生viewer。保留可编辑位置/正等比缩放/组偏移/可见性/层及index/topdown顺序，拒绝平面旋转/镜像/非等比。已验证`init`遇现有地图/viewer会拒绝，TMJ SHA未改变。V02删除是按persistentId定向增量，不是init重置。镜头由真实viewport与各段投影范围拟合；默认近景、总体与N1/S1分段按钮可切换，缩放保持中心。

## 实看问题与边界

- N1新B06的非对称房体与B05区别明显，可见连接门/台阶与铺地接到路肩；没有拿规划白盒填补剔除楼。
- N2新B02/B04及旧五楼、停车车已同场看见；V01仍比D骑手轮廓更粗、曲面高光更概括，保留静态比较候选，未美术/用户验收。
- 005原灯头朝车道、树池/自然树及少量针叶比较保持。新增N1灯在原路西侧朝车道内；树根未压保留楼入口。T03原有偏侧视差异不再扩大。
- 6栋中最近源楼间隙手估约0.40m，最近新增楼地脚间隙约1.20m；这是无相交筛选，**未宣称满足规划原1m源楼/2.5m楼间裕量目标**。手估地脚存在数十像素不确定性，应随实际画面由PM集中判断，不能伪装精密配准。
- 地面庭院仍可见几何边缘；邻段较疏、源建筑未全部渲染，整体不是填满全县交付。曲面楼/工坊hold与小道具后续工作不因此关闭。
- 未启动/终止服务器，未暴露端口/远程探测/申请扩权，未碰4182正式游戏、存档或接单购买。没有tests/typecheck/回归/提交推送。

历史资产库阶段报告保留在REPORT-library-stage.md；本报告覆盖“未创建006街段”的旧阶段状态。实际显示、图片候选与用户验收分别记录，后续仍待PM/用户外观检查及用户宣布阶段完成后的集中游戏测试。


## 009首批北侧源址增量（69实例/135地面）

已在同一006 Cocos实际显示4源址楼＋8场地物，新增20面；旧57/115与旧镜头/D路径保持。27 PNG / 2,127,723字节，无新增PNG。详见[本批报告](batch-009/REPORT.md)、[全景](batch-009/cocos-north-overall.jpg)、[近景](batch-009/cocos-north-market-close.jpg)。入口 http://127.0.0.1:4186/revision-006/viewer/?view=north 。未用户/导航/全县验收，未跑游戏测试。


## 009第二批五源址（74实例/164地面）

5源实际显示，20批准面＋9有限庭院/门前面；旧69/135及首批额外物件保护，0.9只应用一次并读回UI尺寸，共享27 PNG /2,127,723字节。详见[报告](batch-009-r2/REPORT.md)、[1.0与0.9真实等镜头对比](batch-009-r2/cocos-real-map-equal-scale-1_0-vs-0_9.jpg)、[住宅门前](batch-009-r2/cocos-round2-two-homes-close.jpg)。入口 http://127.0.0.1:4186/revision-006/viewer/?view=r2-courts 。原停靠点为新设计接近关联，无POI/业务/导航变更，未用户或全县验收。


## 009第三批20源（94实例/260地面）

20源/20模块/96面已在同一006 Cocos实际显示，0拒绝；旧74/164字段保持，0.9/1/1.1单次比例均读回核UI与共享Frame。27 PNG /2,127,723字节，无新增图。详见[本批报告](batch-009-r3/REPORT.md)、[中央近景](batch-009-r3/cocos-round3-central-close.jpg)、[东北近景](batch-009-r3/cocos-round3-northeast-close.jpg)、[宽关系图](batch-009-r3/cocos-round3-wide-relationship.jpg)。入口 http://127.0.0.1:4186/revision-006/viewer/?view=r3-central 。180m为邻接阈值，当前29明确源绑定不等于全县覆盖或业务/导航验收。


## 中央街巷生活层（局部用途整理）

593住宅小花园、610连门路休憩角、612树下长椅庭院已在同一Cocos实显。[街巷图](central-life/cocos-life-street.jpg) · [细节图](central-life/cocos-life-rest-detail.jpg) · [报告/逐面差分](central-life/REPORT.md)。新增9物/5面，选中10面候选调整；旧94对象与前164面、未选面/原门路保持。27 PNG /2,127,723字节，尚未用户或全县验收。


## 第四批40源址（life-street后增量）

40源/40模块/197面实际接入同一006，当前143静态/462面；原103/265及life-street全保护。27张PNG/2,127,723字节不增。局部关系＋U院/市场/住宅三近景、节点UI/Frame和保护SHA详见[本批报告](batch-009-r4/REPORT.md)。场地仍稀疏，候选未用户/全县验收。稳定scene SHA `9f7adf3e269fc320830b3b5b422797faed5014b453a99d199efd0c76d546bf8f`。


## 三件新原生有限比较（第四批后）

B12源1731/B13源1383各1件，T05现612庭院1簇，新增4面；当前146/466，旧143/462全保护。[实际两张Cocos图与校准/保护报告](native-comparison/REPORT.md)。30 PNG/2,425,880B，B13只用clean。仅比较，不是普通楼高/用户或批量验收。稳定scene SHA `64e00ad3a2d6654858233fe623d4fba1b81754bdc8b47f4d4676d6851ce51a5c`。


## 第五批v2（两个邻区，146实际基线后）

10源/10模块/31面准入0拒绝，当前156静态/497面/81源绑定；旧146/466全保，B12/B13/T05不扩量。[市场/住宅两张实际Cocos图、UI/Frame与保护报告](batch-009-r5/REPORT.md)。30PNG/2,425,880B不增；U1423只12m²部分内院，稀疏/裸前场仍未完成，不用户验收。稳定scene SHA `69ee3cb14645be306500d5db09a46a3eac4b5c75c8154eaacb586a90a23e6cc8`。


## 市场0587候场／休息／收集生活层

[实际市场全景与入口细节、逐面前后差分及保护报告](market-life/REPORT.md)。有限候场＋灯箱、树荫长椅、独立双桶、低灌木已实际可见；旧156物件/其他493面/原1.5m walk全保，改4授权面＋新4面/5物，当前161/501/81绑定。30PNG/2,425,880B不增，T05总2；不称用户/全县验收。稳定scene SHA `e781547b0767a058e47fad5459e45ab308951c67cf6e3237c9f10a48d824eaa7`。


## 源125受限一scene两模块

[受限入口、consumer负例、事务/保护及实际市场＋院落画面](compound-pilot/REPORT.md)。新增源1/scene1/modules2/面5，当前163静态/506面，源并集82、源scene所有者82、源模块83，不能按绑定记录长度冒称83源。原161/501/81记录全保。30PNG/2,425,880B不增。稳定scene SHA `237252cf5858346686c707335f1a323c0d14261631ec6262b6d403bbfd94b5cc`，仅局部比较，不用户/导航/全县或批量验收。
