# 送外卖 Cocos 工程

使用 Cocos Creator 3.8.8。当前游戏内容仍是未验收的 T01 原型，画面方向已被用户要求调整；MCP 接入完成不等于游戏版本完成。

## Cocos MCP

Funplay Cocos MCP 0.6.8 已安装到 Creator 3.8.8 的全局目录：

`/Users/sanger/.CocosCreator/builtin-extensions/3.8.8/funplay-cocos-mcp`

同一 Creator 版本打开的工程可自动加载全局插件。每个工程使用独立身份与端口；切换工程后必须重新核对连接的 `projectPath`，不能把“全局安装”理解为所有工程共享同一个场景。

当前工程连接：

- Endpoint：`http://127.0.0.1:28917/`
- Codex server：`cocos-delivery-gam-34a835`
- 项目配置：`funplay-cocos-mcp.config.json`
- 已验证工具：`get_editor_state`、`get_scene_info`、`get_hierarchy`、编辑器上下文的只读 `execute_javascript`。
- 已验证启用路径为全局插件目录，当前工程没有重复的项目级插件副本。

Codex 的连接配置已登记在用户配置中。当前会话未热加载新增的原生工具；重启 Codex 可加载新配置。在此之前，也可通过本地 MCP 桥接调用真实的编辑器服务：

```bash
cd '/Users/sanger/Documents/ChatGPT/taptap 2/delivery-game'
python3 scripts/mcp.py get_editor_state
python3 scripts/mcp.py get_hierarchy '{"rootPath":"Canvas","maxDepth":3,"includeComponents":true}'
```

Creator 必须打开本工程，服务才会运行。执行场景操作前先核对 `get_editor_state` 返回的项目路径；场景/预制体修改使用 MCP 的编辑器、场景和 AssetDB 工具，保存后读回验证。

验证记录：`../docs/reviews/2026-10-27-cocos-mcp-connection.json`。旧的项目插件副本和 Codex 配置已保留在仓库忽略的 `.merge-backups/2026-10-27/` 中。
