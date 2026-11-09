用户已认可revision-005混合街段，授权持续推进和多对话并行，明确参考已认可25图的建筑多样性。运行素材长边一律<=280；统一机位/光照/画风，不统一造型，换色/换牌不算新款。
你只做地图资产，不做游戏/UI/经济/车辆参数/存档/路网/边界修改，不建Agent或线程，不fork/新worktree，不跑游戏tests/typecheck/回归，不commit/push，不读凭据。仓库 /Users/sanger/Documents/ChatGPT/taptap 2。新写集仅下述revision-006专属目录，revision-005和更旧只读。
先看revision-006/references/approved-25-index.json和approved-25-contact.jpg，从总览选候选后打开完整源图。25源已核SHA，图07锁TR25-v2。每件记录来源图号/region/version/SHA/完整单栋像素box/选择理由到自己references子目录；不把整张邻图作为生图构图/机位输入，不把裁片放大冒充原生。可读25区district-identities.json辅助，但必须看图不靠名字。
固定几何参考revision-003/road-constraint.json，当前frontage屏幕-28.486deg、depth+55.406deg，墙体竖直，不转/镜像/拉斜旧PNG。几何脚本可读revision-005/references/make_references.py和guides.json，在自己目录做新体量辅助图。候选尺寸非用户硬限/源实测。画风参考docs/art/2026-11-03-whole-region-map/references/2026-11-03-user-building-variety.png，已认可五楼只用于机位/光照收尾，不复制浅墙玻璃配方。自然日光，无黄洗/整图蓝染/亮窗/屋顶树/文字logo。
每个指定ID真正用当前内置image_gen原生生成一次；在本Agent内按顺序，第一件原生和来源先保存再做第二件。跨Agent并行已授权。每件最多一次，不额外扩量/重试；网络/工具阻塞如实报，不用空等文字冒充提交，不启外部付费API/浏览器生图或程序盒子代替原生。
每件交付OWN/ID-v1.png原生逐字节副本、provenance.json（真实tool源绝对路径/完整实际prompt/参考SHA/实际尺寸modealpha/源副本SHA/候选状态）、ID-runtime-280.png及.runtime.json、短REPORT.md。原生母版不进包。运行导出可直接执行只读工具：
python3 docs/art/2026-11-05-modular-map-kit/revision-005/runtime-size-pilot/export_runtime.py --output-dir OWN --max-edge 280 --single-source OWN/ID-v1.png --single-target OWN/ID-runtime-280.png
实际打开图检查主体/透明边/机位/差异，估读地基/接地点需注明不精密，不称用户验收/地图完成。final简短中文给真实绝对路径/尺寸字节/缺陷/阻塞，parent auto收，不重复发信。

本角色任务（规划角色以此处不生图覆盖上方出图流程）：
你不生图，改为几何/布局执行Agent。唯一新写集revision-006/planning/，其余全部只读。输出实际执行的规划脚本、next-neighborhood-plan.json、标明几何底稿的SVG/PNG与一份短REPORT，不停在文字方案。
读取原完整city：delivery-game/assets/resources/map-sample/city.json；先确认schema不要猜字段。读取docs/art/2026-11-02-county-zoning/selection.json及README，把红全图/蓝经营/绿繁华的真实近似坐标依据带入。先核实已认可revision-005样板坐标实际属于哪一层，不能因为它被接受就假设位于繁华区。
为接下来的2~3个相邻街段/两类街区提出可执行原坐标布局，优先蓝内可与原路连接的城区/居住混合区，保留源道路所有节点顺序/宽度/方向和原业务入口，不新增道路/桥/POI/经营范围。若原样板不适合作正式区域，应如实标明并选择符合原边界的新区域，不挪原路迁就。
资产输入旧B01~B05和本轮B06~B11是已出/在制库，按候选足迹与退距放约10~20栋的有意场景，不铺整县，不把同套街区复制。体现住宅/商业/设施与院落/绿化/停车组织差别，住宅约50%是全县蓝内总体面积方向非本块强凑楼数。运行280与共享贴图。
当前资产主方向frontage-28.486、depth55.406；从实际源街段切向验证能否用，不能拿世界轴代替路向。优先选相近路向便于先落地；其他路向明确列出需要新原生朝向的gap，不能转PNG。对原路/水体/楼间距作静态多边形/线段碰撞和定量净距核对，报告候选尺寸不等于精密原生标定。
输出保留完整源道路/来源SHA/每块zone依据/道路ID及节点范围/拟用楼型anchor与地块polygon/ground surfaces/车与树灯位/摄像机建议/资源依赖和未满足朝向。避免直接修改已认可revision-005 Tiled或viewer，本任务不浏览器/服务器/游戏测试，只做实际落盘并执行的数据规划。

所有相对目录前缀为 docs/art/2026-11-05-modular-map-kit/。不得写其他角色目录。
