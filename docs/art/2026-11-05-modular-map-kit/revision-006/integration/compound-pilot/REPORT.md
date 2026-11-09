# 源125复合院落：一次受限运行交付

[同一viewer](http://127.0.0.1:4186/revision-006/viewer/?view=compound-market) · [真实市场关系图](cocos-compound-market.jpg) · [真门路细节](cocos-compound-detail.jpg)

两新楼、共享院落/真门路、现有市场与原道路已实际Cocos显示。仅**源125／scene009compound-source0125-court／两模块／五面**；没有额外道具/面，也不扩为批量生产、美术/导航/用户或全县验收。两张图为实际页面直接取图，未拼贴/生图；全景有整市场与两楼，细节屋顶自然裁切。全技术记录见[TECHNICAL-NOTES.md](TECHNICAL-NOTES.md)。

## 实际计数与旧数据保护

- 从真实161静态／501面／81源增量到**163静态／506面**。旧161所有block字段、图框/PPU/UV、实际UI、固定排序值及相对顺序，旧501面、旧镜头/D/市场层/source/POI/nav全部保持；Tiled原层/对象/tiles/index/组偏移全保持。
- 源集合并集**82**、源绑定scene所有者**82**、源绑定模块记录**83**。旧81单模块记录只在内存临时归一化为legacy owners、不回写；明确compoundScenes注册只有本次1scene，源125两模块共享只加1源，绝非83源或经营地址。后续读取当前合法scene已实际识别为同一所有者。
- B12/B13/T05仍原有限实例，hold状态不扩。原95条引用路/619完整节点不改；605760963-0保完整4点、width5/direction1，既有road字典不覆盖。

Tiled：`/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/integration/neighborhood.tmj`。

## 受限入口与真实负例

[compound_import.py](../compound_import.py)复用batch_prepare.Context原生校验与同一neighborhood_export；[compound_contract.py](../../../revision-009/pipeline/compound_contract.py)验证schema、scene/module/面双向归属、源polygon/SHA、每源唯一scene、旧绑定/预留与ID防重。[compound-schema.json](../../../revision-009/pipeline/compound-schema.json)单独记录受限形状；旧batch_prepare明确拒绝本compound schema，未删除旧去重断言。

```sh
python3 docs/art/2026-11-05-modular-map-kit/revision-006/integration/compound_import.py preflight
python3 docs/art/2026-11-05-modular-map-kit/revision-006/integration/compound_import.py negative-probes
python3 docs/art/2026-11-05-modular-map-kit/revision-006/integration/compound_import.py apply
python3 docs/art/2026-11-05-modular-map-kit/revision-006/integration/verify_compound_pilot.py
```

均已真实执行。consumer-negative-preflight.json：12类明确内存坏副本（重复模块/面ID、缺sceneId/scene、漏列/孤儿/缺模块、跨scene复用源、旧数组260/旧单数630/已用1731冲突、独立预留114、未知schema）均由同一preflight拒绝，主TMJ/scene/manifest SHA前后不变。独立预留负例只在内存去掉旧绑定以隔离该规则，不改生产。发布后重复apply也实拒且主SHA不变；不冒用独审模型结果或游戏tests。

先整scene暂存导出并核旧数据，再带备份/journal逐文件原子替换；异常恢复全部目标，未完成日志可`recover`，不声称跨文件原子系统。两模块/五面必须一起成立，transaction-journal已committed。暂存是同一壳的导出证据，非新工程/服务。首次暂存曾捕获旧north_region重复插入镜头筛选代码，在live写入前拦下；只加已存在则跳过判断，当前renderer字节未改，失败stage证据保留。重复export的TMJ/scene/manifest/HTML/renderer现均字节稳定。

## 真实脚线、门路与运行尺寸

原SHA/PPU/UV保留；B05@0.9、B01@1，输入world frame已最终值，nodeScale均1，不二乘。B01携带原手估四点[198,910]/[438,1229]/[1055,931]/[815,612]及25px不确定性，B05沿原校准含推断后角，未把整图框冒充精密脚线。native/tool母版及运行图SHA实际重核。

|模块|单次标量|实际world frame|实际UI像素|实际nodeXY|固定插入值|
|---|---|---|---|---|---|
|B05|0.9|9.162777×10.486393|293.208871×335.564577|[227.8259344123397, -5744.888343066962]|128.888888889|
|B01|1|7.936234×9.940515|253.959490×318.096485|[-166.53612464825343, -5825.789208444775]|128.944444444|

实际163静态＋D/影子共165项均读回核坐标/尺寸/scale/index；新两节点Frame文件与缓存index见new-two-runtime-node-frame-check.json。同scene实体仍互查：体间4.691031m，门路距对方实体最小4.445288m；只本栋首0.6m手估门槛允许有限接触，之后自身脚线≥0.05m。

consumer独立重核最新161实体/501面（含市场五脚点及8处新改面）、所有他源、9970原路、492水道/水polygon、蓝边/POI与同scene两体/五面，距离下界剪枝不漏障碍。B05距旧市场walk1.312391m，屋顶在图上遮住后方旧步道短段，未见市场入口被堵，实体脚线/旧路径保持；这是实看残差，不扩大误差豁免。

四块铺地连通，基底→有限种植面→共享连接→真门路，原路最后；种植面不盖通路。G02仍为已有受控种植色，不是新原生土纹。脚线外伸8.021/13.400㎡已按批准scene全局重核，约19.47%原carrier被新脚线覆盖是美术重组，非等形测绘/扩大经营边界。原semantic unknown、POI/nav不改。

## 预算、SHA与未解

仍30张≤280 PNG、2,425,880字节，新增PNG0；实际30 images／28 nativeFrames／2 canvasFrames，重复file+SHA共享Frame。全景/细节各只激活一块≤2048有限地面，原生/25图/全城快照不入包；未测FPS/实际内存。736个只读源/规划/原生/审查文件SHA不变。source原候选的rendered0只是保留输入证据，实际本次显示证据来自截图与runtime读回，不回改批准包。

- parentOriginalSHA256：`a5564388f2efb4afc55c8baa50e0f0607b1d0484ded6c2b05b6cc9abda6edb27`
- derivedSHA256：`bd304158193244a7e7d3c62247c318415c01fa503ebae0cfcd6eb2075def3896`
- baselineSceneSHA256：`e781547b0767a058e47fad5459e45ab308951c67cf6e3237c9f10a48d824eaa7`
- finalSceneSHA256：`237252cf5858346686c707335f1a323c0d14261631ec6262b6d403bbfd94b5cc`
- finalTiledSHA256：`26eb9baad3f38a13570c5c23d4cadd5a5f4f4ef29f1c5a174436d3c566fd99e8`

仍有B01重复、裸种植色块、软边、素材与原路轴角差和屋顶局部遮路视觉残差；未为此生图/变形/加物。无新Agent/库/工程/服务、游戏tests/typecheck/回归/渲染矩阵/FPS、业务/UI/经济/存档或提交。未用户验收、未导航或全县完成。
