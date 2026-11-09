# 009 批次数据准备交付

已执行真实008输入转换、差分去重、共享PNG打包、tile联合索引、可见缓存窗口计划及静态校核。本轮只示范未新渲染，主图新增0；57实例/115地面/现有镜头/D内存路径全部保留。

- 入口：batch_prepare.py、schema.json、README.md、budget-policy.json。
- 实际包：staging/demo-008-core（13件/17面/23条源路），staging/demo-b07-wide（1件/13面/1条源路）。全为已存在ID，新增0/0/0，拒绝0；两包increment.tmj为空新增层，是正确零差分，不是素材占位。
- 共享图：staging/shared-assets，11张，879,180字节，全部长边<=280。无原生母版、25图、全城分析快照，无新引擎工程。
- 原始父批准SHA与派生转换/差分SHA分开记在各prepare-report/difference；详情及实际命令见 execution-prepare.json 与README。
- 静态原路基线25条/178节点已逐值核源city节点顺序/宽度/方向，投影完全相等；门点按真实原像素/PPU换算，B07门11正确；V02车身在原车位polygon内。门导航/隐藏脚线与新视觉不在此次验证范围。
- verification-results.json：两个audit退出0；9个静态门禁（重复batch/index、错误父SHA、镜像、旋转、非等比、hold、缺失素材、改路宽）均拒绝。没有游戏测试/typecheck/回归。
- source-protection-final.json：193个保护文件SHA保持，changed=[]；其中006全目录与固定008/原city共186件，加实际读到的原生/工具/schema/预算等输入。原生 sourceSHA 在各包的真实原图读取检查中匹配。

稳定源：

- 006 scene SHA256 `8035f4da47817a2d1361021f3e6c385fb3c058711390c4ea857b84ee8d6be020`
- 006 TMJ SHA256 `52f26ed58b6acf33967e6b824e2666a56ad1179f744bc3d3eeedc3ab49a852bf`
- 原city SHA256 `536e3347d1ed6e512727426ee646412c1d553e061869257f615b975827220d20`
- 核心原规划 `a5412d65a4a9149051f98f43026b8d9e00d4b2e111d3c9366b998a2e4f230758`
- B07原规划 `5e5c40725da225cb5fa45c129c0ab04951f76a9f562d519911f8acc44922fa76`
- 准备器 SHA256 `ecd15513fcfb82f820a472d850d542449392052f17e08479f7c4e8878ad32d92`

分块输出：staging/batch-index.json共6个候选tile，仅覆盖这两份已存在示范子集；cache-core/wide输出实际load/evict引用与共享素材key。建议64m tile、2m halo、最多8resident（含2预取）、地面<=8,388,608像素/单边<=1536；core示范6resident=7,090,176像素，wide4resident=4,726,784像素并给2个evict。此为准备预算，不是实测内存/FPS；现有006三画布机制未改变。真实扩量仍需在同006引擎实现按可见tile挂载与释放，不能将所有分块常驻或烘成县级巨图。

当前无准备阶段阻塞。待父明确批准新009稳定输入SHA后再生成真实新批差分，并获准接入同一006；本轮未消费009在途规划、未新增显示/截图、未声称新街区或用户验收完成。B09/B10/B11仍hold，有限比较资产的上下文门禁不因导出而解除。
