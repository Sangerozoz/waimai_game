# AU01 有边界的正常UI通道排查

2026-10-30，按项目经理指令仅检查一次，不轮询/重发。

1. cua.getState：ChatGPT应用 com.openai.codex 与Chrome运行中；浏览器列表为空，错误为 `Local browser use is disabled in Work settings`。此前ChatGPT原生应用已返回安全限制拒绝，本次不换其他底层接口访问该应用。
2. cua.getApp(com.google.Chrome)：可正常读取原生Chrome界面。当前是花瓣页面，无已打开的目标GPT聊天标签。
3. 通过Chrome原生新标签按钮，地址栏输入目标普通聊天 https://chatgpt.com/c/6ae2a254-e478-83e9-b1ae-23aa0282d551，使用正常Return导航。未访问内部API。
4. 随后的AX与截图显示目标URL的ChatGPT页面壳，正文为空且中央加载指示；`Open profile menu`、`Add files and more`、`Send`均disabled，profile显示Loading profile。没有取得原聊天正文、附件控件可用状态或任何发送回执。工具截图已内联留在本美术会话本轮，无本地截图文件，未虚构导出路径。

本轮未上传、未输入AU01正文、未发送，也未产生新成图。未遇到可供操作的验证控件，未解决/绕过挑战。最终观察补记如下。

## 排查结果：正常UI发送成功

页面随后加载完成，标题“规划主角形象”，mode=ChatGPT，目标URL正确，原聊天正文与可用附件入口实际可见。通过Add files and more → Add photos & files正常系统文件选择器上传唯一锚点；观察到style-anchor-image5.png附件缩略图，上传进度消失后填写prompt.txt完整正文并点击Send一次。

真实回执：AX显示分隔符 `Today 1:25 PM`、新 `You said:` 下的 `User attachment` 和以 `AU01：图5青春都市动漫风首批代表样板` 开头的正文；输入框清空，ChatGPT显示Thinking/Working及Stop按钮。由此确认本次已附图并发送成功，进入响应中。没有可用消息ID，不编造ID。未轮询或重复发送。

此前loading状态仅为加载过程，不能当最终阻塞；先前cloudflare_challenge是连接器发送失败，本次受支持原生Chrome UI已成功继续。未绕过任何验证。

截止回执时未观察到AU01生成图，因此仍为未成图、未导出、未接入、未获用户确认。旧B01下已能看到Generated image控件，属于旧方向历史产物，不是本批产出，也不代表用户接受。
