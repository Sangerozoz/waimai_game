# 已独立复审：受限scene级适配＋源125一次真实入图

这是实施与运行交付，不是只写方案。父已读独立review，结论safe-for-limited-integration；现授权你在原同一Tiled/Cocos中支持并实际接入**仅这个1源/1scene/2modules/5面**。不扩成全量多模块自动生产，不删去重断言绕过旧接口。

## 精确输入与基线
候选：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-009/planning/compound-pilot/scene-compound-pilot.json
批准原SHA a5564388f2efb4afc55c8baa50e0f0607b1d0484ded6c2b05b6cc9abda6edb27。
独审：revision-009/review/compound-pilot-review/REPORT.md、review.json（核其reviewedCandidateSHA与当前target）。必读scenic-scene-contract.md、producer import-contract、latest161-recheck；原包/原生/审查都只读，不“修复”sceneId或ID。
当前场景161/501/81，scene SHA e781547b0767a058e47fad5459e45ab308951c67cf6e3237c9f10a48d824eaa7；TMJ 5a4ee4e32ca61f88c81d97161469fa558fdfa75d1f8051ffaeef7c03badfee5c。父已再次核实际目标未前进。若后续有合法新基线，须重核而非回退。旧156只是producer历史来源，不能重放快照。

## 写集与接口任务
仍仅006/integration、viewer、009/pipeline。先读你自己的prepare_fifth/add_fifth、neighborhood_export/batch_prepare/schema及计数所有调用再做最小适配；优先独立compound入口＋必要共用校验/计数扩展，别重写主renderer/迁移旧记录。无新库/工程/服务/原生图，无游戏tests/typecheck/回归/FPS/存档/业务/UI/经济/提交。

1. 事务写入前验证受支持schema、sceneId/moduleIds双向归属、源polygon/SHA、每源唯一scene所有权、模块/面persistentId唯一；允许source125只在009compound-source0125-court内两模块共享，跨scene/旧绑定/预留源继续拒绝。旧sourceIndex/sourcePolygon与数组schema仅临时归一化检查，所有旧81记录字段不回写。已存在的明确compound归属后续仍需识别，不能把已合法同scene模块误当两个旧scene。
2. 计数用源集合并集与模块/scene分别计算，不能len(visualReplacements)当sourceCount。旧81源保护，本次两模块都指125仍只加1；每模块自己的ID、sourceNativeSHA、真门/脚线、sceneId必须可追溯。源计数不是经营地址。
3. 原PPU/UV与canonical×单一正比例：B05@0.9、B01@1，输入worldSizeUnits/anchor/footprint/entry已经最终值，nodeScale1，不再二乘。保留B01真实手估四点与不确定性，不能换整图框当精密脚线。source125外伸院地已独审，不扩大经营或豁免其他原源。
4. 接入前独立核当前161实体/501面（含市场5新物/8新改面）、所有原source/完整原路水/蓝边/POI与同scene两模块、门路/5面；同源不互相豁免。原路605760963-0完整数组/width5/direction1保持，既有road字典字段不覆盖，不新增nav/经营点。铺地先基底后真门路、土床不盖通路，新模块按地脚排序，旧161固定值/相对顺序保持。
5. 场景原子追加：两模块和5面一起成立才写，失败整scene保留候选，不悄悄删成单模块称复合已完成。重复apply拒绝，异常不得留下半个Tiled/scene。原source和批准JSON不可改；适配产物自己SHA和原SHA分列。
6. 用真实consumer的静态输入预检（非游戏测试）实际演示拒绝重复ID、缺scene、漏列模块/孤儿、跨scene复用源、旧绑定/预留源冲突和重复apply；坏输入在临时副本/内存构造且明确负例，不假装production数据。失败前后主图SHA不变。这是新入口完整性校验，不跑pytest/typecheck/行为回归/渲染矩阵，不引用审查模型结果冒充consumer已支持。

## 实际交付
保旧161所有block字段/世界图框/排序值、501面、原镜头/D/source/POI/nav及原city；不改市场层或原B12/B13/T05有限状态。只增此scene2楼/5面，使用现有<=280 PNG和共享Frame，不打包原生/25图/全城快照。不新增其他道具/面，不借本次放宽旧场地权限。

先实际打开同一viewer，交一张能看清**两栋楼＋共享院落/真门路＋现有市场/原路关系**的有用近景（必要再1张细节），别交纯几何/远处小点或矩阵。重点看B05距旧市场门路余量、排序/门阶/土床是否遮通行；不为小残差重生或变形。真实读回每新节点宽高/坐标/Frame缓存，源并集/scene/module计数、旧数据保护、单次scale和PNG预算；源数显示必须按集合不是模块长度。

交可执行受限入口、静态预检负例证据、实际增量前后/保护/稳定scene与TMJ SHA、截图与短REPORT。真实出现阻塞即报告，不 fabricated、不把准备包当已显示；成功也只是一次局部运行比较，不是批量、美术/导航/用户/全县验收。
