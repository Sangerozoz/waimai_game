# 活动订单面板贴边与地图控件对齐

已查看三张参考图。状态：已实现，未测试，待阶段集中测试及用户体验验收。

定位图通过现有icon加载入口使用与站点相同86.4设计单位适配框，保留独立且不少于116设计单位的定位热区。监听两张图片的SIZE_CHANGED及ACTIVE_CHANGED，根据已加载图框实际高度、站点图中心偏移计算定位图中心，使主体底边对齐；图片未加载时沿用占位几何。左右安全区加默认16 CSS px仍保留，规划阶段隐藏两控件。

活动订单DeliverySheet背景居中铺满720设计单位，sheetBottom抵消OrderPanel底部安全区偏移，使背景到屏幕底。底部用矩形填平圆角，上缘保留圆角；结算等其他弹窗不变。新SheetContent按左右安全区和16 CSS px限定宽度及中心；订单标题、信息、路线和按钮均在该容器内。底部按钮底缘为屏幕底部加安全区和24 CSS px，滚动区域为按钮和间隔预留空间；sheetHeight把同一安全区及按钮额外留白计入，地图高度、控件位置沿原sheetBottom+sheetHeight几何联动，避免重复安全区偏移。

保留各阶段按钮分支、取餐进度、卡底加速、取消、done全图、结算双按钮及现有素材。只修改MapSample.ts，before、changes.patch、source-sha.json和build-manifest.json记录真实改前、增量与最终构建文件SHA。

一次必要构建17:39:23 Finished、包装退出0；原build.log包含build-script SIGTERM诊断，不推断各原子进程均正常。4181静态HTTP 200，本地index SHA一致。未运行测试、typecheck、回归或渲染；未操作用户页面或存档，未commit/push。安全区机型、短屏、图像加载与视觉对齐尚未验证。
