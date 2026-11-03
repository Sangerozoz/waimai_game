# 三色路线、卡内加速和结算背景

状态：已实现，未测试，待阶段集中测试；用户体验未验收。三张任务参考图均已查看。

- 地图及路线卡标题共用 ROUTE_COLORS：fast 蓝、main 黄、smooth 绿。每条备选保其颜色，选中路线最后绘制、7.5 CSS px及浅色外沿，备选4 CSS px；卡片选中边框使用对应色。
- 将现有 ClickBoost 节点创建到 DeliverySheet 底部主按钮位置，复用原触摸单指、移动、多指取消、时间限流与平滑加速逻辑。仅支持的新profile实际移动阶段创建，其他旧profile仍显示原禁用状态；取餐/服务/去配送分支保留。原地图浮动入口删除。
- 屏幕根节点的暖白底黑字“配送中”固定在顶栏下方，toDropoff running显示，刷新阶段后隐藏，不随地图移动。
- done视为全屏地图布局，地图 viewport/ground 不再预留订单卡空间。完成结算保存后根据布局状态重建，旧路线、取送卡和加速控件不再创建，车辆继续取当前终点；业务active和receipt保留。保存失败时也重建但由pending冻结，重试成功才显示回执。布局重建的done标记避免递归。
- 结算关闭、遮罩和“确认，返回首页”均经finish及保存后回首页，确认不再自动打开大厅；保存失败继续冻结并等待重试。

交付：before/是真实修改前副本，changes.patch和source-sha.json记录增量及SHA；build-manifest.json记录最终构建JS与静态入口SHA。未更改存档、业务参数或素材，未commit/push。

构建：第一次构建因加速控件参数与原触摸坐标重名解析失败，退出34，原日志保存在build-failed.log；修正命名后最终构建16:55:10显示Finished，包装退出0。最终日志还保留Cocos编辑器layout.json、window.json解析错误和build-script SIGTERM诊断；包装成功不能表明所有原子进程正常。4181静态HTTP 200，index与本地SHA一致。未运行测试、typecheck、回归、渲染或独立复验，未操作用户页面或存档。构建和静态可用不代表阶段测试通过。
