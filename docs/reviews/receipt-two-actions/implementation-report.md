# 结算双按钮

状态：已实现，未测试，待阶段集中测试及用户体验验收。

结算弹窗上方为金橙“继续接单”，下方为深棕次按钮“返回首页”；保持正常触摸尺寸、16 CSS px外边距与金额单行。请求高度及可滚动内容底界为两个按钮和间隔预留空间。全屏地图背景和无订单底卡保持。

按钮及X/遮罩共用finishReceipt：只在done且非冻结时执行一次finish和save，成功后返回首页或打开大厅。失败时原弹窗留在屏幕、pendingSave冻结，保留所选去向；自动重试保存成功后才恢复布局并按选择打开大厅或首页，不重复执行finish或发放收益。失败期间其他结算点击被拦截。

本轮仅修改MapSample.ts；before、changes.patch及source-sha.json记录真实改前及增量；build-manifest.json记录最终构建文件SHA和4181入口响应。

一次必要构建17:14:01 Finished、包装退出0；原始build.log记录build-script SIGTERM诊断，包装成功不代表各子进程均无异常。4181静态HTTP 200且index SHA一致。未进行测试、typecheck、回归或渲染核验；未操作用户游戏/存档，未commit/push。
