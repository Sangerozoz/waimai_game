# 三维街角视觉样板

2026-11-03。承接用户“让我看看你的能力”：实际制作上轮推荐的小范围样板。用户此前已确认目标画风、原路网和范围，不重新设计产品或让用户重选方向。

## 目标和隔离

在 Cocos Creator 3.8.8 内制作一个独立、可浏览的三维街角。使用榕树街食堂—晴川广场380×440米范围内真实道路和三个相邻建筑足迹，其中一个足迹不规则。固定斜俯视近景，相机目标为三栋主要建筑与街面；不一开始展示整县。源 city.json、经营逻辑、存档、现有页面保持不变。旧 Canvas 方案保留为历史，不再作为正式新样板。

## 画面要求

以 docs/art/2026-11-03-sample-fidelity-rework/user-target-v2-concept.png 为已确认方向。三栋为转角餐饮商铺、现代玻璃沿街楼、普通商住楼：体量及首层各有区别。完整体块、厚窗框、大玻璃、立体遮阳棚、屋顶女儿墙与设备、门口台阶和少量街边桌椅。道路保留源中心线/宽度，增加连续人行道、路缘、必要路口标线、地面树、路灯、街边设施与静态D车/骑手尺度参照。不得屋顶种树；不用大片绿地或空铺装填空间；保持暖白建筑、少量橙色与参考图现有蓝灰程度。

三维几何、真实深度遮挡、统一太阳/环境光及投射阴影是本次要落地的表现层。精细资产通过独立设计的几何组合制作，禁止仅给相同盒子循环贴窗。无成熟外部模型库，不安装或下载未知授权资产。

## 数据接口

主资产路径 docs/art/2026-11-03-street-corner-3d/scene-design.json。各形状用世界米制的局部引擎坐标，地图平面映射为 X=x-origin.x、Z=-(y-origin.y)，竖直为Y。source 元数据记录原始SHA、中心节点/原始道路ID、三栋建筑源索引与原足迹，任何镜头旋转不改变道路拓扑。

JSON 根字段：version:1、origin:{x,y}、source、camera:{target:[x,y,z],position:[x,y,z],orthoHeight:number}、materials:{[key]:{color:'#rrggbb',roughness:number,metallic?:number,emissive?:'#rrggbb'}}、objects:数组。object 的公共字段 name、material、position:[x,y,z]、rotation:[x,y,z]（角度，默认0）、castShadow（默认true）、receiveShadow（默认true）。几何 type 为 box（size:[x,y,z]）、cylinder（radius:number,radiusTop?:number,height:number,segments?:number）、sphere（radius:number,scale?:[x,y,z]）、mesh（vertices:number[],indices:number[],normals?:number[]）。mesh使用三角形并保证外朝；允许开发计算缺省法线。所有依赖只读，默认只用此JSON，无保存功能。

## 展示和边界

独立 Cocos 场景与单独构建目录，使用现有本机4181服务下 street-corner-3d/ 入口。画面占据主体，仅必要缩放/复位与载入失败提示，无新产品HUD、无测试面板。不让新样板替换正式游戏业务入口；旧 county-sample 增加明确新样板链接即可。

用户只在说“阶段完成”后组织游戏测试，本轮不自动运行测试、typecheck、正式游戏操作或截图矩阵；必要构建及输入资产静态完整性检查可以进行。用户本轮直接要求“让我看看你的能力”，交付允许对这个隔离且无业务/存档的美术样板生成实际运行画面，作为展示产物；这不构成玩法测试或代替用户验收。交付报告必须区分源码、资产、构建、样板展示与实际视觉验收，不声称已达到参考图。无需新增设计确认，常规技术问题自主解决。
