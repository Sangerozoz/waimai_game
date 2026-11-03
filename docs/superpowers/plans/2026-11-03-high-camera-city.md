# 高斜俯视完整地块样板 Implementation Plan

> **For agentic workers:** Use executing-plans task-by-task in the existing checkout. 用户已指定固定PM/开发与禁止过程测试，覆盖技能默认worktree、TDD、commit和再次征询执行方式。

**Goal:** 原路不动，用完整地块美术与独立大骑手交付 `/high-camera-city/`。

**Architecture:** PM生产两块带统一投影底稿的透明整景和两方向骑手，开发使用同一62.5°正交投影绘原路/铺装、放整景、更新动态骑手；独立Cocos2D入口保留旧展示。

**Tech Stack:** 既有Cocos Creator、TypeScript、内置image_gen、JSON；docs内几何底稿生成工具仅用于美术结构，不成为运行时程序建筑。

## Global Constraints

- 规格：`../specs/2026-11-03-high-camera-city-design.md`；保留所有dirty/untracked、原路/边界/业务/存档。
- 62.5°对地面俯角、45°方位；6–10m退距，低楼；少量穿帮容忍，不预建全图像素级遮挡。
- 不tests/typecheck/回归/渲染矩阵；必要独立构建/部署和HTTP允许。禁止绕过浏览器禁用设置。
- PM写docs，固定开发写delivery-game。不新建worktree/聊天；不commit/push/发布。

### Task 1: 原坐标结构包与原生美术（PM）

Files: `docs/art/2026-11-03-high-camera-city/{scene-layout.json,asset-manifest.json,generation-records.json,prompts/,guides/,metadata/}`。

- [x] 从旧sample-layout原样引用三路，计算主路局部单位切向/法向、两地块与四楼候选几何；生成共同投影的地面/楼体线框底稿，仅生产参考。
- [x] image_gen各生成一块完整原生透明地块，保留几何关系、绘画丰富细节；保存原图、prompt、源、SHA。实读地面角点/入口，记录误差，不依据prompt冒称标定通过。
- [x] 原生生产高机位D骑手NE/SW，保留橙头盔/衣/箱和圆灯；实读轮点/opaqueBounds。
- [x] 输出 manifest：id/file/nativeSize/sha256/anchorUV/anchorMap/nativePixelsPerUnit/controlPoints/observations；骑手含opaqueBoundsUV/wheelContactAnchorUV/direction。统一缩放只用地面对应点，禁拉伸。

### Task 2: 独立显示与动态骑手（固定开发）

Files: `delivery-game/high-camera-city-project/`、必要独立build脚本、`docs/reviews/high-camera-20261103/implementation-report.md`（开发负责该报告）。输入 Task1 场景/manifest，实施时可先搭加载接口，正式美术缺失时不交付占位图版本。

- [x] 复用既有小样Cocos设施建隔离项目，新增唯一 `projectMap(x,y,z=0)` 使用规格正交基。原道路完整数据只读，显示裁切不改路。
- [x] 原道路沥青/边线/人行道与地块前缘连接；整块美术保持原生比例按anchor和统一像素比例落地，不用程序盒体替代。
- [x] 骑手地图坐标沿原路线插值、方向帧NE/SW、轮点接地影；参考720宽可见轮廓至少旧两倍。相机取景独立配置，允许拖动/缩放但无旋转。
- [x] 保留旧所有入口，部署 `/high-camera-city/`，不覆盖 `/modular-city/`。必要Cocos构建，记录真实退出/Finished与诊断；不附带测试。

### Task 3: 交付与接续（PM）

- [x] 核实际归档/构建/部署证据与HTTP可达；不是页面渲染/游戏测试，无浏览器权限则如实记录。
- [x] 长期基准/current交接与交付报告写真实状态、来源、局部透视/两方向演示限制；展示新入口及实际原生美术给用户。未代填用户验收。

实际交付见docs/team/reports/2026-11-03-high-camera-city-pm-delivery.md。完成勾选指本轮源码/素材/独立部署与证据整理，不代表游戏测试、运行视觉验收或整县完成。
