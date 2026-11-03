# SHOP-1101 美术资源交接

2026-11-01。状态：十档车辆复用清单已整理，四张实际生产图均已查看并记录规格，资源交接收口，未做引擎或用户验收。仅维护本文件与manifest.json；未改代码、导入资源、运行游戏测试/typecheck/渲染，未代用户视觉验收。

依据：`docs/superpowers/plans/2026-11-01-vehicle-shop-implementation.md`；商城目标 `docs/art/vehicle-garage-concept/vehicle-shop-screen-v2.png`。主角也是骑手，所有具体配车均在骑手页。商城仅展示车型、买车与拥有数量，不显示使用中或配置对象，购买不自动装备。

## D与D+：实际母版与静态映射

本轮已实际查看两张原图。D为圆形大灯、弧形前罩、明显剥落旧橙漆、贴纸残痕与磨损旧橙箱；D+为方形灯、外露前叉及棱角前罩、更干净的橙黄漆面与箱体。两者须分别使用母版，不能从概念图裁车、镜像或换色冒充另一档。

只读检查 `VehicleSideArt.ts` 与 `CartoonArt.ts`：前者tier 1/2分别使用side-d/side-d-plus。后者第73–74行留有早期D+共用D别名，但第90–91行随后覆盖为V01独立侧45与顶视图；因此当前有效静态映射不同，未发现D/D+最终映射错误。此结论仅针对读到的源码，不是运行页面验收，也不能解释所有可能的加载/构图问题。旧注释不应被当成最终映射。

## 十档侧45母版复用

路径相对仓库根目录。SHA、像素尺寸与alpha范围见同目录manifest.json，均来自实际文件元数据；除D/D+外，本轮未逐图视觉查看。

| 档位 | 原件精确路径 | 引擎资源键（无扩展名） |
|---|---|---|
| D | `docs/art/user-deliveries/2026-10-30-au02/vehicle-d-three-quarter-original.png` | `map-sample/anime/au02/vehicle-d-three-quarter-original` |
| D+ | `docs/art/user-deliveries/2026-10-31-vehicles/V01-d-plus-45.png` | `map-sample/anime/vehicles-20261031/V01-d-plus-45` |
| C | `docs/art/user-deliveries/2026-10-31-vehicles/V02-c-45.png` | `map-sample/anime/vehicles-20261031/V02-c-45` |
| C+ | `docs/art/user-deliveries/2026-10-31-vehicles/V03-c-plus-45.png` | `map-sample/anime/vehicles-20261031/V03-c-plus-45` |
| B | `docs/art/user-deliveries/2026-10-31-vehicles/V04-b-45.png` | `map-sample/anime/vehicles-20261031/V04-b-45` |
| B+ | `docs/art/user-deliveries/2026-10-31-vehicles/V05-b-plus-45.png` | `map-sample/anime/vehicles-20261031/V05-b-plus-45` |
| A | `docs/art/user-deliveries/2026-10-31-vehicles/vV06-a-45.png` | `map-sample/anime/vehicles-20261031/vV06-a-45` |
| S | `docs/art/user-deliveries/2026-10-31-vehicles/V07-s-45.png` | `map-sample/anime/vehicles-20261031/V07-s-45` |
| SS | `docs/art/user-deliveries/2026-10-31-vehicles/V08-ss-45.png` | `map-sample/anime/vehicles-20261031/V08-ss-45` |
| SSS | `docs/art/user-deliveries/2026-10-31-vehicles/V09-sss-45.png` | `map-sample/anime/vehicles-20261031/V09-sss-45` |

## 适配交接

- 大预览与卡片缩略图复用各档同一原件，保宽高比，以可见车体边界统一尺度、以轮胎接地点统一落地线；不按完整透明画布统一视觉大小。A原件名确为`vV06-a-45.png`。
- 原图有alpha不代表边缘干净；D/D+可见暖色半透明光晕，缩小或叠深色背景时仍需开发注意。原件不覆盖，不把自动去光晕当作本轮已完成。
- 车体已有阴影时避免重复叠黑；独立接触影由引擎适配。概念图车辆不是替代母版。B车颜色争议不在本轮擅自改色。
- 商城按车型聚合真实拥有数，骑手页按独立车辆ID配置；其他骑手占用车不可选，新买另一台才有空闲车。不要把同档多辆合并为一个配置实例。

## 背景与无字UI皮肤：四张实际图

目标为1张无车/无字/无UI干净车库背景，以及共享无字材质皮肤（深色面板、普通卡框、暖橙按钮；选中态可叠橙边，页签可共享）。应接近商城稿的磨损材质、边角高光与深浅层次。不能以普通平面矩形代替皮肤目标。动态文字、档位、拥有数、余额、价格与交互状态由引擎绘制。

PM提供实际图后再补：精确路径、尺寸、模式、alpha范围、SHA、实看问题、候选九宫格边界与伸缩安全区。九宫格数值在实际图尚未查看前不预填；最终引擎表现待阶段集中测试及用户体验确认。此处不提前宣称资源通过。

### 已收到并实际查看：背景与面板

- `garage-clean-background.png`：1374×1145、RGB，无alpha；实看为空车库、左侧街景暖光、连续地面，未见车辆、UI或可读文字。下方地面为车辆接地区，车轮需落在地面上；缩放裁切应保留地面与光向，不把整张强行拉成长竖图。场景工具、轮胎与箱体仅装饰。此为静态素材观察，不是页面验收。
- `metal-panel.png`：2172×724、RGBA，alpha范围0–255；深炭灰中心、磨损金属包边与四角螺钉，无字。四周透明留白且有极低alpha散点，**不能用整图或alpha>0包围盒作为皮肤可见边界**。alpha>0框为(0,12)–(2156,724)，alpha>16主体框为(41,139)–(2131,568)，坐标均为左上原图像素、右下排除。
- 面板建议SpriteFrame rect候选为 **x=33,y=131,width=2106,height=445**：围绕主体保留8px余量，舍弃远离主体的低alpha散点。无需另裁原图；开发可设置SpriteFrame rect，保持源PNG。矩形内仍可能含少量边缘alpha，不代表已清理。
- 九宫格候选值相对此rect：**left=144,right=144,top=112,bottom=112px**。固定螺钉、斜切角与边框，中心区域可伸缩；作为横向信息条/列表面板共用。该值按实物角部范围估计，未在引擎拉伸验证，短小卡框不能直接照搬此值。文字放在内边框再向内留白的区域，不压磨损边角。

上述两图实际SHA与元数据已写manifest。卡框与主按钮规格见下表，四张已齐。所有候选均未通过游戏测试或用户视觉验收。

### 卡框与主按钮：最终补齐

两张均已查看本地实际原图，无烘焙文字或车辆。卡框为深炭灰实心底、磨损金属边、内侧细金线与斜切角，**中心不透明**，车辆和动态数据需叠于其上；按钮为明亮暖橙黄、金属包边及圆角高光。四张生成图共同承担商城材质层次，不用普通矩形替代。

| 文件 | 尺寸/模式 | alpha>16主体框（左上–右下排除） | SpriteFrame候选rect（x,y,w,h） | 相对此rect的九宫格候选L/R/T/B |
|---|---|---|---|---|
| card-frame.png | 1122×1402 RGBA | (25,37)–(1098,1364) | (17,29,1089,1343) | 128/128/128/128px |
| primary-amber-button.png | 2172×724 RGBA | (62,164)–(2110,552) | (54,156,2064,404) | 144/144/96/96px |

两图alpha均0–255。卡框alpha>0框为(0,0)–(1110,1382)，按钮为(39,39)–(2114,692)，包含远离主体的微弱散点；裁切候选按alpha>16主体外扩8px，不以整幅透明画布占据UI布局。原图保留，不另裁图。九宫格固定斜切角/圆角与高光边缘，拉伸中心；卡框源为竖向，三列列表卡片缩短时要保留角部比例与内容留白，最终边缘值由开发按实际目标节点调整，不能宣称已验证。按钮中心提供动态购买文字/价格，禁用态与按压由引擎处理。

四张实际文件的完整SHA256、尺寸、alpha与候选切片均见`manifest.json`的`generatedAssets`。来源为PM本轮生成交付，实际prompt由PM保存在同目录；本角色只查看、记录，不重生或修改原件。十档车辆继续以既有母版为权威，尤其D圆灯旧漆与D+方灯整洁结构，不从商城概念图取代。

本轮资源文档已收口；未改代码/导入资源，未运行游戏测试、typecheck或渲染，未代用户视觉验收。
