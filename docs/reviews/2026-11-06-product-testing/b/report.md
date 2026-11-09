# 产品测试 B：旧冻结包 RED 检查点（等待父PM修复包）

**非最终报告：真实UI测试在planned路线选择处FAIL，保留上下文和该单，暂停等待。**

仅内部4198，本线程自有local headless `b49c55d0-74b5-4dd7-9829-bfdc4cc1d74c` / host_tr578kqahd。390×844、仿真DPR2、触屏tap/TouchHandle拖拽；画布780×1688，保存截图390×844，非真实手机或用户浏览器。

## 真实结果

- 入口及12个实际加载JS、1个import-map输入的HTTP SHA与`v2-tick-follow-1106`冻结包吻合。
- 新档首页未点定位，骑手已居中、follow=true。头像/底栏、骑手首末、原生车辆场景及车型3→10、菜图/徽标、地图卡图片可见。
- 骑手返回底部偏移保持；车辆底部点晨光后偏移保持。四页大标题删改、账单收入去币图/未记录字段、所查入口无重开保持。万元近似held不列缺陷。
- 通过真实UI选首张酸辣粉2格单，容量2/2，报价20；只点“选择路线”。真实订单已进入Trip3/planned，但路线/出发/底栏未渲染。
- 原始错误：`Uncaught Error: 配送容量单位或条款无效`。完整堆栈在B14/B19 JSON，真实空白页截图在B14/B19 JPG。
- 只读实际订单显示load与quote.terms.load均slots-v1/2格，capacitySlots=2。冻结包UI实际生成`p=be([].concat(u.values()),f)`；对应Map.values展开被loose转换为单个迭代器元素，totalV2Load继而拒绝。父PM已确认并接管单点源码/构建修复；B没有改源或绕Runtime出发。
- 正常reload后入口为“继续游戏”，经真实按钮恢复同一个`v2-road-268`，金额100、已送0、位置、phase/planned及Trip数据保持。恢复后再进入详情仍真实RED；这不是已完成单或行驶恢复PASS。

## 性能与未覆盖

只读rAF观察44138个间隔，p50=16.70ms，p95=16.70ms，最大483.30ms，>50ms为10个；longtask记录7项。范围是入口/菜单/错误页混合，不是active配送，不称真机FPS或全部性能通过。统计全观察窗，保留末尾300个原始间隔及longtask/错误原文；见性能JSON。

连续行驶/到店/取餐/服务/ready停留/主动继续/交付、非零已完成收入恢复、315×851暂停流程、多单同店/30NPC/广告及远程分享均未覆盖。不能把已实现的ready/分组/U22说成未实现，也不能把阻塞后的未覆盖记为PASS。

## 证据与暂停状态

[test-results.json](test-results.json)列分项PASS/FAIL/NOT_COVERED、完整SHA及状态；[actions-trace.json](actions-trace.json)列19个实际步骤；共17张截图已立即保存并指纹绑定。原B14/B15保留；B17/B18为正常续档，B19为恢复后RED。

当前仍是同一浏览器/4198 origin、同一planned单。只读frame.paused=True；不清档、不重接单、不执行业务命令。不关闭会话，等待父PM给精确新包/root/hash后复验。没有启动/更换4198服务或4182/4196，不写任何产品/地图源码、构建或资源。
