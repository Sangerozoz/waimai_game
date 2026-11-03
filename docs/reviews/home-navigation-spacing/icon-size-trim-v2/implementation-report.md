# 底栏图标再次缩小

四侧图片节点局部scale设为0.9，UITransform原适配框和异步加载后的原始框宽不变，spread仍按缩放前框宽计算，因此位置和热区保持；文字、中央按钮、站点定位和订单面板未改。图片加载前的原生占位不变。

before、changes.patch和manifest.json记录源码前后及构建SHA。一次构建17:54:27 Finished、包装0；build.log保留build-script SIGTERM诊断，不能据包装结果推断子进程均正常。4181 HTTP 200，index SHA一致。

已实现未测试，待阶段集中测试与用户体验验收；未运行测试/typecheck/渲染，未操作用户页面或存档，未commit/push。
