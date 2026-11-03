# Whole Region Map Implementation Plan

> **For agentic workers:** 按executing-plans在原checkout推进，复用固定PM/开发；用户明确不过程测试、不开worktree、不commit。

**Goal:** 先交一次生成的120×120m完整区域A，作为区域拼接生产线的首片。

**Architecture:** 原路网及20楼参考只作为整体结构底稿；内置image_gen一次绘制完整区域。独立动态骑手保留，后续按区域接缝和实际路网控制点接入，不逐栋出图摆放。

**Tech Stack:** 现有地图JSON、docs内几何底稿工具、内置image_gen；后续引擎复用Cocos2D。

## Global Constraints

同日whole-region-map-design规格与用户whole-area-production-confirmation为准。保所有dirty/untracked/原街角/源路/存档。禁止过程tests/typecheck/回归/渲染矩阵/页面自动化/commit/push/发布。

- [x] 原地图提取整区范围、完整道路引用、源建筑足迹参考和路口/边缘控制点，生成单张统一相机结构底稿。
- [x] 一次image_gen绘制A全区域，保存原生图/alpha或RGB模式/源/全prompt/参考SHA；不以零件组合冒充整区。
- [x] 实读整体密度/道路/机位与明显偏差，记录候选状态，区域B后续按同尺度/源路接头/A边缘制作。
- [x] 更新基准/交接，向用户展示首片正确粒度的原生整区图；不冒称已与B拼接、与原路精确配准或已替换引擎。

首片A原生候选已交，来源见docs/art/2026-11-03-whole-region-map/generation-record.json。勾选仅代表本计划首片生产/观察与归档，不代表相邻B/无缝拼接/配准/引擎/游戏测试完成。
