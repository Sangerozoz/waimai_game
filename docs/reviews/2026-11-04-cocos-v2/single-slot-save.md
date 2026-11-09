# V2 唯一存档与清空重开

2026-11-04。按用户最新明确授权：旧存档全部废弃，全部新开；只能保留一份当前进度，清掉即消失。此要求覆盖历史保档/迁移/备份限制。仅当前 V2 入口实施，未清项目文件、fixture 或真实浏览器数据。

## 唯一持久快照

- `delivery-county-single-slot-v1`：唯一游戏快照，直接保存当前 V2GameSession 序列化结果。固定 key，不随经济配置 ID 增生。
- `delivery-county-single-slot-epoch-v1`：一个随机世代标识，仅用于废止旧运行实例，不含人物/金币/路线等游戏进度，不能用于恢复游戏。
- Web Lock 名仍为 `delivery-county-save-v1:writer`，是浏览器并发锁，不是存档 key，也不包含快照。

V2RuntimeStore 不再调用 CountySaveStore，不写 backup/corrupt/pre-foundation，不读旧档，不迁移，不从其他 key 自动回退。CountySaveStore 原实现留给旧工程，当前 V2 不接入。

## 明确清理 allowlist

启动 V2 入口即尝试取得共享 Web Lock，逐项删除下列已知游戏 key；打开游戏和重开时再次清理。没有 localStorage.clear，也没有前缀通配清除。

```
delivery-game-save-v1
delivery-game-save-v1-recovery
delivery-county-save-v1
delivery-county-save-v1:backup
delivery-county-save-v1:corrupt
delivery-county-save-v1:pre-foundation
delivery-county-v2-economy-save-v1
delivery-county-v2-economy-save-v1:backup
delivery-county-v2-economy-save-v1:corrupt
delivery-county-v2-economy-save-v1:pre-foundation
delivery-county-v2-runtime-save-v1
delivery-county-v2-runtime-save-v1:backup
delivery-county-v2-runtime-save-v1:corrupt
delivery-county-v2-runtime-save-v1:pre-foundation
```

来源静态搜索：DeliveryController.SAVE_KEY 及 `-recovery`；CountySaveStore.COUNTY_SAVE_KEY 及其三个衍生 key；CountyV2Session.COUNTY_V2_SAVE_KEY；旧 V2RuntimeStore 的 runtime key 及 CountySaveStore 衍生 key。未找到其他生产源码游戏 localStorage key。未删除引擎/其他产品数据。

## 用户入口与重开

入口一个“开始游戏 / 继续游戏”动作，由是否存在当前 slot 决定文案，点击后在锁内重新读取最新状态。首次使用新版清旧档后从头开始。坏档/不支持的快照显示可读错误，仍保留“清空进度重新开始”按钮，明确提示永久清除并需再次点击确认，不创建临时新档覆盖坏档。

首页提供可见“重新开始”按钮，弹出遮罩确认框：“将永久清掉全部进度并从头开始；仅一个存档，清掉后无法恢复”。取消不删除。确认后先停用运行会话、废止广告回调世代，再更新 epoch、删除唯一快照及旧 allowlist，创建并保存全新会话；页面选中订单/车辆/反馈等内存展示状态一起重置。删除/保存失败不继续旧会话，返回入口可重试。

每次写入同时要求当前实例持有共享 Web Lock、epoch 等于已取得世代、slot 字节等于本实例最近一次读取/写入值。重开后旧 runtime 已失去 live，会话回调也受 generation 限制；其他新代码标签页不能并发取得锁。没有写锁的页面明确要求先关闭其他游戏页，不能以强行抢锁破坏存档。删除 slot 后仍在运行的实例，下次提交因字节不同停止保存，无法复活原档。

## 验证边界与手动检查点

本次仅静态检查 API、持久 key 来源和调用关系，未运行 tests/typecheck/回归，未打开或操作用户浏览器实际存档。必要 Cocos 构建由主代理统一执行，本文不声明构建/游戏测试通过。

阶段测试时在隔离 origin/浏览器资料中检查：旧 key 与备份存在时启动仅清 allowlist；其他产品 sentinel 不变；首次全新开局；关闭后再次打开继续同一 slot；重开取消/确认；坏 JSON 和未来版本可清空重开；两个标签页第二页不能写；重开前广告回调不能进入新会话；存储拒绝删除/配额写失败可返回入口；手动删除唯一快照后旧实例不能自动保存复活。

限制：浏览器存储是本机 origin 范围，不跨域、不跨设备。Web Locks 不可用时维持阻止写入并显示错误。极旧 DeliveryController 不使用共享 Web Lock，若用户单独运行旧版可再写旧 key，但新版绝不读取，并在下次进入时再次删除。未改旧工程以免扩大任务范围。epoch 与快照两个 localStorage 操作不具备跨 key 事务；若清空中断而删除未成功，入口报错，不宣称已清空；删除成功后不保留恢复副本。
