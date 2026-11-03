# High Camera City R2 Implementation Plan

**已停止：** 用户要求完整多街区区域一次生成后拼接，覆盖本小地块扩展计划。3张原生候选留档、R2未集成/构建/部署；不得自动恢复。改用whole-region-map-design与同名区域计划。

> **For agentic workers:** 按executing-plans在当前checkout逐项执行，复用固定PM/开发；用户禁止过程测试、worktree和commit，覆盖技能默认流程。

**Goal:** 稍高主景楼与四地块连续街段，部署到原隔离入口。

**Architecture:** 两张增高R2整地块＋一张窄街角新图＋一张已认可v1东地块复用＋原两骑手；同一投影、同一原路线段、完整原道路。PM只产docs美术/布局，固定开发写delivery-game并集成/构建。

**Tech Stack:** 现有Cocos2D/TypeScript、内置image_gen、JSON。

## Global Constraints

遵守同日high-camera-city-r2-design规格。保留v1源图/确认/部署备份和所有dirty/untracked；不游戏测试/typecheck/回归/渲染矩阵/页面自动操作/存档/commit/push/发布。不得用2D变形代替新楼高机位图。

### Task1 PM生产

- [ ] 两原图原生增加一层，保持原地面/入口，归档完整prompt/源/SHA/alpha。
- [ ] 从原源路几何核定南侧两个候选地块，东侧沿路南移26m，西侧按12m窄地块原生作一栋4层街角，保留原三路并补显示原149396705-0支路与priorRoute；新示范路仍在原直线段上。
- [ ] 新图实读控制点/门点，统一缩放/平移求落点；原生v1/骑手按原字节复用，交付六资产manifest/四地块layout。

### Task2 固定开发实施

- [ ] high-camera-city加载支持4完整地块，其他已满意效果保持；地块间按布局做克制步行过渡。
- [ ] 完整备份当前high-camera-city与源码/数据，准备R2运行包，原modular/县城/3D入口不动。
- [ ] 必要独立构建并部署原high-camera-city，记录实际退出/Finished/诊断、source/runtime/deployed SHA与HTTP；不宣称实际看见新运行画面。

### Task3 PM交付

- [ ] 核已保存新图和真实集成/构建/部署证据，更新长期基准/current交接/交付报告；未用户验收与未阶段测试分开记录。
