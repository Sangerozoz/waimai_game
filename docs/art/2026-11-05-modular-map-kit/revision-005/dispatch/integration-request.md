# 地图接入执行：五类真实楼型＋树灯混合街段

你是本地图PM的独立接入开发Agent。用户已授权多个对话并行加快地图，已认可B01/首街段观感，要求真正的建筑/树/车辆多样性、运行素材长边最多280。现在原生图已回齐，你的交付必须是实际可见的新混合街段，不是计划/清单。你不负责游戏开发/UI/经济/存档，不建立其他Agent，不fork/新worktree。

## 独占写集
仓库 /Users/sanger/Documents/ChatGPT/taptap 2。
只写 docs/art/2026-11-05-modular-map-kit/revision-005/integration/ 与 revision-005/viewer/，包括脚本、独立可编辑mixed-street.tmj、精简运行包、报告/截图。不要写其他目录、全局设置、旧地图/旧viewer、原生PNG、公共BRIEF/production-brief。不commit/push。不要跑游戏tests/typecheck/回归/渲染矩阵，不操作真实存档；允许必要的数据导出/静态完整性与本独立viewer真实显示核对。

## 只读输入与当前事实
所有下列路径相对docs/art/2026-11-05-modular-map-kit/：
- revision-005/planning/mixed-street-layout.json 及 plan_mixed_street.py/REPORT.md：5栋楼、38地面多边形、17灯树fixture的原路布局，3条完整原路已保留。B01锚点LOCKED [-1596.5787045725883,58.400981377657935]。其他新楼允许为实际原生足迹做小摆位调整，但不挪路。规划候选尺寸不是源实测。
- revision-004/tiled_street.py、integration/bridge-meta.json、integration/street.tmj、viewer：已有可靠的Tiled底左锚点→map坐标、静态index/topdown排序、地面多边形、缩放保持中心的参考实现，不修改它们。
- revision-005/runtime-280/viewer：已运行的<=280精简壳！推荐作为新viewer壳来源。它已修复按file+SHA共用解码image与SpriteFrame、worldSizeUnits保持裁边后物理尺寸、真正只包含引用PNG。不要退回整目录全原图复制/每实例新建Texture。现有globalThis.__mapPreviewOrder与__mapTextureStats可实际读回。
- revision-005/runtime-size-pilot/export_runtime.py 是只读通用派生工具，可用 --output-dir OWN --max-edge 280 --single-source RAW --single-target OWN/runtime.png 输出PNG与.runtime.json（cropBox/sourceSize/runtimeSize/SHA）；不得修改共用工具。运行PNG是派生图，不是新的原生输出。
- B01原生 revision-003/B01-road-aligned-native-v1.png，原校准 revision-003/native-calibration.json。必须保持已认可的B01原锚点/比例（nativePPU111.2618392940353、原anchorPixel[626.5,920.5]），可直接复用runtime-280现有B01 worldSizeUnits/anchorUV。
- B02新办公楼：revision-005/native/B02-001/B02-v1.png、B02-runtime-280.png、provenance.json、B02-runtime-280.runtime.json。真实三层退台，不复制B01。
- B03窄高楼：revision-005/native/B03-001/B03-v1.png、B03-runtime-280.png及同目录provenance/运行元数据。
- B04低层展馆：revision-005/native/B04-001/B04-v1.png、B04-runtime-280.png及元数据。
- B05坡屋顶住宅：revision-005/native/B05-001/B05-v1.png、B05-runtime-280.png及元数据；源身份已在自己OWN/恢复/重选，见source-selection。原生底边余量窄、彩边需如实记录，不伪造已验收。
- T01认可树：pilot/T01-v1.png；直接复用runtime-280里T01的校准/派生图，比例不重设计。
- T02自然阔叶变体：revision-005/native/T02-free-001/T02-free-v1.png与T02-free-runtime-280.png。无树池，偏窄冠；它是同族变体，不能算新增树种，机位仍待同场检查。
- T03针叶自然树已回：revision-005/native/T03-pine-001/T03-pine-v1.png、T03-pine-runtime-280.png。分层针叶冠不同于阔叶，但自报偏侧视，必须放同场检查，不能自动声称高俯视通过。
- 新近/远侧灯：revision-005/native/retry-near-001/L01-road-near-v1.png、native/far-001/L01-road-far-v1.png 与各自provenance。近侧臂+n向车道、远侧臂−n向车道，杆竖直，远侧原生多一段折肘需如实检查。不要继续用方向反的旧L01/L02填位置。新近灯280派生参考runtime-280/examples/new-near-lamp-280.png，需自己在独占目录导出/拷贝所需派生图，不能改native。
- revision-005/references/guides.json、各B02~B05-geometry.png：只是几何参考，可辅助初始足迹/尺度，绝不拿请求角度当实际配准结果。

## 必须完成的执行
1. 先打开实际5栋楼/树灯成图，不依赖子Agent自报。核验每件原生副本与provenance实际tool源SHA；核验运行图长边<=280。保持所有输入SHA不变。
2. 写统一asset-calibration.json：B01/T01保持已认可校准；其余从真实原生估读地基角点/树根或灯脚/杆高，正等比PPU。可以对实际地基边与PM候选足迹做单一正标量拟合，但不非等比拉伸/平面转图/镜像，不挪源路。全部手估/候选尺度明确标注，不伪造精密控制点或registration-ready。裁边后anchorUV与worldSizeUnits必须按原像素变换，不能PNG缩了世界物体也缩。
3. 接入规划5栋不同楼型和两侧向内灯、T01沿街树。T02/T03可先少量比较：规划自然树位置里混用两种冠形，不把树池复制到自然林。如果实际视角不合适，先排除问题树并报告，不为了凑齐把不合格树铺全场。
4. 按源JSON导出全部地面安排（草坪/种植/草甸为受控地面颜色或已有材质，不假称新的原生纹理），原路最后覆盖，3条roads节点顺序/宽度/方向/projection逐值不变。不要创造桥/新道路/POI或改变蓝内配送业务。
5. 独立可编辑Tiled mixed-street.tmj；导出位置、正等比缩放、可见性、组偏移和层/index顺序；初始化拒绝重置已有手改地图，导出只改本派生viewer。旧probe/revision.tmj都保留。
6. viewer只包含实际引用的唯一<=280图，实例共享图像/Frame；字节/唯一图片/实例数用代码统计。仅复用已有D骑手内存演示，不能把车辆多样性说成已完成。
7. **必须真正打开并看新Cocos画面**。现有父会话静态服务端口4186，root是kit目录，日志在 /Users/sanger/.hermes/cache/scratch/map-4186-server.log；不要另起/杀服务。新URL http://127.0.0.1:4186/revision-005/viewer/。若服务异常报告父会话，不去改游戏预览4182。
8. 默认镜头必须让5栋楼与原路的混合街段清楚可见，不再只有稀疏小点。规划viewWidth61是名义建议：当前landscape Cocos固定高度会导致它太远，需依据实际canvas/design可见尺寸拟合。可提供总体/分段近景按钮或query入口；缩放保持中心。不要靠裁掉问题对象宣称全场通过。
9. 保存真实运行全景和至少一张有多种楼的近景到integration/；实际读回__mapPreviewOrder与__mapTextureStats，记录5栋都已载入、节点坐标/静态顺序对应导出。说明遮挡/接地/灯向/树视角可见问题，轻微残差按用户容忍不反复生图。

## 回报
不要停在stub/计划，交可打开URL、Tiled绝对路径、运行图路径、资源文件字节统计、原路/旧图SHA保持结果、真实已显示/未通过项。图片产出、运行可见和用户验收严格分开。若真阻塞说明精确原因和已有可用子集，不能编造截图/完成结果。final用简短中文，父会话auto接收；不重复发信。
