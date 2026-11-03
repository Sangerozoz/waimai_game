# 默认外边距 16 CSS px 实现交付（2026-10-30）

状态：已实现，未测试，待用户宣布阶段完成后的集中测试；用户体验未验收。

## 实现范围

- `PresentationLayout.ts` 提供 `DEFAULT_PAGE_MARGIN_CSS=16` / `pageMargin(screenHeight)`，沿已有 SHOW_ALL 的 `cssUnits` 换算。安全区仍由各布局先扣除，再追加默认外边距。
- `MapSample.ts` 的 `outerMargin()` 统一顶栏左右、顶部头像可见范围、活动订单卡左右与底部、提示条左右、站点/定位控件左右、底栏内容水平边界；背景继续铺满。
- 暂停按钮仍为完整节点 0.5 缩放，原白色原生Ⅱ、热区、显示阶段与交互不变。其本地 x 取 `-avatarWidth/2 + 原按钮宽度/4`，抵消头像中心定位，使缩放后完整底板左缘与安全区内侧加16 CSS px对齐。
- 大厅手机框与公共弹窗使用共享边距约束左右和上下可用范围；保留 684 / 1240 等 maxWidth/maxHeight，因此大屏可能自然产生更大留白。弹窗内容宽度派生同步更新。
- 活动订单卡高度估算及进度条几何随新卡宽度同步。`CityMap.setHeaderClearance()` 使用头部/暂停底缘到地图视口顶缘的实际几何更新路线取景顶部避让；卡片上缘仍决定地图视口下缘。15m默认、手动缩放、总览fit算法、比例尺与署名节点保持。

## 有意保留

卡片内部40/48宽度扣除、16/24 padding、按钮gap、标题/字号、固定宽高、头像内部原图透明边补偿、暂停纵向gap、导航项目位置与主按钮尺寸、地图底部控件避让及署名/比例尺内部几何均保留。手机外观侧键/阴影保留；默认边距约束以主框为基准，装饰投影可能伸出主框。

只改四个展示层源码；40时钟、指数加速、取消、结算回执/清卡业务与素材未改。

## 构建与交付证据

执行 `npm run build:map --prefix delivery-game`，输出 `delivery-game/build/map-sample`。最终构建于16:09:06显示 Finished，包装退出码0；不能据此声称所有原子进程无异常。本轮共构建两次：第一次后修正高度预估使用传入screenHeight的边距换算，再执行最终构建。日志保留 Cocos 自身的 SIGTERM 诊断。

4181仅静态HTTP取文件，未打开或操作用户页面/存档。`build-manifest.json` 保存本地index与4181响应SHA及构建JS清单；最终HTTP 200，index SHA一致。

改前真实文件在 `before/`，逐文件前后SHA在 `source-sha.json`，仅本轮改动补丁在 `changes.patch`。HEAD未充当改前基线。未commit/push，保留现有未提交/untracked。

未运行测试、typecheck、回归、渲染或独立复验。构建与静态HTTP交付不代表阶段测试通过。
