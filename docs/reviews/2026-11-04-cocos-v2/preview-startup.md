# V2预览启动

2026-11-04用户明确要求启动项目看效果，授权必要预览构建/启动，不等同于集中测试授权。

Creator 3.8.8正常应用环境构建独立outputName=v2-preview，输出delivery-game/build/v2-preview，日志preview-build.log含Finished，进程退出36。日志仍有脚本构建子进程SIGTERM及计时诊断，保留不隐藏；未运行typecheck或测试套件，不能称其通过。

独立HTTP服务127.0.0.1:4182，预览URL http://127.0.0.1:4182/?v2=1，HEAD返回200。原4181服务及map-sample输出保持。本次未点击新建/恢复或操作存档。

尝试通过内置浏览器工具打开，工具返回browser access host unavailable，未能取得画面；只验证HTTP可达，不能声称已目视确认渲染成功。用户可点击链接查看，新档与恢复入口将由用户操作。
