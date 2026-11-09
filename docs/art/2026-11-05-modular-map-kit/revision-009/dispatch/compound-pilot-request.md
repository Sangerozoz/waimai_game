# 复合场地静态试点：先补未知记录，再验证一个真正可放的多模块场景

父已读独立审查及真实plan/assemble分支，复核45源：7因无旧metadata直接延期、38试算、6可行全在旧池，净新增0。不是距离算法已证bug，不再盲目扩大散点批次。PM决定见revision-009/scenic-scene-contract.md，必须遵守。你继续规划执行，审查者thr_vgk87iy5cy保持独立；本轮先交静态产物，不改共享实现或直接接入。

唯一新增写集：/Users/sanger/Documents/ChatGPT/taptap 2/docs/art/2026-11-05-modular-map-kit/revision-009/planning/compound-pilot/。上轮fit-round-5及历史资料永久只读，不改gate/renderer/library/city/原路/边界/水/POI/业务/存档，不生图、不测试/typecheck/回归/FPS/浏览器/服务/提交/新Agent。

## 只读输入和基线
- 独立审查revision-009/review/placement-capacity-audit/REPORT.md、classification/examples与源级证据；不要执行原写脚本。
- 父冻结数据revision-009/baselines/visible156/scene-layout.json、asset-library.json、parent-check.json：父在市场作者开工前已实核156/497/81，现从内存序列化为规划快照，published SHA与serialized SHA已分列，不把两者混同。snapshot只供规划，不回放主图。旧准入B01～B08校准可读visible143与后续已完成对应footprint-review；新增13实例真实脚线可读已完成r4/r5/native-comparison产物，别把整个屋顶billboard冒精密地脚。
- 原city/三层边界、原投影、已认可25图只读。共享接入作者正在做market0587生活层，不消费/等待在写viewer或renderer新版本；后续入图仍须对其最新完成基线复核。原子场地之间碰撞不能因快照滞后自动豁免。

## 真正执行的小目标
1. 对未测7源586/125/590/588/430/580/429作只读空间清单和有限入口可达性试算。原用途仍unknown，新增scenicProgramme/证据明确是PM美术设计，不冒充原历史/业务类型，缺旧testedSources记录不再自动当空间失败。父几何初算586约13.33㎡、590约407.25㎡，其余见parent-check，不是可行认证；按真实形状/道路/邻楼判断，不能13㎡小源硬塞楼。
2. 选其中一个真正合适的**未绑定/未预留**源，优先考察较大590而非预设一定通过，做一个sceneId下两种体量模块（现B01～B08，合理既有正比例）。若单源不成，最多两个实际相邻源共同一场景、最多3模块，显式列真实owned源集合，不跨原道路圈大片未画楼豁免。可先给7源中合法单模块子集，但复合失败需完整记据，不凑数；不重跑源1/377旧三个偏移失败当新成果。
3. 实际检查各模块真实原生脚线/门阶/路径、模块间净空、其他原源/旧156和497面、原路水/蓝边/POI，只有声明拥有的源carrier可豁免。新同scene铺地可以有合乎用途的连接/层叠，但不能让同scene模块彼此穿、穿真门路或车道。原道路完整数组/顺序/width/direction和停靠node不改，门为视觉接近不新建经营点。
4. 给scene级sourceIndices/sourcePolygonsMap/moduleIds与每模块sceneId/persistentId/entry/footprint/最终worldSizeUnits；源数按集合并集，模块数独立，不能沿用len(assigned)==len(buildings)断言。源可在同一scene多个模块引用，不得跨scene/旧已绑定源重复占用。不要删除既有防重断言就让新包“过”；本轮只在自己的新静态schema实现严格scene所有权校验，旧格式/旧文件不动。
5. 不修改旧草坪/铺地权限，不用放开旧面作为试点默认前提。若需要某个具体旧面接边，单列surfaceId/字段/场景所有者/理由和其他失败，不自己改动或放开全部障碍。B12/B13/T05原有比较不扩准入，B09～11/T04不使用，不等新图。

交scene-compound-pilot.json（若真实可行）、import-contract.json、7源逐源/逐模块尝试及失败JSON、纯静态核验脚本和一个局部几何投影图/短REPORT。脚本在本目录实际执行，原输入SHA前后核；原源数、scene数、module数、已显示/用户验收分开。先交一个稳定可用候选原SHA，后给独立复审；本轮不向共享代码或运行图apply，不声称已经增密。没有可行复合就直说，不编造支持或偷偷换源。
