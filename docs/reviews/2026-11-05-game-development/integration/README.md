# 当前产品候选与历史集成记录

## 11-06实际新增：v2-product-candidate

- 前批核心/归日/车辆布局/P0轻量读取/资源缓存五份质量门禁与实际源码组合核对；P0原版本和各分项基线匹配，构建后源码及车辆helper哈希仍匹配。详见`product-candidate-source-freeze.json`、`product-candidate-build-integrity.json`。
- 必要Creator构建日志`build-product-candidate.log:1336`有Finished，进程仍退出36，SIGTERM/trackTimeEnd诊断保留，不称命令全绿。143衍生纹理路径、pack及143图原字节进入导出产物。
- 仅本地隔离4187外观核对，六页截图位于`visual-private/`，`riders-bottom.jpg`实际可见末位书宁；底栏/肖像/车图/菜图在这些屏幕可见。不读取或操作用户存档，不接单/购买/招募/升级/补给/广告，不跑tests/typecheck/回归，不测试配送/性能。
- 4182分享仍是旧v2-preview；本地出现不证明用户路径可见，不关闭U03—U07或98%。既有卡页只查看旧插图和文案，未制作地图或加工其资产。
- 真实遗留：U38今日/累计收入分类仍有金币堆；nav-base/button-disabled及clock/coin-stack回退调用出现warning。`private-visual-observations.json`记录只截获前200条，不是完整warning总数。车辆背景仍中性占位，不是场景资产；骑手新卡/近似金额仍待确认。
- 下一源码批次复用开发A（NPC帧内事件）和开发B（账单币图/无效回退调用），与本静态产物分开，不将后续源码冒充本包内容。

## 历史：集成候选01/02

父PM已读回Runtime热路径、Route权威LRU、GameSession、UI update和资源/布局报告。本轮尚无性能轨迹、远程真实显示或阶段行为结果，U01/U02及全局验收都未通过。

UI原owner thr_uevwv32vnh后续会话因上游502连接失败（不是代码失败）。已停止并读回idle、队列为空；原源码保留。父PM接管本次窄范围订单/地图/账单明确修改，没有重做待用户确认的骑手新排版/万元格式/四页标题。

父PM本次只改V2GameUI.ts：订单/在途详情去取送地址末端pin；KG跟餐名；订单顶栏/报价/专送/汇总的金币图片改¥文字标记（仍游戏币，不是人民币支付）；时钟与字做同一行光学偏移候选；地图未购买改未解锁（业务购买资格不变）；账单顶栏/指标/明细金额前金币图片移除。内部金额、称重、合同、扣款与账本逻辑均未修改。

Creator必要构建输出delivery-game/build/v2-candidate（不是当前4182的v2-preview）。build-candidate-01.log和build-candidate-02.log保留；进程均退出36，完整Finished及诊断由PM读取。未覆盖当前分享目录、未启动新分享、不把候选包当用户交付。

独立窄范围代码质量审查已启动 sa-0-f4cac4ed，检查U01/U02与本次明确展示修改；只读、不跑tests/typecheck/游戏，不声称运行通过。全页视觉审计仍fail，首页主体/远程图片/业务缺口保留。

骑手静态确认稿已实际生成并目视：../..//2026-11-05-ui-fidelity-recovery/rider-proposal-01/index.html（使用现有角色图集，非游戏截图）。用户确认前不把新骑手排版和近似金额规则进入运行版。
