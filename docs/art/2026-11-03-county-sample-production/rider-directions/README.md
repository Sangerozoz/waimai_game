# D级橙色电动车＋主角：八方向透明素材

制作日期：2026-11-03。使用内置 `image_gen.imagegen`，每个方向独立生成，保留原生alpha；无程序裁切、去底、调色或重采样。当前为已制作候选，**未用户验收、未引擎验证、未游戏测试**。

依据长期实施基准、已认可首页/车辆页、AU02 D车结构及当前县城美术样板。最新D识别为全橙车身、黑座、橙色后箱、圆形/近圆竖椭圆前灯；不沿用车辆页顶部C级奶白车板与横向方灯。骑手为橙帽橙服自然成人比例主角，不改变产品或车辆参数。

| screen-heading | 文件 | 表现 | 实际原生尺寸 |
| --- | --- | --- | --- |
| N | [rider-d-n.png](rider-d-n.png) | 向上，后视 | 1157×1359 |
| NE | [rider-d-ne.png](rider-d-ne.png) | 向右上，后侧 | 1312×1199 |
| E | [rider-d-e.png](rider-d-e.png) | 向右，侧面圆灯 | 1536×1024 |
| SE | [rider-d-se.png](rider-d-se.png) | 向右下，前侧圆灯；当前身份母版 | 1312×1199 |
| S | [rider-d-s.png](rider-d-s.png) | 向下，正面圆灯 | 1133×1388 |
| SW | [rider-d-sw.png](rider-d-sw.png) | 向左下，前侧圆灯 | 1312×1199 |
| W | [rider-d-w.png](rider-d-w.png) | 向左，侧面圆灯 | 1536×1024 |
| NW | [rider-d-nw.png](rider-d-nw.png) | 向左上，后侧 | 1312×1199 |

实际尺寸、RGBA mode、alpha范围、alpha>16主体框、SHA256、原生成路径、项目路径、提示词和地面锚点均在 [manifest.json](manifest.json)。原图在 `$CODEX_HOME/generated_images` 保留，11张归档副本逐一比对SHA一致。主体框不触边。E/W的alpha最大254是生成原件实测值；透明区底层RGB含暖色，不能脱离alpha当背景显示。

接入时坐标原点是原图左上，x向右、y向下。`frontWheelContact`、`backWheelContact` 为视觉候选；`groundAnchor` 取两轮接地点的中点，不能直接用画布底部中心。N前轮/S后轮被遮挡，位置为视觉推断，均未引擎验证。各原生画布与主体占幅不同，应按轮距/主体框统一世界显示比例，然后将地面中心贴至地图坐标；不建议所有原图直接使用同一像素高度。

八张已逐张目视检查朝向、人车完整、橙帽橙服、全橙D车、黑座橙箱和可见圆灯；未以平面旋转生成方向。独立重绘不是同一3D模型的精确八视图：箱体比例、轮毂、左右机械壳存在小差异，左右机械壳仍有近似对称重绘，尚未精确收口。已告知PM此限制，不把静态候选视作场景匹配或用户验收。

历史原件保留但不得接入：`rider-d-se-v1-cream-rejected.png`（奶白车板/方灯）、`rider-d-se-v2-squarelamp-rejected.png`（全橙但方灯）、`rider-d-e-v1-squarelamp-rejected.png`（旧侧灯）。SE按PM检查先修车板、再单目标修圆灯；E随后同步修圆灯。N/NE生成于圆灯修正前但前灯遮挡，当前保留；其余从最终圆灯SE制作。完整提示词在 [prompts](prompts/)，各次输入引用在manifest保留。

仅新增本目录的素材和资料，无业务代码、地图、经济、存档修改，无游戏运行、typecheck、回归、浏览器或Cocos操作。
