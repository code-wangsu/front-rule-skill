# 多模型与客户端接入

## 两层兼容，不虚构统一插件机制

- 模型层：Codex/OpenAI、Claude、Gemini、GLM/智谱、Kimi、DeepSeek、Qwen/千问等可将 UTF-8 Markdown 规则作为上下文。
- 客户端层：Hermes、Claude Code、Codex CLI/IDE、Cursor、Antigravity、Gemini CLI、各厂商 IDE/CLI、网页聊天是否支持文件读取、skills、规则目录和终端，取决于实际客户端版本。
- “规则可用于该模型”不代表某网页自动识别 SKILL.md，也不代表已对每个厂商完成集成测试。
- 不编造 .deepseek/skills、.kimi/skills、GLM 专用配置路径；没有经当前产品文档核实的入口，使用通用提示词/上传文件降级。

## 三种接入

### A. 原生 skill

客户端明确支持 Agent Skills/SKILL.md 时，把完整目录复制到其当前版本文档声明的技能目录。
保持根 SKILL.md 与 references/scripts/templates 的相对路径；agents/openai.yaml 是可选 Codex 展示元数据，其它客户端忽略即可。
使用用户或项目级哪个作用域由用户决定，不自动修改客户端全局配置。

### B. 项目规则入口

运行 scripts/export_rules.py 生成适配输出，再复制到已核实的入口，合并而非覆盖既有规则：

| 客户端 | 输出用途 |
| --- | --- |
| Codex / 采用 AGENTS.md 的 Agent | codex/AGENTS.md + AGENTS-2.md，全量独立规则 |
| Hermes | hermes/SKILL.md 和完整支持资源，或客户端认可的项目规则 |
| Claude Code | claude-code/CLAUDE.md + CLAUDE-2.md；也可用其原生技能目录 |
| Cursor | cursor/front-rule.mdc + front-rule-2.mdc，均带规则元数据，安装位置按当前文档 |
| Gemini CLI | gemini/GEMINI.md + GEMINI-2.md；入口名称可以由版本配置覆盖 |
| Gemini Antigravity | antigravity/frontend-rules.md + frontend-rules-2.md，通过其当前规则/工作流入口导入 |
| 智谱清言 / GLM、Kimi、DeepSeek、千问 | 各目录 system-prompt.md + system-prompt-2.md，一起注入 system/developer 或项目指令入口 |
| 其它模型与工具 | generic/system-prompt.md + system-prompt-2.md |

这些是导出文件用途，不是声明每个客户端都自动发现这些目录。
文件导出只是素材生成，不会联网、写 API Key、安装插件或改目标项目。

### C. 网页 / API / 仅聊天

不能原生加载 skill 时，把导出的 system-prompt.md 与 system-prompt-2.md 一起上传或放到长期项目指令；无法访问 references 时必须使用全量导出，而不是只贴相对链接。
只有用户消息可用时，将规则先作为任务约束提供，再给任务；不称它为真正 system role。
上传容量或上下文受限时优先十条硬约束 + 本次相关参考，不静默裁掉 ID 或确认门槛。
没有执行工具时只输出建议/补丁和验证步骤，不能声称文件已经写入或 tests 已通过。

## 导出命令

通过当前客户端终端，skill 根目录运行：

```text
python scripts/export_rules.py --output <new-output-directory>
```

输出目录必须新建或为空。内容聚合主规则与执行参考，移除 YAML 元数据及本地链接依赖。
每个客户端的规则按逻辑分成多个部分：第 1 部分（原文件名，如 `AGENTS.md`）是 SKILL.md 主体 + 代码规范 / 注释组织 / API 契约；第 2 部分（追加序号，如 `AGENTS-2.md`、`front-rule-2.mdc`、`system-prompt-2.md`）是 UI 还原 / 设计决策 / 组件 / 流程 / 测试 / 项目适配。每个文件独立保证 ≤500 行，文件头标注“第 n/N 部分，须一起加载”；接入时必须把全部部分都放进同一入口（同一规则目录、同一 system prompt 或一次性上传），缺一部分即规则不完整。
`manifest.json` 记录 `parts` 与各部分行数。不要把输出目录放到技能源码内部，避免重复打包。

## 验证清单

1. 核实客户端版本、入口范围、原生 skill 支持与上下文限制。
2. 检查十条硬约束已加载；没有被本地旧规则覆盖。
3. 测试未知字段是否询问、超长 ID 是否原样、mock 是否按范围清理、文件是否按职责拆。
4. 客户端无法执行脚本时明确降级；规则无法保证模型完全遵从，实际代码仍需审查与测试。
5. 本包验证结构、脚本与导出完整性；没有宣称所有厂商 SDK、IDE、网页模型都已真实运行。
