用户已认可revision-005混合街段，授权持续推进和多对话并行，明确参考已认可25图的建筑多样性。运行素材长边一律<=280；统一机位/光照/画风，不统一造型，换色/换牌不算新款。
你只做地图资产，不做游戏/UI/经济/车辆参数/存档/路网/边界修改，不建Agent或线程，不fork/新worktree，不跑游戏tests/typecheck/回归，不commit/push，不读凭据。仓库 /Users/sanger/Documents/ChatGPT/taptap 2。新写集仅下述revision-006专属目录，revision-005和更旧只读。
先看revision-006/references/approved-25-index.json和approved-25-contact.jpg，从总览选候选后打开完整源图。25源已核SHA，图07锁TR25-v2。每件记录来源图号/region/version/SHA/完整单栋像素box/选择理由到自己references子目录；不把整张邻图作为生图构图/机位输入，不把裁片放大冒充原生。可读25区district-identities.json辅助，但必须看图不靠名字。
固定几何参考revision-003/road-constraint.json，当前frontage屏幕-28.486deg、depth+55.406deg，墙体竖直，不转/镜像/拉斜旧PNG。几何脚本可读revision-005/references/make_references.py和guides.json，在自己目录做新体量辅助图。候选尺寸非用户硬限/源实测。画风参考docs/art/2026-11-03-whole-region-map/references/2026-11-03-user-building-variety.png，已认可五楼只用于机位/光照收尾，不复制浅墙玻璃配方。自然日光，无黄洗/整图蓝染/亮窗/屋顶树/文字logo。
每个指定ID真正用当前内置image_gen原生生成一次；在本Agent内按顺序，第一件原生和来源先保存再做第二件。跨Agent并行已授权。每件最多一次，不额外扩量/重试；网络/工具阻塞如实报，不用空等文字冒充提交，不启外部付费API/浏览器生图或程序盒子代替原生。
每件交付OWN/ID-v1.png原生逐字节副本、provenance.json（真实tool源绝对路径/完整实际prompt/参考SHA/实际尺寸modealpha/源副本SHA/候选状态）、ID-runtime-280.png及.runtime.json、短REPORT.md。原生母版不进包。运行导出可直接执行只读工具：
python3 docs/art/2026-11-05-modular-map-kit/revision-005/runtime-size-pilot/export_runtime.py --output-dir OWN --max-edge 280 --single-source OWN/ID-v1.png --single-target OWN/ID-runtime-280.png
实际打开图检查主体/透明边/机位/差异，估读地基/接地点需注明不精密，不称用户验收/地图完成。final简短中文给真实绝对路径/尺寸字节/缺陷/阻塞，parent auto收，不重复发信。

本角色是原生资产制作：下述两件必须生图并导出280运行图，不是仅规划或选型。
唯一新写集：revision-006/references/industry/、native/B10-001/、native/B11-001/。产B10、B11。
B10选低层工坊/仓储原型，连跨/锯齿/坡顶或其他工业屋顶及金属/砖等实际实体材料；B11选小车库/服务楼/作坊，宽门洞、附属体量和功能开口与B10不同，不是白玻璃平盒改名。未知背面和功能写候选推断，不虚称源事实。不要整厂地块/路/车/烟雾；保留既有B05和选框。
所有相对目录前缀为 docs/art/2026-11-05-modular-map-kit/。不得写其他角色目录。
