# COMPACT-HANDOFF 最终独立UI复核

2026-10-30。**UI所列技术及隔离真实渲染范围通过，F1关闭，同ID重接提示去重回归通过，无遗留已证实UI缺陷。用户真机体验未验收。** 原阶段证据留在independent-stage-report.md、independent-handoff.log与independent-stage-sha.json，不覆盖。

## F1与同ID回归闭环

- F1原为正常订单短屏风险行裁切、标准组件末路线底部超视口6设计单位。共享食品行移除重复小标题并收紧高度后，独立普通订单标准/短屏safe的content/viewport分别366/366、447/447，末路线底部留18单位。原17项修后全部通过；补极长文本、取消阶段及同ID后20/20通过，independent-handoff-retest.log。
- 真实Cocos新normal-three-720、normal-three-360-safe图亲自查看：三条路线名称、时间/km、风险/准时行均完整，无固定按钮遮挡。独立解析browser-flow.json三视口测量：scrollMax均0，所有route矩形完整在viewport内，卡底到圆顶换算均12 CSS px，见independent-real-records.log。不是仅凭复用函数判通过。
- 同ID：真实去取餐→awaitPickup→取消→原ID再接→去取餐，零距离直接awaitPickup仍重新触达且取餐入口可达。新accept重置lastHandoffEvent；同一次等待阶段收卡/查看页与普通帧不重新抢弹。INDEPENDENT_OLD_EVENT_KEY=1只在内存去掉重置，1项失败/退出1（independent-reaccept-red.log）；当前源码20项通过。该red是旧逻辑内存变体，不冒充历史构建实测；只看root变化会被普通rebuild掩盖，已补事件身份断言。

## UI/主动触达结论

| 范围 | 证据与结论 |
|---|---|
| 大厅共享紧凑布局 | 已亲看最终lobby-first-720、lobby-transfer-360图：普通黄抢单及转单绿接受转单；食品图/名称份数/重量风险为左中，黄色费与下方km靠右，左右地址及箭头，真实备注独立，未互盖。开发browser-lobby.json真实三视口transfer卡高390/470/470，小于列表viewport862/849/801，独立断言通过。这里不要求整个10单大厅零滚动，而是普通单卡信息紧凑完整。 |
| 当前卡正常内容 | 三路线横排完整、无重复装饰空白；普通三视口scrollMax0。红取消小于主操作，卡片与红圆间隔满足12CSS。亲看720/360safe实际图并核生产布局测量。 |
| 异常长内容 | 独立长备注/长地址实际标签保留原文，中区overflow增长、所有真实路线位于content范围、固定操作不被覆盖；亲看long-top-safe及最终long-bottom-safe，备注可读到末尾且最后路线可达，期限/底部操作固定。不是声称所有中文组合都已遍历。 |
| 取消阶段显示 | 独立真实phase推进确认planning/toPickup/awaitPickup可见取消，点击pickup后picking/awaitDeliveryStart/toDropoff/done不再显示。亲看arrive-pickup-360-safe左红取消+右取餐同时可见；ready-delivery-360-safe取消消失、仅去送餐。核心业务守卫与anchor合法性另由核心审核支持覆盖。 |
| 主动触达 | 独立真实小图OrderBook及生产MapSample按钮/update链：到店、服务完成、结算×收卡/车辆/地图/账单12组合均关闭普通查看页并直接回卡/回执，不等中央。再收卡或再开查看页，额外帧不反复抢弹。后台hidden大dt不推进，恢复首帧补偿dt丢弃，之后事件仍可达。真引擎browser-flow的34记录与阶段图为开发执行补证，不称本角色亲跑引擎。 |
| 保存失败UI栅栏 | 去取餐保存失败后pendingSave、可见失败提示，大dt不推进、不开放后续流程；恢复可写后重试解锁。最终源码presentHandoff也受pendingSave阻断；本轮不宣称完整跨页并发事务安全。 |
| 旧door与简洁结算 | 独立恢复真实历史fixture arrived，按生产启动使用的act→settle(true)路径回执，无demand弹窗；旧done receipt原样。标签只含收益、一行事实、确有影响的餐损行、评价与一次经验，无倍率/余额/基础价。亲看最终finish-trip-360-safe，收益22.38、准时/完好/按备注、一行评价+4/经验+10，紧凑无需长滚。旧启动测试不是完整resources/start流程，边界如实保留。 |

## 执行主体与日志

- 本角色亲跑：independent-handoff.cjs使用生产模块、81节点新内存小图及Cocos边界骨架，修正唯一父关系，未硬塞phase。20项修后通过；最终MapSample回执高度/事件键变化后只重跑受影响17项，**17/17、退出0**，independent-final.log。未因最终收口重复核心或全回归。
- 本角色亲自view_image：早期preview/door图用于F1发现；修后三路线/到店/待送/结算图；最终另看lobby-first-720、lobby-transfer-360、long-bottom-safe、finish-trip-360-safe。相关阶段指纹与最终库存指纹各自保存，不把已重拍同路径当前图当旧失败证据。
- 本角色独立数值核算：browser-flow三组路线完整/零滚动/12CSS间隔，browser-lobby三组转单卡可完整显示；见independent-real-records.log。来源是开发真实Cocos记录，非本角色重新发送浏览器事件。
- 核心审核支持fresh-core-audit.md/.log：checkpoint16组通过，最终仅CountySaveStore变化补未来primary/backup写保护2/2通过。其负责schema/anchor/旧档/收入分解，证据主体是另一个PM派发审核，不计作本角色亲跑。已读取最终报告并对照核心SHA，不重复其72组分解或anchor流程。
- 开发最终tests.log/verification.json：27+190+20+4=241通过、退出0；typecheck.log退出0；build.log于08:42:24记录Finished、包装退出0。这些是开发执行证据，不称本角色重跑；保留Cocos包装/子进程诊断边界，不写引擎零异常。

## 最终源码、样板与图指纹

实际核对final-source-sha.json **34/34匹配**，清单自身SHA `4c25a6f804928307a9c1f76afe609d57225d0f502f171547d6b1fd800d43342a`。关键：

- MapSample.ts `2dacdf2e7f6d978a226357fe3b6f8f1109586c964caf94e454ef9031cebfbb7f`
- CompactOrderInfo.ts `806b3df07fe49d02f0e881271ab1a7086bd826c475233762d67b3dc9347033d6`
- OrderBook.ts `f3b08c1cd876361eef71009b3a316fac55d6ec7711c95d0542de82bf02e816b2`
- fixture.js `6efaeed7c2383977a398a886fdf49930befb8a32c2fbf96165c01107a50f8a0f`

independent-final-sha.json保存全部34源、截图37张、fixture、构建66文件、浏览器记录及构建日志的实际SHA；66构建文件与隔离site逐字节一致，index仅去掉授权fixture插入脚本后比较，fixture本身与site一致。已对开发最终screenshot-sha.json的37张逐一核SHA，fixture-sha.json的7脚本和build-manifest.json的66构建文件均匹配；preview已移iterations。旧阶段失败仅引用留存原日志/阶段指纹，不把被重拍同路径图倒认成旧失败图。最终通过依据为上述亲看新三路线、大厅与结算图及同批browser记录。开发最终implementation-report.md/verification.json也已读取并入本方指纹，未变源码不重复测试。

## 权限与未验收边界

本角色所有产物限independent-*，未修改生产/开发tests、未派子代理、未访问用户4181或存档/真实接单购买。最终大厅直接查看开发同构建图，未重复驱动样板浏览器；已有同批图足够，未执行浏览器命令。

隔离fixture禁生产start/update/save、不创建CountySaveStore，内存会话；Storage.setItem('storage')支持探针被拦，不能称零访问。真实Cocos事件记录与模块替身分别注明，均不代替真机FPS、系统后台/触感或用户体验。未独立逐一检查全体餐品/地名/备注/phase×存档版本组合，不将小图用例扩为长期业务全覆盖；本轮UI关闭不代表完整M2或多写者存档安全完成。
