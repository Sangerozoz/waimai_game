# 写锁只读状态诊断 2026-10-31

## 已知事实

- PM报告当前 IAB 安全上下文和 Web Locks 可用；`delivery-county-save-v1:writer` 有一个独占持有者，clientId `71C046E12BA194743122B607E39331BF`，刷新后仍相同。用户现有画面 Lv5、余额 1872.95、评价100；本轮未读取或更改存档。另一个 Chrome 页使用不同存储环境和不同 clientId，已关闭；不能据此认定它导致当前占锁。
- `WebWriterLease.acquire()` 只尝试一次 `ifAvailable:true`；不可用时返回 false，`MapSample.start()` 仍载入存档并调用保存，`CountySaveStore.save()` 的 `canWrite()` 检查由此产生当前只读提示。它不说明锁由谁持有，也不能区分 Web Locks 不可用、申请异常和其他客户端占锁。
- `MapSample.onDestroy()` 调用 `release()`；`pagehide` 仅调用 `onHide()`，先记录/保存然后保留锁，没有针对持久化页面缓存的专门释放或恢复逻辑。普通后台隐藏也不释放，设计上锁随页面存续。若旧页面保留在缓存或隐藏上下文且未销毁，就可能继续持锁；当前没有证据证明这是本次原因。刷新后 clientId 未变也不能单独证明持有者属于当前显示页面。
- 源场景 `MapSample.scene` 静态只有一个 MapSample 脚本组件，源码搜索未发现主动再创建该组件。此事实不排除运行时重复场景、隐藏文档、其他脚本或嵌入浏览器生命周期问题，也未证明运行时只有一个实例。

## 建议只读定位

在当前 IAB 的 JavaScript 上下文由 PM 执行下式：申请一个随机命名的临时独立诊断锁，在持有期间用 query 比较其 clientId 与现有业务锁。该操作不申请、释放、窃取业务锁，不读写存档。仅返回锁 clientId 和比较结果；诊断锁回调结束自动释放。

```js
await navigator.locks.request('diagnostic-'+crypto.randomUUID(), {ifAvailable:true}, async lock => {
  if (!lock) return {error:'诊断锁不可用'};
  const held=(await navigator.locks.query()).held || [];
  const mine=held.find(x=>x.name===lock.name);
  const writers=held.filter(x=>x.name==='delivery-county-save-v1:writer');
  return {currentClientId:mine?.clientId, writers: writers.map(x=>({clientId:x.clientId, mode:x.mode, sameClient:x.clientId===mine?.clientId}))};
});
```

sameClient=true 表示业务锁的持有者和当前 JS 上下文同一 Web Locks 客户端，应进一步查当前运行时是否存在多个 MapSample/旧实例；不能直接视为同一个组件持有。false 表示另一个同存储分区上下文持有，需从内置浏览器的同源其他标签、隐藏/缓存上下文或宿主视图着手定位；仅一个可见标签不足以排除隐藏上下文。不要关闭未确认的页面、抢锁或清存档。

## 改动和未验证项

未改业务代码、存档协议、存档或浏览器状态，未构建、测试、渲染或操作游戏。尚未取得上面的当前上下文 clientId 对照，根因未确定；先获得对照再决定是否需要定位重复组件或处理持锁页面生命周期，不能盲目释放锁或自动接管。用户明确阶段完成后再组织测试。

## 追加证据：当前文档与持锁者不同

PM已在当前 IAB 执行上述诊断：当前 clientId `787D51436C475D2D00915F9F15ABDDAF`，业务锁持有者 `71C046E12BA194743122B607E39331BF`，`sameClient:false`。因此持锁者属于当前文档之外的 Web Locks 客户端，同页重复初始化不是本次占锁原因；具体是哪一个旧文档或隐藏上下文尚未确认。

PM将关闭当前只读游戏标签后以原 origin 重开，排查同标签旧历史或缓存文档残留；若锁仍存在，继续定位其他隐藏 IAB 上下文。当前不改业务代码或存档协议，不抢锁、不清存档。此前“尚未取得对照”仅代表追加证据前的状态。
