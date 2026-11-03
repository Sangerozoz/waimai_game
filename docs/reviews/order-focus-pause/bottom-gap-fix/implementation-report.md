# 活动单底部空白最小修复

**已实现，未测试，待阶段集中测试。** 依据用户实际反馈实施；仅修改MapSample.ts布局定位，无业务、M2底座、存档或资源修改。

根因：上一版隐藏navigation时没有同步去掉订单卡的导航预留。sheetBottom()仍以-479.4为底边，地图baseMapHeight还直接重复这个旧常数，因此卡片下仍留着原底栏/中央圆钮空间。

本次增加共享sheetBottomFor(screenHeight)：活动单改为-640+cssUnits(12,screenHeight)，无活动仍沿原底栏布局。订单面板本身已经应用-screenExtra/2和bottom安全区偏移，因此最终活动卡底边为-屏幕设计高/2+底部安全区+12 CSS像素，不重复计算安全区。地图预估baseMapHeight改为同一helper；实际mapHeight/mapY、站点和定位控件原本经sheetBottom()取得位置，现在自动跟随新底边。sheetHeight、内容滚动、金额布局、结算、暂停与不可收卡逻辑未改。取消/结算清理后无活动，原首页navigation分支恢复。

按最新测试节奏，本轮未运行测试、typecheck、回归、浏览器/渲染复验；上述为代码实施说明，不是视觉/体验验证通过。未操作用户4181游戏或存档，未commit/push。

before/、before-sha.json为本轮改前范围，production.patch记录最小差异，final-source-sha.json与build-manifest.json记录最终指纹。build.log及delivery.json记录交付构建结果，static-http.json仅记录静态服务HTTP，不运行游戏。

实际构建命令`npm run build:map --prefix delivery-game`包装退出0，日志13:55:40 Finished；产物为delivery-game/build/map-sample。4181静态首页HTTP200，响应index与本构建SHA一致。
