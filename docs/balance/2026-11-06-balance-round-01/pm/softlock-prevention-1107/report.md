# 唯一车防新增软锁：集成交付

2026-11-07，PM `thr_4xmqy6fzdm`。作者复用B，独立审查复用A，同checkout/Sanger max。

防新增已集成并更新4182/4196。给NPC配置非空车辆以及kg/slots新签批均保留主角至少一辆可恢复车辆；拒绝文案“请为主角保留一辆可用车辆”，原子失败。已拥有但被NPC当前配车或未付旧合同占用的车不算备用。主角卸装、NPC卸车、自由购买/招募保持，旧批照原有限额度与原价推进，restore未加新全局约束。

## 验证与证据

| 门禁 | 实际结果 | 收据 |
|---|---|---|
| 作者RED/GREEN及最终测试ROOT | 最小RED 1失败、边界RED 17失败/1通过；最终GREEN 71/71，原件保留 | [作者交付](../../../../reviews/2026-11-06-product-testing/b/softlock-prevention-1107/receipt.json) |
| A独立只读审查 | Critical/Important/Minor各0，确认两源及最终测试SHA | [审查原文](independent-review-a.md) |
| PM完整默认回归 | `node delivery-game/tests/run-v2.cjs`，113/113，exit0 | [回归](default-regression-receipt.json) |
| 项目类型检查 | `node delivery-game/scripts/typecheck.cjs`，exit0 | [类型检查](typecheck-receipt.json) |
| 真实Creator构建 | 36/Finished，721输入无漂移，550文件、14个JS | [构建](build-receipt.json) |
| 原4182/4196 | 每端入口及全部14个JS均200且SHA匹配 | [服务身份](preview-deployment-receipt.json) |

原224保护清单未修改；批准变更只有 `V2EconomySession.ts`、`V2FleetSession.ts` 及 `run-v2.cjs` 的PlaceCatalog编译入口，其余221项一致。新增测试按最终SHA原样进入 `tests/product-regression-1106/hero-car-reserve.test.cjs`。A旧模型输入中的两源已按本次批准更新，旧36项指纹和模型产物仍作为历史保留，不能冒称生产36项仍零漂移。[集成指纹](integration-receipt.json)。

首个Creator沙箱内启动在macOS RegisterApplication阶段SIGABRT，日志为空、无产物；原失败及崩溃摘要保留。相同命令经单次临时沙箱外执行后成功；成功日志仍含build-script SIGTERM诊断，不隐藏。[首次失败](build-attempt-01-receipt.json)、[诊断](build-launch-diagnosis.json)。未改机器、模型、账号或全局权限配置。

## 交付边界

已签、零额度且唯一车仍被旧合同保留的旧软锁终态仍可读，**本修复没有救援它**。不赠车、取消、注资、补额度或重价。带剩余额度的历史批次和旧kg合同兼容在领域测试覆盖；本轮没有浏览器/用户档操作，旧B20～41证据保留且不当作新包浏览器验收。

长期A结果接收到150.076223分钟、亲送771单/NPC884单、12NPC/3图/5款付费车型；CPU270.125秒主动停机，80%及完整节点未到，时间比null。30级训练排除、同一city复用；PM只做16项离线核对，没有重跑模型。报价候选C仍未批准。

40项用户反馈正式关闭0；E09防新增结果通过，旧档救援仍开放。全产品、真机FPS、广告SDK及98%尚未验收。A/B本批写集已交回，原生权限选项未暴露，不虚报Default已切换。

旧软锁救援的[候选规则](recovery-options.md)已另行具体化，等待用户选择；当前交付不包含该新机制。
