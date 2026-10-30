# 多个按钮首次点击无效修复

2026-10-28，用户反馈多个按钮经常需要点击两次。没有操作页面，使用实际SampleUI.tap的输入事件序列复现。

## 已确认的共用原因

原tap把任意TOUCH_MOVE直接标记为拖动。按下→移动1个UI像素→松开时，实际action调用0次；零距离移动事件同样丢弃点击。原按下还把根节点缩为0.98，本机Cocos的NodeEventProcessor在释放时重新对当前UITransform做hitTest，因而按钮边缘的首次点击可能变成TOUCH_CANCEL。

另检查列表路径：本机Cocos3.8.8的ScrollView在捕获阶段按UI坐标距起点>7判断拖动，并携带同一touch派发模拟CANCEL；End随后会被滚动视图截断。本轮沿用引擎阈值，不禁用列表取消机制，不阻止触摸传播。

## 修复

SampleUI.tap以距按下起点的最大移动量区分点击和拖动，≤7个UI像素可正常点击，不再缩放命中节点。仅当前触点能结束此次按压；取消即清理，触点ID0有效。释放时先解除按压再调用action，重复End不重复执行；无Start的End不触发，遗漏Release后的同ID新Start可以恢复。

所有由共用button/tap创建的抢单、订单、路线、出发、交付、回执及车辆按钮均使用该逻辑。列表实际滑动依然取消点击，不会为了单击灵敏而误接订单。

## 验证

- `node --test tests/tap-gestures.test.cjs`修前9例中8失败、1通过：[失败日志](button-taps/red.log)。修后共11例通过，覆盖1px/零距离抖动、实际拖动返回起点、Cancel后End、孤立End、多触点、命中区不缩小、漏Move远距离释放、重复释放、ID0及遗漏Release后的下一次点击。
- HUD测试改用真实Start→End输入序列，仍能单击打开订单、定位骑手及保存。
- `npm test`共142项通过（27旧域＋93地图/经营/展示＋18存储＋4数据），0失败：[完整日志](button-taps/tests.log)。类型检查退出0：[日志](button-taps/typecheck.log)。Cocos构建退出0：[日志](button-taps/build.log)。
- 独立只读复核PASS，无确认P1/P2；再次核对引擎捕获CANCEL/End机制并运行11项定向回归，全部通过。[复核](button-taps/review.md)。

用户刷新[当前游戏](http://localhost:4181/)后重点单击抢单、关闭、选路和出发，再确认滑动大厅不误接。不代替用户判定实际设备上的点击手感，也不清理存档。
