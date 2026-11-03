# 配送暂停/取消规则与D档45度展示接入

**已实现，未测试，待阶段集中测试。** 依据用户本次明确规则覆盖旧“取餐后不可取消”及暂停“退出/reload”交互。未运行测试、typecheck、回归、渲染或独立复验；未操作用户4181游戏/存档，未commit/push。旧报告的退出刷新语义不再代表当前实现。

## 实际实现

- 暂停入口改为原生Graphics绘制Ⅱ双竖条，继续使用头像经验条下位置、原足够触摸宽高和公共按钮。新手动流程仅running中的awaitDeliveryStart/toDropoff显示；取餐前、picking、到达/已结算均隐藏。header布局和逐帧进度更新共同同步可见性，避免服务完成后必须重建页面才出现。旧活动安全适配为running且tripStage为delivery（collecting服务尚未完成不算），其余不扩大。
- 暂停弹窗改为“继续游戏/取消配送”，旧exitGame/window.location.reload代码移除。独立活动读档继续入口保留；暂停仍冻结行驶/服务/在线/时钟，UI和保存重试保持可用。
- OrderBook新增canCancelDelivery与cancelDelivery，与取餐前原cancel分开。仅上述配送窗口允许；done/已结算拒绝。先计算当前真实路段anchor并用anchorExits解析合法性，再同步设置riderAnchor/currentNode、清active。保持钱包、评价、经验、完成单数、候选池、随机状态、刷新额度、ledger不变；不补记整单里程，不回退已在线区间，不调用settle/finish/refill。
- MapSample取消前先完成已有pending提交，避免把两个命令混写。业务清单后设置cancellationPendingReturn并提交当前快照；失败仍在暂停，继续按钮暂禁，取消按钮可重试原快照，后台既有保存重试也可完成。成功才清暂停并重建首页、恢复底栏；成功前无新行驶/经济动作。自动重试成功同样完成回首页，绝不reload。下一次候选展示、路线预览与接单复用既有riderAnchor寻路，包括单行合法出口；没有换池或退回原点。
- 已实际查看用户au02原图。原样导入resources/map-sample/anime/au02/vehicle-d-three-quarter-original.png，保留RGBA和暖光半透明边；side-d使用完整1536×1024原图SpriteFrame，车辆页按原等比适配显示。top-d仍用au01顶视，side-d-plus/top-d-plus仍旧库存，未声称D+已替换；没有将45度展示图拿去地图旋转。

## 保存与兼容

无需新增schema，取消结果复用schema5的active:null/riderAnchor/currentNode和既有随机状态；CountySnapshot校验及CountySaveStore提交包络未改。重启前取消未提交则读回上次合法活动并停在继续入口，提交成功则读回首页及真实锚点。保存失败只重试同一取消结果，重复按钮不再执行业务清单，不产生奖励或额外扣费。旧活动亦不改其履约profile；它若仍running且已取餐，可按新增取消意图结束，已结算绝不回退。

## 构建与证据

`npm run build:map --prefix delivery-game`包装退出0，build.log于2026-10-30 14:02:37 Finished。产物delivery-game/build/map-sample。4181静态首页HTTP200，index响应与当前构建SHA记录static-http.json；仅HTTP，没有游戏页面操作或存储访问。构建完成不代表逻辑、保存恢复或视觉验证通过。

before/、before-sha.json记录本轮范围基线；production.patch记录MapSample/OrderBook/CartoonArt实际差异；asset-sha.json记录au02原图和导入件；final-source-sha.json、build-manifest.json、delivery.json是当前最终指纹及命令结果。CountySnapshot仅保存before未修改。仍待阶段测试：取餐阶段可见性、旧活动适配、精确anchor/下一单接入、失败重试/重启、取消经济不变及45度图实际显示。
