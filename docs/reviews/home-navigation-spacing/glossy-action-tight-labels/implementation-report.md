# 中央亮面抢单按钮与紧凑图文

已查看用户交付原图（1200×1200 RGBA），按原样复制到resources，注册main-action-glossy，以现有cartoonArt加载并等比填入145.6设计单位按钮。原生Surface作为加载前回退，成功加载后隐藏，白色动态文字位于其上；触控、大小及位置保留。原图与导入件SHA见source-sha.json，原图未改像素。

四侧caption在图片异步尺寸/激活变化时重新定位：以图片节点实际UITransform高度乘现有0.9缩放得到底边，减2 CSS px及Label框半高得到文字节点中心。使用Label行框而非字形墨迹边界，因此实际可见字形空白可能大于2px，需用户体验验收；图片大小、水平位置、标题字号和热区保留，异步水平spread仍使用缩放前框宽。

上次会话因网络权限撤销中断，恢复后保留原before，检查当前源码修改时间早于构建、构建JS含新资源键，故未重复构建。构建日志18:02:26 Finished；调用中断导致包装退出码不可确认。日志保留build-script SIGTERM诊断，不能据Finished推断所有子进程正常。4181静态HTTP 200、index SHA一致。changes.patch、source-sha.json、build-manifest.json保留源码增量、原图与构建文件指纹。

已实现，未测试，待阶段集中测试及用户视觉验收；未运行测试/typecheck/渲染，未操作用户页面或存档，未commit/push。
