# 三维街角样板实施计划

> 使用现有PM/固定开发与有边界的资产子任务执行；遵从用户持续推进和阶段结束才集中测试的要求，不新建worktree，不提交或清理现有改动。

**Goal:** 交付可运行的原坐标三维街角小样，使用户能直接判断建筑/街面的制作能力。

**Architecture:** 独立声明式三维场景资产由美术任务制作；固定开发将其转换为Cocos静态网格/材质，设置固定相机和光照。独立场景、独立构建，保留正式游戏和Canvas历史。

**Tech Stack:** Cocos Creator 3.8.8、TypeScript、静态JSON资产、本机4181静态服务。

## Global Constraints

输入与精确接口见同日spec；只读city.json。保留全部未提交工作。不操作正式游戏/存档，不运行测试/typecheck/截图矩阵。用户本轮要求实际展示，交付允许生成隔离美术样板的运行画面；必要构建与画面展示不等于验收。已确认风格与范围不重问。

### Task 1 资产生产（独立子任务）

- [x] 读取原图/源地图，选原样板内一处路口及三栋相邻原建筑，记录原始坐标与来源SHA。
- [x] 写 scene-design.json 与可重复生成的 build-scene-assets.py，仅该美术目录；三栋建筑必须有独立体量/首层设计，加入连续街面/道具/尺度参照。
- [x] 运行资产生成，检查JSON/三角形/有限数/引用材质等静态数据完整性，写README与manifest；不渲染、不运行游戏。

### Task 2 Cocos显示与独立构建（固定开发）

- [x] 为隔离主工程引擎配置，在 delivery-game/street-corner-3d-project/assets/scripts/StreetCorner.ts 内建立JSON→静态合并网格/材质转换，按材质合并避免大量独立draw call；建立独立scene及资源。
- [x] 使用真实三维mesh、深度、固定斜俯视正交相机、主光/环境光/阴影；大小和取景以主资产camera为起点。补最少载入反馈和缩放/复位。
- [x] 创建独立build配置和脚本，构建到 delivery-game/build/map-sample/street-corner-3d/，不覆盖正式入口。旧county-sample提供进入新样板链接并同步静态副本。
- [x] 以构建日志与静态产物写 docs/reviews/street-corner-3d-20261103/implementation-report.md，注明未游戏测试/未视觉验收。

### Task 3 PM交付

- [x] 检查两个任务产出与输入合同、原图归档和source SHA；隔离样板首次载入报错修复后已显示，engine-v1.jpg为真实运行画面。根据可见画面完成一轮材质/光照收口，非画风已验收。
- [x] 更新长期入口/交接到新样板真实状态；已显示实际新版场景并保存engine-v2.jpg，提供可点击入口。美术未达到认可概念，不扩全县。详见PM交付记录。
