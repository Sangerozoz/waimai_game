# HC-CITY-1103 独立高机位街角实施报告

2026-11-03，用户“那我们可以开始干活了吗？”后的固定开发实施。依据同日high-camera-city-design规格/plan与长期基准。PM写docs美术，固定开发单写delivery-game及本报告；保留所有已有dirty/untracked，不worktree/commit/push/发布。

## 当前源码产出（尚未编译/集成）

- `delivery-game/high-camera-city-project/`独立Cocos Creator 3.8.8项目，仅复用既有scene/settings并剔除历史disabled controller序列化项，未复制library/temp/build。保留旧modular-city及其他入口和原地图/业务/存档。
- `assets/scripts/Projection.ts`唯一canvas-down投影入口：X=(.7071067812,.6272113751)、Y=(-.7071067812,.6272113751)、Z=(0,-.4617486132)，显示时统一反转Y以适配Cocos。道路画布矩阵也从该入口求轴，不另建旧.866/.5投影。
- `HighCameraCity.ts`读取独立manifest/layout，加载原生两整块图与两方向骑手，核对原文件SHA及nativeSize；整图按anchorUV/anchorMap、nativePixelsPerUnit同比放置。未用guide/概念/程序盒体代替地块；整块深度按sortMap地面前缘候选，保留整图遮挡局限。
- 原完整道路数组只读，按原宽绘沥青/边缘/1.8m人行道，显示只裁bounds；两块原生地景负责入口砖、树池/土草和固定光影等美术。骑手沿原route地图插值，按NE/SW两原生帧切换，轮点接地影同步；不接正式订单或存储。
- 相机新配置默认52投影单位横宽/720参考画幅，允许PM具体camera覆盖，非旧fit。拖动/缩放无旋转，最小缩放不低于初始，保持骑手参考可读性。
- 旧R01原生alpha>0 bbox为(0,54)-(1296,1199)，原画布1312×1199；按旧公式作制作尺寸换算，720参考下旧画布宽62.7672992px，2倍画布目标125.5345983px，2倍alpha轮廓宽124.0036886px/高109.5557280px。每张新骑手按opaqueBoundsUV四数数组统一补偿画布宽高，满足三个下限；这为元数据计算，不是新运行画面测量/用户验收。极淡alpha残边会影响bbox，是保守制作参考。
- `tools/prepare-runtime.py`准备只读PM最终清单，把projection.originMap适配origin、parcels适配blocks、方向帧适配forward/reverse，保留原roads/route，输出工程runtime-data及SHA记录，不改PM文件。
- `delivery-game/scripts/build-high-camera-city.sh`默认只编译；显式--deploy需完整runtime-data才打包到新的`build/map-sample/high-camera-city/`，若该新入口已有版本先备份。未调用脚本，未新建占位部署。

## 待PM最终素材包

已读PMscene-layout：原主路149397380-0，originMap[-1591.5766733668343,75]；两块22×18m、前缘在车道路缘外1.8m，四楼退距6.3m、高9/10.5m均为PM候选；不声称原地图全楼满足。原三路完整节点/方向/宽度与原示范route只读保留。

还需实际原生地块/两方向骑手、实读anchor/controlPoints/nativePixelsPerUnit、sortMap及完整asset-manifest。现阶段不执行集成脚本、不部署无图版本；不把guide盒体或HC01概念当最终对齐底图。

## 权限与真实未完成

本轮未运行tests/typecheck/回归/渲染矩阵/页面/存档，尚未构建、部署或HTTP检查。Work本地浏览器自动化禁用，不绕过、不声称看见新画面。静态加载接口存在不能代替资产配准/运行或美术验收；两方向演示、整块排序、固定光影的范围限制继续保留。

## 首次必要独立编译（覆盖上文“尚未编译”的时点状态）

15:53:29在普通应用环境完成Cocos独立编译，日志显示`build Task (high-camera-city) Finished`，进程退出36；仍有build-script子进程SIGTERM和asset-db trackTimeEnd缺项诊断。不宣称全检查通过。实际bundle `build/high-camera-city/assets/main/index.1db80.js`包含新HighCameraCity逻辑，场景序列化与index均实际产出；证据保留工程`build-evidence/initial-compile.log`和`initial-compile-record.json`（含源码与全部编译文件SHA）。

未运行prepare-runtime或部署脚本，正式原生素材/清单仍待PM，编译包不能当成完整画面。旧modular-city部署全部68文件SHA与MC-REV1前基线一致，新的high-camera-city部署目录未创建，无占位版上线。未做HTTP/页面/游戏测试、typecheck或存档操作；编译不是新画面实显或美术验收。

## 原生道路材质收口（首编译后，待最终包再构建）

按PM指令复用原生`docs/art/2026-11-03-modular-city-assets/`的S01-paving.png和S02-asphalt.png；原manifest来源SHA与源文件实际SHA一致，分别为`45c3eb327861a41a418eb3d8ab9baf9e129c2022fd86051e6492451bc1e7ed3b`与`06cf22f3d6f84b39afb93fec03b67e6a84f4c823bbf91b7c9e1778cb960ef47f`。

prepare-runtime会将两项以material身份按原字节复制随包，不改PM manifest或源PNG；运行加载同样校对SHA/nativeSize。ground()改为统一世界坐标CanvasPattern（人行道3m周期/沥青10m周期），原节点和车行道宽不改。补路缘排水小盖和局部边线，段端留白避开部分交口；无随机噪点替代原生材质。完整地块内部仍由原生整图负责，不程序盖地块。样板外未规划区域仍是范围背景，不能称已完成整县地块；最终近景取景需结合实际图边与参考相机收口，不能用大片万能底色冒充地块内容完成。

骑手明确采用旧R01 **alpha>0** 的保守bbox制作参考（含极淡边缘），2倍轮廓下限宽124.0036886px/高109.5557280px；新图按PM **alpha>8** 的opaqueBoundsUV补偿，因此不把新图透明画布当可见轮廓。画布同时至少125.5345983px宽。待新帧实际尺寸与bounds到齐再记录每方向计算显示值，当前没有新运行屏幕测量。

本次源码改动晚于initial-compile，不套用之前编译结果。尚未再次构建、集成或部署，待PM完整原生包后统一执行；未测试/typecheck/打开页面。

## 正式原生包集成与新入口交付（覆盖前述待素材/未部署状态）

PM明确packageComplete后，实际读取4张1254×1254原生透明候选、配准控制点/估计说明与scene-layout。执行prepare-runtime生成工程runtime-data：保留PM原图字节和元数据，加入字节复用S01/S02 material、origin适配和双方向帧ID，不改PM源文件。4张图和2张材质的部署SHA均与清单一致，runtime全部文件与部署副本一致。

- 新入口：`http://127.0.0.1:4181/high-camera-city/`。仅该独立目录新增部署，旧modular-city全部68文件SHA与MC-REV1前基线一致；其他入口未操作。
- 正式runtime manifest SHA256：`4d4478af33b8b90d89c6d890b171c800597cc68d7db7b0528c32e1608f3df7c4`。
- 正式runtime layout SHA256：`c3037faf6cab8a563b65fec09d47e9fb8dc55ca0f9a74c97d689f9ac2aa5c4e4`。
- 三路完整节点/宽度/方向及示范route与旧sample-layout逐值相同；源city SHA仍为`536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20`。
- 最终相机按PM配置viewWidthUnits=54、focusMap[-1591.5766733668343,75]，720参考初始zoom=0.4166666667，无旧fit沿用。新图每块只按实际nativePPU与anchor统一缩放/平移，无变形/镜像/平面旋转。

### 构建、部署和可达证据

执行`build-high-camera-city.sh --deploy`：16:11:03 Cocos日志显示Finished，Cocos原始退出36，包装脚本退出0；保留build-script子进程SIGTERM与asset-db trackTimeEnd缺项。最终编译bundle为`build/high-camera-city/assets/main/index.d54a8.js`，不同于首次编译的index.1db80.js，已含原生道路材质改动。完整日志持久保存工程`build-evidence/final-build.log`，源码/所有编译与部署文件SHA在`build-evidence/deployment-record.json`。

沙箱HTTP无法连接，获准普通环境执行HEAD后，新入口、两份JSON和6张素材均HTTP200；记录`build-evidence/http-head-record.json`。HEAD只证明可达，不执行页面脚本、不表示Cocos实际加载/渲染或画面通过。没有新运行截图，不沿用旧engine-v3充当新画面。

### 两方向骑手的计算尺寸（720参考，不是屏幕实测）

旧参考仍采用alpha>0保守bbox，新图采用PMalpha>8 opaqueBounds。原始轮点锚点保持，PNG无像素更改。统一比例计算结果：

| 方向 | 画布宽高px | alpha>8可见轮廓宽px | 可见轮廓高px |
| --- | --- | --- | --- |
| NE | 137.8552×137.8552 | 124.0037 | 124.5534 |
| SW | 136.7640×136.7640 | 124.0037 | 126.1849 |

两帧画布均超过125.5346px最低宽，可见轮廓宽均达旧保守参考两倍，高均超过109.5557px的两倍下限。运行仍受视口适配/遮挡影响，不能以元数据计算声称已实测所有位置可见。按原路线地图插值并切NE/SW，独立接地影同步；仅演示，不连接业务/存档。

### 明确保留的美术/表现限制

两块nativePPU分别40.0611249321、39.9647517458；沿街对应点决定比例与平移，西/东后部最大残差约2.2338/1.1952投影单位。东岸上临街角被遮挡、属估计点；不宣称四角精确62.5°标定或画中楼高/退距实测通过。四楼9/10.5m、墙退6.3m为几何制作候选，不等于绘画全满足。

NE轮轴约34°，原路屏幕航向约28.5°；SW与NE为独立原生绘画，比例/身份/轮点仍有细节差异。没有通过镜像、旋转或压扁掩盖偏差。整块Sprite按front sortMap整体排序，不能处理块内逐树/逐立面精细遮挡，固定光影也不是动态真实光照；在用户已接受的局部穿帮范围内交候选，不扩全县或升级全面遮挡系统。

当前真实状态是“源码与正式原生包已集成，必要独立构建/新入口部署完成，HTTP可达；未运行页面/游戏测试/typecheck/回归/渲染矩阵，未用户美术验收”。原存档/业务/经济数据未操作，无commit/push/发布。

## HC-CITY-R2 准备：已认可v1备份与四地块接口

依据同日R2规格/plan，用户“继续做吧”授权增加主景一层、顺接南侧地块。首样v1基本满意的规则保留；PM正在原生制作，不整体拉伸旧完整地块。

修改前已完整保存工程`revision-backups/hc-v1-before-r2/`：assets源码/meta、settings、tools、runtime-data、build-evidence、完整build、package/config及构建脚本副本，另存完整已认可部署35文件。`snapshot-record.json`记录全部文件SHA与v1部署清单。新增独立对照入口`/high-camera-city-v1/`，与原入口35文件逐个SHA一致；当前原`/high-camera-city/`未覆盖。

源码移除恰好2块限制，改为检查非空且逐块有实际block资产，兼容4块。布局新增可选`groundRegions:[{id,polygon,materialId,tileMeters?}]`接口，仅绘PM布局指定的步行过渡（世界坐标材质），随后重绘原道路，不创建可通车道路。建议使用既有S01-paving、3m周期，不重做已满意整块内部。prepare-runtime支持parcels各自anchorMap/sortMap优先，便于同图不同世界放置；PM六资产/四地块包齐才执行集成。

本时点仅源码/备份/对照副本已落盘，未集成R2素材、未构建或更新原入口，也未HTTP/页面/测试。原路线延长与priorRoute等待PM最终layout，不在源码猜测或改变正式业务。骑手两帧/尺寸、投影与材质未改。
