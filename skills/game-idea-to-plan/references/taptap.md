# TapTap：阶段路由与当前能力核验

整理日期：2026-10-27。参考入口为 [TapTap agents.md](https://developer.taptap.cn/agents.md)（[人类可读版](https://developer.taptap.cn/agents/)）。保存流程要点与来源，具体参数和支持范围在执行时重新核验。

## 1. 先判断阶段

想法阶段使用通用规划方法；先交付完整的可玩循环。能玩之后按实际需要接平台能力；准备发行时再核对形态、产物、资料和流程。上线后依据游玩数据和玩家反馈安排改进。

这些是阶段目标，不表示必须先安装 CLI、登录、接 SDK 才能做原型。用户只讨论方法或暂不发行时，保持相应范围。

## 2. 比较候选形态，核验后选定接入路径

通道尚未确定时，先盘点现有产物，再查候选通道的兼容性、包结构和迁移成本，帮助用户选择。选定通道后读取相应细节并实施接入。

| 目标形态 | 官方入口 |
| --- | --- |
| 平台定义的 H5 游戏 | [H5 MCP 指南](https://developer.taptap.cn/minigameapidoc/quick-start/mcp-guide/mcp-setup/) |
| Tap 小游戏 | [小游戏开发文档](https://developer.taptap.cn/minigameapidoc/) |
| APK / PC | [游戏服务 SDK](https://developer.taptap.cn/docs/sdk/) |
| TapTap 制造 | 以制造控制台提供的本地插件和发布流程为准 |

网页运行、WebGL 渲染、使用 Cocos 等引擎是不同维度。Cocos 可导出网页，但产物是否满足某一 TapTap 通道，仍须核对该通道的运行容器、模板、接口和包结构；避免将引擎项目统一归成 APK / PC。

官方 agents 文档将「H5」与「Tap 小游戏（WebGL）」作为不同平台形态。按这个产品语境选接入路径，不推广成「所有 H5 都不能用 WebGL」的技术结论。

上述 H5 MCP 指南在整理时声明只支持 H5；其他引擎 Tap 小游戏的 MCP 支持仍在开发。该边界执行前重新确认。不能因为本地引擎 MCP 已连接，就推断 TapTap MCP 已配置或支持同一产物。

## 3. 工具与发布流程

开始平台工作时，优先读 [CLI 文档](https://developer.taptap.cn/v3/cli/)。若本机已有 CLI，通过当前帮助、`taptap-cli skills list` 和相关 Skill 查看实际能力；参数以当前 schema 为准，不从旧对话猜命令。

CLI 当前将 AI Skill 随工具版本同步；安装和更新方式读当前文档。agents.md 与更具体的 CLI 能力或通道文档存在差异时，核对当前版本和实际接口，记录差异，避免照搬固定命令。

创建草稿、准备产物与测试入口、真机验证、补齐资料与资质、玩家测试、提审与上线，是发行准备的主要工作。根据选定通道的当前流程组织任务；不能假定所有形态均可通过同一个 CLI 上传命令完成。

整理时 agents.md 提到 Tap 小游戏上传走控制台。实际操作前复核 [包体管理](https://developer.taptap.cn/v3/cli/skills/taptap-package-management.md) 与所选通道的最新说明。

执行前定位正确的开发者、应用、产物和目标环境。使用平台要求的预览、校验、幂等与确认流程；平台规定的高影响操作确认点需要保留。沿用用户已有授权，授权不足时才请求补充。创建技能本身不授权安装、认证、上传、提交审核或发布。

## 4. 按需增加能力与运营工作

平台能力对应具体需求再接入，每次形成可单独验证的增量。H5 与小游戏能力从对应小游戏文档寻找；APK / PC 能力从游戏服务 SDK 文档寻找，避免混用接口。

上线后的改进计划需要关联证据：重复反馈、操作卡点、关卡流失、留存或商店转化。把建议变成带假设与验收的任务；外部回复、宣传和发布仍遵守当前授权。

## 5. 维护来源

- 工作流：[agents.md](https://developer.taptap.cn/agents.md)。
- 工具能力：[CLI](https://developer.taptap.cn/v3/cli/)、[命令参考](https://developer.taptap.cn/v3/cli/command-reference.md)。
- 发行资料：[资料编辑与版本发布](https://developer.taptap.cn/v3/cli/skills/taptap-app-edit.md)、[资质](https://developer.taptap.cn/v3/cli/skills/taptap-qualification.md)、[测试计划](https://developer.taptap.cn/v3/cli/skills/taptap-test-plan.md)。
- H5：[MCP 安装与范围](https://developer.taptap.cn/minigameapidoc/quick-start/mcp-guide/mcp-setup/)。

无法访问当前文档时，标明哪些能力或参数尚未核验，交付准备清单；不猜测上传方式，也不宣称已具备发布条件。
