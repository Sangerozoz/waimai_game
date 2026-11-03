# 二维素材拼装街角实施报告

2026-11-03，框架已构建，等待 PM 提供最终素材清单、坐标和 PNG。依据 `docs/superpowers/specs/2026-11-03-modular-city-sprite-design.md`。

- `delivery-game/modular-city-project/` 是独立 Cocos Creator 3.8.8 2D 工程，未复制上一工程的 library/temp/build，也不连接正式游戏、订单或存档。代码 `assets/scripts/ModularCity.ts` 根据 `assets/asset-manifest.json` 和 `assets/sample-layout.json` 读取完整图片、原图锚点、显示宽度、原坐标和真实路段；建筑/树/道具为 Cocos Sprite，无临时盒子或颜色染色。
- 坐标将约定的 `.8660254*(dx-dy), .5*(dx+dy)` 转换为 Cocos 向上的 Y；地面使用透明图片材质在局部离屏画布按原始路宽铺装，再作为 Sprite 显示，建筑不使用画布切片或绘制。建筑、树和骑手按落地点及可选 layer 排序；单幅完整图遮挡是整体排序，不能处理角色穿过同一栋建筑前后部分等细粒度遮挡。路口接缝、贴图颜色、比例和排序效果须后续实际展示确定。
- 有拖动、滚轮/按钮有限缩放、复位；移动端有按钮缩放，尚无双指缩放。骑手沿一个首个合适原路段内存往返，只用于观察，不接业务或存储；运动朝向目前读取单帧，尚未切换八向。
- `delivery-game/scripts/build-modular-city.sh` 仅构建独立工程并打包到 `delivery-game/build/map-sample/modular-city/`；构建日志 `/private/tmp/modular-city-build.log` 11:34:58 显示 Finished，含 build-script 子进程 SIGTERM 诊断；静态入口存在，4181 监听存在。不能仅凭构建结果宣称运行或视觉成功。
- 资产目录目前没有最终 `asset-manifest.json`、`sample-layout.json` 或本批 PNG，部署入口因缺文件会报加载错误，不能交作画面。待 PM 告知最终 SHA、锚点和布局后，按相对路径将最终资源原样部署至入口 `assets/` 并记录 SHA，不覆盖 Cocos 构建数据；必要时按照实际资源接口调整。
- 未运行测试、typecheck、回归或正式游戏，也未操作存档，未作用户视觉验收。

## 资产进度与脚点观察

B01/B02/B03 原生透明建筑文件已落盘，完整 manifest、layout 及道路/树素材仍未交付，因此本轮没有部署不完整资源，也没有最终画面。用户否决的 `T02-tree-v1-front-view-rejected.png` 保留来源，禁止接入；树的斜俯视替代图由 PM 制作。只读查看用户斜俯视参考与三栋原图后，B03 正面基底线目测比参考图及 B01/B02 更接近水平；该观察不能推导精确投影或判定素材验收，最终须结合脚点、实际布局与画面观察。代码使用 manifest 最终 anchor 而非图像边缘猜测落点。

骑手演示改为选择离其初始 map 位置最近的、长度至少 4 米的原路段，并从对应投影位置开始往返，避免直接跳往第一条远处道路；若其初始点本身不在路段上仍会向最近路段投影。独立构建 `/private/tmp/modular-city-build-2.log` 11:49:37 Finished，包装脚本退出 0，仍含 build-script SIGTERM 诊断；未运行或验证实际组合。

## 候选资源预同步（12:09 后）

按 PM 指定，已把 `B01-cafe.png`、`B02-glass-v2.png`、`B03-residential-v2.png`、`T02-tree-v2-oblique.png`、`T03-tree.png`、`S01-paving.png`、`S02-asphalt.png` 原样复制到独立入口的 `assets/`；逐个源/目标 SHA256 一致。前述“本批 PNG 尚未部署”及 B03 v1 角度观察是历史，当前不使用 v1 建筑和用户否决的正视树；两版带光晕路灯均未复制。未修改 alpha 或重抠边缘，微 alpha 残余是否可见尚待组合展示。

静态图片元数据：五张建筑/树是 RGBA 且 alpha 范围 0–255，S01/S02 地面图片实际为 RGB。程序中完整图片使用 Cocos Sprite 默认白色，无三维灯光、蓝色罩层；地面图片仅作为路面铺装材质。正式 manifest/layout、最终路灯及骑手资源未到，入口仍无法组合完整画面；不因预同步宣称已接入场景或视觉验收。

## 路灯候选更正

PM 对 `P01-streetlamp-v2-halo-candidate.png` 的实际 alpha 做了像素核对：此前观察到的外侧 RGB 色值对应 alpha 0，不会以普通 alpha 合成显示。该灯为白天熄灯候选，已按 PM 确认原样同步到入口 assets，源和目标 SHA256 均为 `e1ae1b87448311bf282e7864544a76891441858f33983ec723a3715dbe252373`；未修改 alpha。上一段“两版均未复制”仅为更正前状态。最终 manifest/layout 尚待交付，尚未显示或验收。

## 显示范围与道路收口（12:23）

- 地面画布现在严格读取 `layout.bounds`，先裁地图矩形并仅处理与其带路宽包围盒相交的原路段；不根据完整道路的远处节点扩大地面画布或修改源路。
- 坐标、sprite 尺寸与地面统一读取 `manifest.projection.pixelsPerMeter`（规格为 32），不再使用代码固定的 20；等比变化后由完整图片外沿重新计算初始取景。720×1280 参考画幅使用左右各 30、上下合计约 150 的留白；缩放范围相对初始比例约 0.65–1.7 倍。实际手机视口下的画幅和素材遮挡尚待展示确认。
- 地面按路段先合成扩宽 0.28 米的路缘，再合成原宽道路，覆盖路口内部的部分重复边缘；宽至少 6.5 米且长度至少 14 米的路段添加虚线，端部预留 5 米。此为现有几何的显示装饰，不声称这些线是真实交通设施；密集复杂交口的衔接仍须实画检查。
- 独立构建日志 `/private/tmp/modular-city-build-3.log` 12:23:15 Finished，包装退出 0，仍有 build-script 子进程 SIGTERM 诊断。已预同步的素材未覆盖；最终 manifest/layout 尚未到，未进行实际画面、测试或验收。

## 最终清单与布局接入（12:28）

PM 最终清单、布局和 R01 已复制到 4181 的 `modular-city/assets/`：manifest SHA256 `d914d743664cb28ac45941509191256e803e7f9f56d2dd1d264e70cdf54faf05`，layout SHA256 `2a29cd749551d93b637ece78d526aa2d19b5198cbdb205a6a7e881f45d44fdbf`，R01 SHA256 `ca358184fa199f25b40c095e22f6e4ca3f1ca4263cdf21630078dc98dc441332`。部署清单的全部 9 项素材文件及 SHA 与清单一致，构建入口存在，4181 正监听。该状态覆盖此前“缺清单/不能组合”的历史描述。数据含 3 楼、7 树、6 灯；bounds 为 X[-1606,-1551]、Y[43,108]，完整源道路节点保持，只绘制 bounds 内地面。

静态对照发现放置物 layer 全为 10、原代码骑手为 0，会让骑手始终处于后面；现让骑手默认继承场景物件 layer，再依脚点排序，并采用布局指定的原路内存演示段。独立构建日志 `/private/tmp/modular-city-build-final.log` 12:28:49 Finished，包装退出 0，保留 build-script SIGTERM 诊断。未自动打开画面，也未游戏测试、typecheck 或操作存档。入口现可供 PM 打开隔离样板验证实际加载及画面，具体遮挡、脚点、接缝、取景及视觉质量尚未确认；不能以静态齐备代替用户验收。

## 首次拼装展示后的近景调整（12:34）

PM 首次实际显示并保存 `docs/art/2026-11-03-modular-city-assets/engine-v1.jpg`。图中可见独立建筑/树/路面，但楼体偏小、黑色清屏、地面呈硬边孤岛和较多空铺装；不能视为达到认可概念。根据该实图，初始取景由所有树灯外沿改为只统计 B01/B02/B03 的第一处主楼，将三楼全包围比例乘 1.5，镜头聚焦 B01 并允许邻楼超框。根据当前 layout 的几何静态计算，新比例约为旧版全物件取景的 1.98 倍；新增背景摆放不应再因远处树灯而自动压缩镜头。具体楼体屏幕尺寸及视口边缘效果须 PM 刷新观察。

独立 scene 的相机清屏由深黑改为中性浅灰米色 `(228,226,217)`；没有用额外整屏地块覆盖边界。原始道路、`bounds`、素材及像素未改；PM 侧的邻楼与近景布局仍在制作。本次独立构建 `/private/tmp/modular-city-build-closeup.log` 12:34:19 Finished、包装退出 0，日志保留 build-script 子进程 SIGTERM。当前部署 manifest/layout SHA 未变化；尚未观察新画面、未验证视觉效果或用户验收。

## 地面简化阴影（12:37）

在原有地面/路面绘制之后、所有独立 Sprite 显示之前，按建筑 `groundFootprint` 绘制朝屏幕右下偏移的低透明灰冷色简化阴影；树和灯按脚点绘制轻量径向渐隐接触影。阴影与路面共同合成为地面 Sprite，受既有 bounds 裁切，不修改素材图片、路网或建筑原始颜色。此为 2D 近似，非真实投影或准确遮挡；与素材自带阴影是否叠加、实际浓淡和方向是否协调需 PM 实画观察。

独立构建日志 `/private/tmp/modular-city-build-shadows.log` 12:37:28 Finished，包装脚本退出 0，仍记录 build-script 子进程 SIGTERM；4181 监听正常，当前 manifest/layout SHA 未改变。新邻楼布局仍由 PM 侧处理，本轮未运行游戏测试、typecheck 或操作存档，也未自行打开画面。

## 布局 v2 部署

PM 最终 `sample-layout.json` v2 已原样复制至 4181 入口，SHA256 `5ba2fac8d85eda22d356324b80e401ff5387470eac09649f85510d06f7ebce3b`；manifest 保持 `d914d743664cb28ac45941509191256e803e7f9f56d2dd1d264e70cdf54faf05`，清单所列素材文件 SHA 均一致。该布局共 21 个放置对象，含原三栋与五栋本批素材复用邻楼，以及原七树六灯；bounds 为 67×72 米。源数据、原三主楼与骑手不因部署而移动。

当前已构建 consumer 只按 B01/B02/B03 的首次出现定位三栋主楼，v2 中恰好对应 cameraFocus 的三个 placementId；新增邻楼不参与初始 fit。沿用中性背景与 12:37 构建的二维简化接触影，无需重建纯 JSON 变更。4181 监听正常，可供 PM 刷新隔离样板；尚未自行打开 v2 画面，不声称接缝、遮挡或画风通过验收。此前 v1 layout SHA 与数量记录保留历史。

## 沿街镜头焦点（12:46）

PM 保存的 `engine-v2.jpg` 显示近景素材清晰，但主要朝向东侧院内，前景铺装过多、道路位于建筑后方。已让 consumer 使用布局的 `cameraFocus.placementIds` 中三栋西侧街排计算比例，并将 `map:[-1591,75]` 投影为镜头中心，应用 `screenOffset:[0,-70]`；padding 按米转显示坐标并用于计算包围尺寸，保留 1.5 倍近景策略。未把其他楼、树或灯纳入 fit；该取景允许部分楼体超出画面。旧布局无 cameraFocus 时保留原 fallback。

更新后的布局部署 SHA256 为 `a190dd06c3f95aa244c9a759ed13d5d6d3b88a91539eb3e2c7af750d5e07aac6`，旧 v2 保存在 `sample-layout-v2.json`。独立构建日志 `/private/tmp/modular-city-build-focus.log` 12:46:55 Finished、包装退出 0，含 build-script 子进程 SIGTERM 诊断；本机 4181 仍监听。仅改变相机消费及焦点配置，未重排地块或重新生成图片；新画面尚待 PM 刷新确认，不代填视觉验收。

## MC-REV1 六项修订：显示层准备（新固定开发）

按2026-11-03六项修订规格/plan推进，当前尚待PM新原生楼图与revision-manifest，未构建/未展示。只修改独立ModularCity.ts；原脚本和部署assets已复制到工程revision-backups/mc-rev1-start/，未改PM源素材、旧manifest/layout、源city或业务存档。

- 骑手渲染宽固定为6.4×ppm，旧3.2m精确同比×2，使用原PNG比例、原轮接点锚点及route。此是显示尺寸，不是车辆属性。
- Asset接口新增heightMeters、groundPolygon以及frontage:{screenSide,entranceUV}。原图UV反投影为地图门点，入口细砖带连接最近道路外侧的人行道；完整Sprite不翻图、不旋转。
- 路面按原节点/原宽绘制，人行道为道路外侧2.2m带，路缘0.24m；入口砖用S03-entry，树池土草用S04-soil，缺新图时只有候选色回退。土芯/少量草/低石围边以树根为中心，局部矮栏，车道最后重绘保证净空；另有路缘排水盖和原虚线。7棵现有树根距车道边最小约1.95m，树池半宽1.05m，无须移动树。
- 左上来光/右下地面投影：楼体按原图groundPolygon与heightMeters生成占地+偏移点的凸包，树按冠幅/高度投影加干影，灯杆按高度画杆/灯头影，再叠加接触影。是二维地面近似，不能跨立面接收或解决完整图片内的细粒度遮挡，未声称3D实时光照。
- 道路侧静态盘点：西侧主景3栋适用E；building-b03适用北侧道路W；neighbor-east-middle可用W但门前连接较长。building-b01/b02/neighbor-east-rear最近道路位于map-x背面，当前仅E(+x)/W(+y)素材无法全部正门临街，已向PM报告，待有界摆位/版本选择。不能用入口砖带冒充正确朝向。

本段为代码已写及静态几何事实，非构建成功/新画面/游戏测试或用户验收。按用户节奏未运行tests、typecheck、回归或渲染矩阵；旧engine-v3不代表本次修改效果。

### 背立面与集成接口补充

PM已决定保留8实例摆位，并补B11-N/B12-N/B13-N原生背面观察素材；不将3栋挪到北路堆叠。frontage支持screenSide:'hidden-left'、visible:false、normalMap及entranceMapOffset（相对放置map、随scale同比），隐藏门不伪造entranceUV。入口地面会被完整楼图遮住，仅露出部分可见；隐藏门本身不能通过当前镜头确认。

工程tools/integrate-revision.py准备将PM只读revision清单合并成工程runtime-data，按新原图UV重新计算占地、精确设置R01=6.4m，记录源及部署数据SHA；不写PM源文件。集成脚本尚未执行。旧完整17MB部署另存revision-backups/mc-rev1-start/deployed-site/，可恢复旧代码包与assets，不只备份PNG。

### 等待机位修正版期间的源码收口

PM通知首批v1机位偏浅、暂不集成构建，已遵守，当前可访问部署未变。入口连接现在按frontage.normalMap（缺省由right/left/hidden-left映射+x/+y/-x）筛选朝向前方的道路，防止把背向道路通过铺装伪装成正门临街。候选门点至车道边超过8m则跳过铺装并记录具体placement警告，待素材/几何收口，不画明显长连接。该8m为本次显示层保守候选上限，不改变路网或经营规则。

只修改源码和本报告；未预部署首批v1图，未构建、tests、typecheck或运行画面。方向/距离判断的实际呈现仍待最终候选集成，不能据此声明8栋朝向已正确。

### 楼前/楼侧窄地坪补充

按PM追加审读，在道路人行道之前增加每栋楼的占地随形窄地坪：使用新asset.groundPolygon反投影（缺省使用既有groundFootprint），轮廓向外0.8m铺S03-entry，外围约0.12m克制条石收边。不额外生成大矩形平台、不涂大面积草色，后绘的人行道与车道路缘保留原道路位置及宽度。背景底色仍是范围底色，不能宣称楼间全部区域已做完整地块设计；该窄地坪仅依据素材落地轮廓，不冒充源地籍边界。

未改变当前部署，也未构建/测试/显示；机位修正版与最终清单继续由PM产出后接入。

### 固定engine-v3镜头比例

cameraFocus新增fixedScale（要求有限正数），有此字段时优先于建筑包围盒fit计算；交互缩放范围和复位仍相对该初始值。工程集成脚本为本轮runtime layout固定0.6129619059310744，保留map[-1591,75]与screenOffset[0,-70]。该值由PM按旧图清单/布局公式静态计算提供，不是新运行验证；新素材外沿不再改变初始道路屏幕比例，使同锚点R01从3.2m改为6.4m时屏幕宽高也同比2倍。源码和集成脚本已写，尚未执行集成或构建，旧部署未改。

### 骑手动态接地影

增加独立小canvas生成的rider-ground-shadow Sprite，不改原PNG。透明度较低的短右下投影、轮点附近接触影，以原轮接地中点为锚，使用与骑手相同route投影位置并在每帧同步；与骑手共用layer/脚点y参与整体排序，同脚点用sortBias=-1确保在骑手之下。其结果遵守现有完整图片的整体建筑排序，仍不能解决单张楼图内部细粒度遮挡或跨立面接收；两处轮影是按现有NE单帧制作的接地候选，未冒称精准重建轮形。

等待最终manifest后才统一集成构建。本项尚未构建或运行显示，未测试/操作业务存档。

## MC-REV1 必要独立编译产物交接（素材生成故障期间）

按PM明确派工，只执行原Cocos构建命令，不调用含部署复制的build-modular-city.sh。第一次沙箱启动退出134、空日志；随后在获准普通应用环境运行同一独立工程构建。2026-11-03 13:34:07日志显示`build Task (modular-city) Finished`，Cocos进程退出36，保留`build-script`子进程SIGTERM、trackTime计时缺项和插件update check网络失败诊断；不表述为零诊断/全检查通过。

实际编译输出留在`delivery-game/modular-city-project/build/modular-city/`，26个文件，index.html时间13:34。`assets/main/index.c3359.js`实际含`rider-ground-shadow`和固定镜头逻辑。持久证据：工程`revision-build-evidence/mc-rev1-compile-app.log`及`mc-rev1-compile-record.json`（含源码/构建文件SHA、退出码、素材SHA和部署未变记录）。源码SHA256为`b55db30a68b4a8b8f9b10b828d3abff78d731cddec9be85bb054309f8786f92b`。

**部署边界：** 构建前后旧`delivery-game/build/map-sample/modular-city/`全部68个文件逐个SHA一致。未复制新编译包到4181，未生成伪造的完整revision清单，工程集成脚本未执行，PM素材未被修改。17MB旧部署回退整包仍保留。未打开/请求页面，未运行tests/typecheck/游戏回归/渲染矩阵，未操作存档。

**素材与六项的真实状态：**

1. 建筑美观：PM目录已有9方向v1及B12-E-v2（共10栋图）；其中v1存在已知偏浅机位，只有B12-E-v2为本轮机位修正有效候选，其余7个本轮实用修订方向因生图服务连接故障未产出。未集成/部署，不能称建筑外观已修正。
2. 地面：分车道/人行道/入口砖/随形窄地坪及路缘代码已编译；S03-entry-brick-v1.png、S04-soil-grass-v1.png两个原生材质已实际落PM目录，SHA见记录。新材质尚未集成/部署，不能以源码存在称已看到地面改善。
3. 树落地：土芯、少量草、低围边和局部矮栏代码已编译，按原7根点净空候选，不改被拒绝树资源；未运行显示。
4. 正门朝向：可见门UV/隐藏背门offset/道路法线/最长8m连接接口已编译；原8实例最终方向选择等待PM完整清单，未完成素材接入，未声明全楼门向通过。
5. 骑手：6.4m宽高同比及固定镜头比例支持已编译；本轮runtime layout固定配置由未执行的集成脚本准备，尚未部署；不以编译代替屏幕实测。
6. 光影：楼占地+高度方向影、树冠/干影、灯杆影/接触影及随route的骑手阴影均已编译；仍为二维地面近似，跨立面接收和完整图片内细粒度遮挡限制保留，未视觉验收。

现可交付的是显示层源码和独立编译包，不是六项完整可访问新版本。待生图服务恢复或用户明确授权的后备渠道补齐复核素材后，再按完整清单接入并必要构建部署；不得拿已知v1冒充修正版。
