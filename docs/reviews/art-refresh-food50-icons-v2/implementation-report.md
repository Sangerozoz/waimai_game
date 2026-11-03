# AU04 50食品及 AU05 v2 图标接入

状态：资源和代码已接入构建，未测试，待阶段集中测试和用户体验验收。

五批原图按 current-batches.json 指定顺序复制到 resources/map-sample/anime/au04，原件未改。CartoonArt 的 foodKeys 扩展到0–49，每个键均指向对应批次源及按图片主体、器皿范围取的 SpriteFrame 矩形。FoodImages 的现有入口因此覆盖50个 FoodCatalog index，不改食品ID、名称、权重、存档或业务数值。food50-mapping.json 列出逐条ID、index、原件、resource路径和像素裁框；原 intake 清单的旧“未接入”状态为历史记录，接入状态以本报告为准。

AU05 v2 复制原件并按新版构图重设招募、外卖袋、定位、确认、关闭、暂停六个矩形（icon-crops.json）。现有实际入口招募、定位、公共关闭引用对应新版；招募仍禁用。bag/confirm为库存；pause仅更新库存资源键，屏幕暂停继续使用清楚的原生白Ⅱ。原AU05图片保留。

取框只限定矩形，不修改源像素。五批原图边缘红黄灰杂点仍可残留，近主体的噪色无法靠矩形完全去除；新版图标存在深色半透明氛围背景，矩形裁切也可能带入。第四批虾饺格外形偏小笼包，仍按用户交付与既有目录标为虾饺，不改业务名称或图像；需后续独立处理或体验确认。本次没有声称边缘已净化。

source-sha.json逐件列原件和导入件SHA，六对一致；before/和changes.patch记录真实改前源码和本轮增量。构建生成的Cocos .meta保留。最终build-manifest.json记录全部构建文件SHA和静态入口响应。

一次必要构建 npm run build:map --prefix delivery-game：17:04:23 Finished，包装退出0；日志保留sud状态检查网络TLS错误及build-script SIGTERM原始诊断，包装结果不代表所有原子进程无异常。4181静态HTTP 200，本地index与响应SHA一致。未运行测试、typecheck、渲染或回归；未操作用户游戏页面或存档，未commit/push。
