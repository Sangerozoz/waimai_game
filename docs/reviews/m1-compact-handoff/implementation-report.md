# COMPACT-HANDOFF 开发交付（已冻结）

2026-10-30，依据最终spec `docs/superpowers/specs/2026-10-30-compact-handoff-design.md`。沿用当前checkout和48份before/SHA；本轮生产单一写入，无子代理、提交、清理或用户4181游戏/存档操作。

## 实际实现

- 大厅与当前卡共用CompactOrderInfo测量/绘制：期限/来源；食品图及菜名份数/整单重量风险；右大黄金额+km；左右取送与箭头；真实备注。保持字号，通过行距和去掉重复标注收紧。当前规划卡最多三条真实路线横排；普通内容不需纵滚，长备注回退中区滚动，固定按钮保持可达。
- 左红取消/右黄阶段动作。planning/toPickup/awaitPickup可免费取消，开始取餐后业务拒绝；X只收卡。取消不发奖/扣费/扣分/换候选/改额度；旧规划及旧活动尚在真实取餐路段时也按免费取消守卫处理。
- schema4保存明确handoff版本/phase、elapsed与pickupWaitElapsed；独立ManualHandoff校验阶段/进度/mode/服务一致性。新接单进入手动流程，旧活动不加人工边界；schema1/2/3原校验后兼容，地图catalog4及mapId未改变。
- 路中取消保存真实road/from/to/fraction。下一路线origin前缀含合法出口、真实点、剩余道路距离/时间；全程定位、绘制、取餐ETA与总计包含前缀。方向/坐标/首段/总计按地图严格校验，不插入虚拟地理节点。连续两次前缀中取消、正反向、单行路已测。
- pickupPath统一预览/寻路/商家排序/筛选/新候选生成；修复审核发现的单行取消后刷新仍按旧节点选商家的P1。原池不可达或超限单保留原ID/位置并禁用，不使大厅整体抛错；刷新新单从真实起点可达。
- 去取餐→到店待取→点击取餐2秒→待去送餐→点击出发→自动按原需求交付结算。大dt逐个人工边界截断，双击守卫，服务0/1/2秒恢复，等待/服务不加游戏分钟。旧未回答door也按true完成；已done旧回答、回执与奖励不重算，交付要求弹窗不再开放。
- 到店/待送/结算主动覆盖收卡或车辆/地图/账单查看态。同一接取尝试的phase只触达一次；每次新接单清空旧提示键，修复同ID到店取消重接后吞提示的问题。后台冻结，恢复首帧丢弃补偿dt。
- pendingSave冻结后续动作与移动，保留确定结果重试；错误持续可见，成功后再开放关键事件。未知未来主档或备份恢复失败时写保护，保留字节。此机制不等于跨会话原子CAS，也不宣称完整M2并发底座完成。
- 结算只留大收益、真实状态、一致的晚到/餐损收益影响、评价和一次XP。纯quote复用原评分/收入公式，I0/I1/I2逐分对账，不创建对照钱包，不新增罚款/二次扣款，MAX余额报价不溢出。弹窗按实际文字高度求高，正常结果收短。
- 规划展开临时隐藏灰站点/定位，收卡和行驶恢复；短屏自动规划采用正的可见区域，手动缩放和30m平滑定位保留。保持卡底至中央红圆最高边12CSS间距。

## 最终检查

| 命令/证据 | 结果 |
| --- | --- |
| npm test --prefix delivery-game | 退出0，27+190+20+4=241通过 |
| npm run typecheck --prefix delivery-game | 退出0 |
| npm run build:map --prefix delivery-game | 包装退出0，08:42:24 Finished |
| Cocos子进程 | build.log保留code:null / SIGTERM诊断，不能称原始进程零异常 |
| developer-core-final.log | 独立核心runner在最终核心源码上复跑17/17，退出0 |
| compact-preview + browser-standard-safe | 720×1280、720安全区、360×560、360安全区：真实三路线门口备注卡maxScrollOffset全为0 |
| browser-flow | CLI退出0，34条记录；三种视口的全381路径点、车/两pin完整入地图且避4组HUD；阶段事件、1秒服务重载、取消/下一单前缀、结算关闭等 |
| browser-lobby | CLI退出0；三种视口的首/转单/末卡，普通黄抢单与绿接受转单 |
| browser-legacy | CLI退出0；构造合法schema3未回答arrived经真实恢复及当前订单入口按true结算，无需求弹窗、重复settle不再奖励 |

红绿保留：handoff-red/green、prefix-red/green、future-red/green、future-backup-red/green、reaccept-event-red与最终tests.log。最后一组旧实现明确失败为账单仍在上层，最终回归通过。

部分原自动流程测试明确改成legacy-order-fixture；新手动单在独立manual-handoff/manual-hud测试覆盖，不把旧测试偷当新流程。独立核心审核另用本轮before真实模块及历史fixture验证兼容，详见其报告。阶段UI审核报告是开发中旧SHA，不能把旧F1日志冒充最终通过；当前开发修复证据已更新，独立尾验由PM接续。

## 样板与指纹

最终源34份SHA在final-source-sha.json，精确差异production.patch。37张最终PNG在screenshots/并列于screenshot-sha.json；旧preview图移到iterations/保留溯源，不混入最终集。fixture-sha.json和build-manifest.json记录脚本/构建；独立样板与66个构建文件逐字节匹配，只有index插入fixture脚本。

样板4191新内存OrderBook；生产start/update/save在创建CountySaveStore之前截断，Storage四种API全拦。真实浏览器记录引擎setItem('storage')探针被拦，不能称零访问。浏览器通过真实Cocos模块/节点事件和显式内存推进观察状态，未运行生产update调度；实际MapSample.update、后台和保存失败栅栏由模块边界测试覆盖，不混称真机后台/触感/FPS验证。

最后核对生产SHA未改变。主备档/服务与动作恢复、财务幂等、布局和关键交互的开发自检已完成；真机帧率/手感、用户体验验收及PM安排的独立最终闭环仍单列。本轮不包含加速、多单、体力/NPC或独立功能页面。
