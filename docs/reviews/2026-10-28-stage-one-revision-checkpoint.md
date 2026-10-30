# 第一阶段修订接续点

用户已批准全部六组修改，并确认30分钟=10秒、封顶15秒、D+200元、首个经验升级5单。当前最后用户表示浏览器设置已开启，可能重启软件；不要重复设计或清档。原验收17通过3失败4未测保留。

当前执行计划 docs/superpowers/plans/2026-10-28-stage-one-revision.md；规格同名-design.md，SDD ledger .superpowers/sdd/2026-10-28-stage-one-revision/progress.md。使用当前codex/food-delivery目录，既有源码多未跟踪，用ZIP差异，不git reset/clean/stage/commit无关内容。

Task1已完成：CountyConfig D12km/h、D+13.2、200元，50XP首次Lv2；新clock道路米/速度，10秒/15秒；v3 snapshot兼容旧v1/v2，active.ruleVersion旧1新2，历史时钟/结果冻结、当前等级重算、running/paused加载自动继续；取消手动暂停。40地图+18存储检查、类型通过，独立revision_rules_review规格/质量均PASS。报告/差异/Task1结束快照在SDD目录，公开副本docs/reviews/stage-one-revision。

Task2正在revision_city_content子代理实现，brief已在task-2-brief.md。范围CityExtent、PlaceCatalog、FoodCatalog、CityMap、OrderBook和必要Snapshot/MapSample接线。主城区密集核心锚定首餐厅，x[-4200,-900]y[-900,600]1013建筑；拟核心含接近城区y[-1200,900]，10%扩展最终[-4530,-570,-1410,1110]。至少40城区餐厅、120顾客、16餐品、无重复地址；新路线在bounds且≤10km，旧外城连续履约不瞬移，必要时兼容外城派单直至可合法回城。必须旧mapId可信别名兼容，旧POI索引不改。Task1-end-snapshot.zip是Task2差异基线。Task2完成后独立审查再Task3。

餐图已生成并保存delivery-game/assets/resources/map-sample/food-atlas-v1.png，1254×1254，4×4左上row-major：鸡腿饭/牛肉饭/红烧肉饭/麻婆豆腐饭，鲜汤面/拌面/馄饨/小火锅，饺子/包子/披萨/汉堡，沙拉/寿司/蛋糕/奶茶。本地图集2.7MB；来源docs/reviews/stage-one-revision/food-art-source.json。未接Sprite，Task3做FoodImages裁格+OrderPhone精简+自动结算弹窗，brief已生成。

根任务已准备新24项验收草稿（独立storagekey，入口拟4189，不覆盖旧4188记录），在SDD/acceptance-revision-draft.html及cases.json，尚未写正式source/build。Task4最终集成时复制到acceptance-revision/index.html，build脚本增加复制；旧acceptance/index.html保留旧结果。新规则重点复验A03/A06/A08–11/A17–18。原用户报告副本docs/reviews/stage-one-revision/user-feedback-original.md。

浏览器：当前CUA重新出现Local browser use is disabled in Work settings，已停止浏览器操作，无绕过。用户已回复开启可能需要重启；待重启后仅用CUA恢复权限再最终UI验证。未成功读取当前用户存档（user-save-before-revision.json未产生）。不要把拒绝当成功。上一轮CUA handles handoffGame tab5 localhost4188、handoffForm tab6 /acceptance、handoffCdp、qaFs，浏览器IAB id3；重启会失效，需要重新列tabs。原正式服务4179PID82565、4188PID90698重启后读lsof核对。别碰无关Chrome。最终QA用独立4181，不注入/清空用户存档。最终新用户4189留新档，不做rootQA在那里。

恢复点 .merge-backups/2026-10-28/stage-one-revision-base.zip（修改前145文件）及此前stage-one-acceptance-v1.zip；原受保护SHA Main.scene4b243a4bfdd6f6cdaf5db358c0405dd9ea4b971351028bee1b3aee84eb368166、旧DeliverySession a2ba218af00e1075cec9b9cf63528e09dcfbe6f56b8e19441dce0f9f6aac6f1c，GameConfig1cb5be314ec1f8bb7373d55f3169b596b6fa493c26d49b9fa6da49f7bf59468e。

接续完成Task2→review→Task3→review→Task4全套tests/typecheck/build+真实UI5单升级/200元购车/图片与滚动/地图各边/自动结算/后台与重载/旧档兼容/longscreen，保存新恢复ZIP与哈希、更新master/README、交用户复验。不进入第二阶段。

接续更新：Task2已完成并SPEC/QUALITY双PASS；实际总272地点（新增144），城区40商家/120顾客，3批10单均10商家/10餐品/10目的地。完整100tests/typecheck0，task-2-end-snapshot.zip为Task3baseline。Task3由revision_ui正在实现（brief/task-3-report.md）。根任务已将新24项复验草稿正式保存到delivery-game/acceptance-revision/index.html、docs/acceptance/2026-10-28-stage-one-revision.md，并在build脚本增加复制新页；旧验收页和旧存储键不改。新页JS语法已通过。等待Task3→review→build/QA。
