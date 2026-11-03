# PM与开发迁移：当前事实快照（2026-11-03）

用户本轮明确要求PM与开发分别新开会话，并先在旧PM对话重新发送产品方案和效果图。资料已先发；迁移仅同一checkout接续，不fork/读旧长聊天、不创建worktree、不清理dirty、不触发测试/构建/存档/发行。新角色ID见docs/team/reports/2026-11-03-pm-development-migration.md与docs/team/README.md最新登记。

## 必须保留的产品/视觉依据

- 固定读入口 docs/product/implementation-baseline.md；正式玩法 docs/product/2026-11-02-delivery-game-product-v1.md；参数 docs/balance/2026-11-02-product-v1/parameters.json（首版配置未实测）；开发范围 docs/product/2026-11-02-delivery-game-development-handoff.md。
- 已认可8张原生UI图 docs/art/2026-11-02-approved-ui-reference/README.md，approval.json的8个SHA本次复核一致。六页＋车辆锁定/滚动。用户便捷查看入口 docs/product/2026-11-03-product-visual-review-index.md。不能恢复历史待审/拒绝图。
- 明亮都市动漫厚涂，蓝白UI不继续变蓝，橙色主按钮，屋顶无树，少量地面绿植。骑手约31人两三屏、车辆上预览下滚动宫格、订单无分页/无已选tab、账单不分今日累计、地图五张独立卡。完整HUD仅首页，其余顶部按用途精简；详见冻结图与revision-requirements-at-approval.md。
- 地图用户红/蓝/绿三界 docs/art/2026-11-02-county-zoning/selection.json：红外景显示边界，蓝街区与全程配送，绿繁华核心；蓝到绿郊区，红到蓝山林绿地，无经营。棕框忽略。建设区不能大片空地/空铺装，也不能只涂草色；建筑更多、绿量受控。

## 当前实际地图制作方向

用户拒绝Canvas通用盒子/重复窗格外观，试做真实3D后仍认为效果/成本不理想，主动提出生图完整独立素材如积木搭城；PM说明后用户明确“那我们开始吧”。当前采用完整图片Sprite＋独立路网，不继续扩3D或旧Canvas盒子。Kenney例图只说明素材组合形式，非采用其低模风格。

- 现样板 http://127.0.0.1:4181/modular-city/ 已由旧PM实际打开显示，真实截图 docs/art/2026-11-03-modular-city-assets/engine-v3.jpg。不是AI整景冒充运行。仅隔离美术展示，正式游戏/存档未操作；本机服务根 delivery-game/build/map-sample/，进程是否仍监听需按需确认，不运行正式游戏。
- 资源 docs/art/2026-11-03-modular-city-assets/README.md，8件新增候选（3楼/2树/路灯/2地面材质）＋字节复用D骑手NE帧；12张生图输出含历史/拒绝/修订，prompt/原生PNG/尺寸/SHA在generation-records.json与asset-manifest.json。
- 用户指出树T02v1正视错误；该图已明确拒绝且禁止接入，旧HT01也不复用。T02v2重生紧凑顶部树冠/短干，T03为第二树形。B02/B03另存机位v2，不覆盖旧图。B02仍有小幅推算机位残差，不能称全部精确统一。
- 原坐标sample-layout.json：3种楼共8实例、7树6灯，背景67×72m；默认西侧沿街近景，路在前景，边楼可出画面，不为看全缩成沙盘。原楼143/144/145等是地块参考，新素材不硬拉原多边形；原city.json未改。
- manifest SHA d914d743664cb28ac45941509191256e803e7f9f56d2dd1d264e70cdf54faf05；layout SHA a190dd06c3f95aa244c9a759ed13d5d6d3b88a91539eb3e2c7af750d5e07aac6。源city.json SHA536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20。
- 独立工程 delivery-game/modular-city-project/（Cocos3.8.8），脚本 assets/scripts/ModularCity.ts，构建 delivery-game/scripts/build-modular-city.sh，产物 delivery-game/build/map-sample/modular-city/。不覆盖主游戏入口。
- 工程报告 docs/reviews/modular-city-20261103/implementation-report.md；PM汇总 docs/team/reports/2026-11-03-modular-city-pm-delivery.md；方案/plan为 docs/superpowers/specs/2026-11-03-modular-city-sprite-design.md 与 docs/superpowers/plans/2026-11-03-modular-city-sprite.md。

## 真实未完成与下一步

已实际显示首批方法样板，尚未用户美术验收，非完整县城；B02透视残差、整张图片脚点排序无法处理所有细粒度遮挡、骑手仅单NE帧往返、背景重复与街景细节待完善。局部简化阴影不是3D真实投影。先保持已交版本，收集/处理下一条具体用户反馈，后续在既定目标内自主拆解；不要未经质量收口便把候选铺全县。

原游戏正式V1尚未全量实施，不因美术小样显示宣称玩法完成。全县蓝框边缘路网封闭/动态地址重筛仍未落实；旧county-sample与street-corner-3d及资料全部保留作历史，不恢复为当前生产方案。

## 约束

用户说“阶段完成”才组织集中游戏测试。过程不自动tests/typecheck/回归/渲染矩阵，不操作正式游戏或存档。必要交付构建和用户明确要求的隔离美术展示可做，不代填用户验收。保留全部已有未提交/untracked，不reset/clean/自动commit/push/发布。只改用户提到的范围，不顺手重构产品或经济参数。

角色可按任务需要有界拆分/选模型，避免无意义多角色；PM统筹产品/素材/文档/派工，固定开发单写业务代码与集成。没有需要用户决策的真实问题就持续推进，不反复追问已确认方向。本次新会话启动仅阅读交接、简短确认接任，不自启动新生图/代码/构建/测试，旧PM完成登记后再承接用户下一条指令。
