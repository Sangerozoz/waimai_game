# 下一地图增量：蓝内郊区/宽院落真实选址，不再按小盒子硬塞

当前006已真实显示43静态实例，含连通休憩角；007小物首批10候选已回，部分未入场因缺合适语境/净空。用户授权自主持续地图制作、丰富场景，不扩产品/UI/经济/业务/存档。你只做有来源的地块/原路规划，不生图、不浏览器/测试/提交。唯一写集 /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-008/planning/。006/007/旧计划/原city全部只读，不改已显示43实例或既有85地面。

目标：找一处蓝框内、优先绿框外的郊区/较宽院落场地，作为同一地图下一可见增量。有住宅小院/小规模园艺，视真实合适场地可有低层市场B08或工坊B11/公共B09特殊地块与后勤停车，不把油箱摆餐桌/住宅门口，不为展示所有资产而违反分区。蓝外只自然背景不得扩大经营/取送/导航；原road/city/水/原业务入口全保持。

只读输入：
- 完整city与docs/art/2026-11-02-county-zoning/selection.json。用真实蓝绿范围、源原道路节点/宽度/方向/连通，不靠crop画面猜坐标。
- /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-003/road-constraint.json：当前资产族u/n投影。优先找同族路向或可合理侧院接入的地块；无法同族就列最小必要新朝向缺口，不旋转/拉斜PNG迁就源路，不泛化生产27种朝向。
- /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-006/integration/asset-library.json、asset-calibration.json、prop-calibration.json、prop-corners-calibration.json、REPORT.md、REPORT-rest-corner.md：按真实手估足迹/门位/世界尺寸选地，不回到名义7x6矩形。
- /Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-007/review/prop-admission.json：P04只v2，P09只园艺比较未过当前机位，围栏P06/P07为不同实际短跨度不能声称标准闭环。

步骤与边界：
1. 先盘点源路与可用宽场地，输出少量真正可行的候选及取舍。优先安排库中可用B05/B06/B08等，以及菜畦P08、短围栏、树与合适后勤车位；小块地面必须形成完整院落/铺地/菜园等功能场景，不能只有几幢孤立楼或大片未规划裸地。
2. 43实例原样板作为固定保护区。源建筑可以作为“原址视觉替换”的只读承载对象候选，尤其无业务源楼，不要一律当不可用隐形障碍后又在缝里硬塞新增楼；必须明确visualReplacementOf原源ID、保持数据/业务门点、实际轮廓不会撞其他楼/路/水。没有足够证据就不用该替换候选，不擅自改变原city/入口或创建新业务POI。
3. 从actual footprint先选地/留通路，再定anchor。B08曾因按真实门对位侵路约1.8m被剔，这次允许在**新的宽地块/新候选**中调整整栋位置并规划新有限步行面，不照搬原不合适小场地；旧已交付原路/路径不动。V02当前候选5.8x2.05且锚点是近侧轮中点，规划足够真正容纳的后勤车位并记清锚点含义，不缩成小车。停车纯静态不增加交通AI/路由。
4. 接入作者另在/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-008/calibration/独立复核B07/B09/B11不规则轮廓/内院空腔/真实可见门位；这些目前hold，不能先标ready或伪造矩形/长边中央门。你先完成不依赖这些hold的可行核心，再标出可放更宽体量的备选槽位，不轮询等待他。父收到两边产出后统一接合。不要等待或读取半写校准文件。
5. 输出next-district-plan.json、源ID/坐标/方向/分区与保护SHA、实际多边形地面与入口/菜畦/后勤停车位置、清晰投影图、简短REPORT。schema沿用可被006导出适配的projection/roads/buildings/fixtures/groundSurfaces/parkingSpaces/parkedVehicles，并区分核心可行子集/依赖待核。只是规划，不叫运行/整县完成。

只复用既有资源，不生成新素材；找不到安全空位不改路、不强填数量。完成直接回父会话：稳定文件路径/SHA、可行布局与真正缺口。
