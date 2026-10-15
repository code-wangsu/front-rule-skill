# front-rule-skill

前端 UI 还原与代码规范 skill。让 AI 编码助手在写前端代码时：先核实项目、设计与接口事实，忠实还原设计稿，沿用项目已有的规范与封装，写出简单、可读、可审查的代码，并在交付时说清改了什么、有什么风险。

不绑定行业、框架、组件库、模型或客户端。适用于 Vue、React / Next、Angular、Svelte、原生 Web、uni-app / Taro 跨端（小程序、H5、App Android / iOS）以及桌面与原生前端项目。

## 优先级

1. **已有项目的规范优先**：目录结构参照相邻页面，复用项目已有的组件、第三方组件、hooks、插件、指令与工具；UI 样式以项目现状为准，不按本 skill 的设计原则改造。
2. **硬约束在任何项目都必须满足**：JS / TS 的十条硬约束与代码规范不因项目风格而豁免。
3. **未知与矛盾交给用户**：接口文档、需求文档、原型、截图之间不一致时，改代码前逐条指出，由用户确认唯一基准，不自行择一。

## 它约束什么

**UI 还原与设计**

- 有设计稿：以设计稿为视觉真源，按“UI 还原七步”提取 tokens 并对照项目、映射组件结构、补全状态，逐维度报告一致 / 偏差 / 未验证。
- 无设计稿的全新界面：先出设计计划，对照常见的模板化特征自审，再实现（思路改编自 Anthropic 的 [frontend-design skill](https://github.com/anthropics/claude-code/blob/main/plugins/frontend-design/skills/frontend-design/SKILL.md)）。
- 展示约定：只有 `0` 显示 `0`，空值文本显示 `-`、组件显示 placeholder；表格、卡片、模块无数据显示空状态；标签与按钮外观区分；超出内容有可见滚动条，Tab 页签固定、内容区滚动。

**十条代码硬约束**

1. 中文注释（函数、变量、import / export、props / emits、模板关键区）
2. 不猜测实现，未知业务先确认
3. 接口字段直绑；mock 集中在模块 `mock.js`，接入后整文件删除
4. 显式分支，不用三元与跨字段候补
5. 实体 ID 全链路字符串
6. 单文件不超过 500 行，按职责拆分
7. 复杂浮层独立组件，重复逻辑抽 hooks，CRUD 入口分离
8. 沿用项目既有规范、目录与封装
9. 语法以 `package.json` 中实际安装版本的官方文档为准
10. 函数单一职责、原子化，React 保持纯函数，代码简单不炫技

**通用代码规范**：命名、类型、组件结构（Vue 单根节点、二次封装透传）、复杂度控制、样式复用（变量 / mixin / 继承）、插件 class 单例、API 层只发请求、可访问性、性能、提示与 loading 只出现一次。

**跨端（uni-app / Taro）**：CSS 用 `rpx`，`uni.xx` / `Taro.xx` 使用前先查官方文档与平台兼容表，平台专有代码放条件编译，除长连接外每个请求有 loading，App Android 的权限、返回键、安全区与真机验证单独核对。

**交付**：项目实际的 lint / 格式化 / 类型检查清零；逐文件说明改动、影响范围、风险与回滚方式，未验证项与待确认事项单独列出。

## 使用

### 作为原生 skill

把整个目录复制到客户端文档声明的 skill 目录（保持 `SKILL.md` 与 `references/`、`templates/`、`scripts/` 的相对路径）。Agent 会按 `SKILL.md` 的触发场景加载，并按任务读取对应参考文件。

### 导出为独立规则

不支持 skill 的客户端或网页模型，用导出脚本生成不依赖相对链接的规则文件：

```text
python scripts/export_rules.py --output <空的新目录>
```

每个客户端输出两个文件，必须一起加载：

| 部分 | 文件示例 | 内容 |
| --- | --- | --- |
| 第 1 部分 | `AGENTS.md`、`front-rule.mdc`、`system-prompt.md` | 主规则、代码规范、API 契约、跨端适配 |
| 第 2 部分 | `AGENTS-2.md`、`front-rule-2.mdc`、`system-prompt-2.md` | UI 还原、设计决策、组件、流程、测试、项目适配 |

覆盖 Codex、Claude Code、Cursor、Gemini CLI、Antigravity、Hermes，以及 GLM、Kimi、DeepSeek、Qwen 与通用提示词。各客户端的放置位置见 [多模型与客户端接入](references/model-integration.md)。脚本只生成文件，不安装、不覆盖任何已有配置。

## 目录结构

```text
front-rule-skill/
├─ SKILL.md                        入口文件，Agent 每次任务都会加载
├─ README.md                       本说明，给人看，Agent 不依赖
├─ LICENSE.txt                     MIT 许可
├─ references/                     细则，按任务按需读取（见下文）
│  ├─ workflow.md                  需求确认与基准一致性
│  ├─ project-adaptation.md        跨框架、跨行业适配
│  ├─ cross-platform.md            uni-app / Taro 跨端适配
│  ├─ ui-restoration.md            有设计稿时的还原方法
│  ├─ ui-design.md                 无设计稿时的设计决策
│  ├─ ui-components.md             组件、分页、透传、空值空状态、标签、滚动
│  ├─ development.md               注释、目录组织、500 行拆分
│  ├─ code-standards.md            通用 JS / TS 与样式规范
│  ├─ api-contract.md              接口、mock、字段直绑、ID
│  ├─ testing-review.md            测试、lint、审查与交付说明
│  ├─ tooling.md                   三个脚本的用法与边界
│  └─ model-integration.md         多模型、多客户端接入
├─ templates/                      执行过程中填写或参考的文件
│  ├─ ui-restoration-checklist.md  设计稿还原记录（tokens 对照、逐维度验证）
│  ├─ contract-checklist.md        接口确认清单（基准一致性、mock 清理、ID）
│  ├─ review-checklist.md          交付前自检与交付说明模板
│  ├─ vue-page.vue                 薄页面示例（带中文注释）
│  └─ use-record-list.js           单一查询 hook 示例
├─ scripts/
│  ├─ check_frontend.py            只读扫描目标项目的规范风险
│  ├─ validate_skill.py            校验本 skill 的结构、链接、编码、行数
│  └─ export_rules.py              导出给不支持 skill 的客户端用的规则文件
├─ tests/
│  ├─ test_checks.py               check_frontend / validate_skill 的单元测试
│  └─ test_export.py               export_rules 的单元测试
├─ evals/evals.json                17 个行为评测场景（输入、期望行为、断言）
└─ agents/openai.yaml              可选的客户端展示元数据，其它客户端可忽略
```

`SKILL.md` 保存所有不可省略的内容：角色与立场、开始前核实、UI 还原七步、十条硬约束、通用规范要点、九步执行流程、常见陷阱。`references/` 只放展开的细则，Agent 按任务类型读取需要的几份，不一次全部加载。

## references 文件说明

按执行时通常被读到的先后排列。

### workflow.md：需求与确认流程

- **作用**：决定“能不能开始写、要先问什么”。
- **内容**：按改动大小分级处理；必须向用户确认的情形（字段 / 枚举 / 权限未知，接口文档、需求文档、原型、截图互相矛盾，设计值与项目 tokens 冲突，需要新依赖或扩大范围）；提问格式（事实 / 未知 / 影响 / 请确认）；同一问题修两次无效即停止猜测。
- **何时读**：每个任务开头；发现任何来源不一致时。

### project-adaptation.md：跨框架、跨行业适配

- **作用**：把通用规则翻译到当前技术栈，避免把 Vue 写法套到 React 等。
- **内容**：各框架中 hooks、props / emits、注释语法的对应关系；行业中立（金额、隐私、时区由需求决定）；环境中立（没有 `package.json` 时读对应生态的清单）。
- **何时读**：项目不是常见 Vue / React Web 项目，或第一次接触该仓库时。

### cross-platform.md：uni-app / Taro 跨端适配

- **作用**：跨端项目的额外要求。
- **内容**：识别 `manifest.json` / `pages.json` / Taro 配置与目标平台；`uni.xx` / `Taro.xx` 使用前查官方文档和平台兼容表；除长连接外每个请求有 loading；条件编译写法与“uni-app 不能用条件编译区分 Android / iOS”；`rpx` 换算；App Android 的权限、返回键、安全区、真机验证。
- **何时读**：发现项目是 uni-app 或 Taro 时，在写任何代码之前。

### ui-restoration.md：设计稿还原

- **作用**：有设计稿 / Figma / 截图时，保证实现与设计一致。
- **内容**：输入可信度（源文件为“测量”，截图为“推算”）；提取 tokens 并对照项目；组件树映射；缺失状态补全表；响应式与资源；逐维度对照报告格式；常见还原错误。
- **何时读**：任务带有任何设计输入时，在写 UI 代码之前。

### ui-design.md：无设计稿的设计决策

- **作用**：全新界面没有设计稿时，避免做出模板化的页面。
- **内容**：先确定产品主题、受众与首要任务；字体、结构、动效、文案原则；五类常见模板化特征；“设计计划 → 自审 → 实现 → 自评”两遍流程。
- **何时读**：只在全新项目或无可沿用视觉语言的新界面时读。已有项目的 UI 以项目现状为准，不读本文件。

### ui-components.md：UI 组件与展示约定

- **作用**：组件选型与通用展示行为。
- **内容**：组件选择顺序（项目封装 → 已引入的第三方 → 确认后新增）；抽屉与表格布局；分页契约；二次封装透传；空值显示（仅 `0` 显示 `0`，空值文本显示 `-`，组件显示 placeholder）与空状态；标签与按钮区分；滚动条与 Tab 固定；主题与权限。
- **何时读**：写页面、表格、表单、弹窗或封装组件时。

### development.md：代码、注释与模块组织

- **作用**：决定文件怎么放、注释怎么写、什么时候拆。
- **内容**：中文注释的粒度与示例；目录建议（已有项目先照相邻页面）；单一职责与 CRUD 入口分离；显式分支示例；500 行拆分方法。
- **何时读**：规划文件、新建模块或文件接近 500 行时。

### code-standards.md：通用代码规范

- **作用**：JS / TS 与样式的具体写法，任何项目都必须满足其中的 JS 规范。
- **内容**：版本与语法基线；命名；类型；组件结构（Vue 单根节点、透传）；原子函数与 React 纯函数；复杂度控制（不嵌套 reduce / 递归，合适时用数据结构与设计模式）；简单实用；样式复用与单位；可访问性；性能；插件 class 单例与 API 层只发请求；错误处理与提示；提交前自检。
- **何时读**：编码过程中随时对照；提交前用最后的自检清单。

### api-contract.md：API、mock 与 ID 契约

- **作用**：接口对接不猜字段、不留脏数据。
- **内容**：契约核实顺序（文档确认 / 用户确认 / 待定）；未接入时 mock 集中在模块 `mock.js`，接入后整文件删除；字段直绑；ID 全链路字符串与超长 ID 测试；API wrapper 职责、提示去重、loading 与并发保护。
- **何时读**：接接口、替换 mock、处理 ID 时。

### testing-review.md：测试、审查与交付

- **作用**：写完之后怎么证明、怎么汇报。
- **内容**：只用项目实际存在的命令；lint / 格式化 / 类型检查必须清零；回归测试要点；浏览器验证需授权；一次合并审查清单；交付说明格式（改动 / 影响 / 风险 / 设计还原 / 验证 / 未验证 / 待确认）。
- **何时读**：实现完成后、交付前。

### tooling.md：检查工具边界

- **作用**：说明三个脚本能查什么、不能证明什么。
- **内容**：`validate_skill.py` 的检查项；`check_frontend.py` 的扫描范围、规则与误报说明；`export_rules.py` 的分部规则与超限处理。
- **何时读**：运行脚本前，或解读扫描结果时。

### model-integration.md：多模型与客户端接入

- **作用**：把本 skill 用到不同客户端和模型上。
- **内容**：模型层与客户端层的区别；原生 skill、项目规则、网页提示词三种接入方式；各客户端导出文件对照表；接入后的验证清单。
- **何时读**：安装或迁移本 skill 时。日常写代码不需要读。

## 执行顺序

### 主流程

每个任务都按 `SKILL.md` 的九步执行，每一步对应要读的参考文件：

| 步骤 | 做什么 | 读取 |
| --- | --- | --- |
| 0. 加载 | 读 `SKILL.md`，判断触发场景 | `SKILL.md` |
| 1. 确定范围 | 列出入口、文件、设计输入、验收标准与未决项 | `workflow.md` |
| 2. 核实事实 | 读 `package.json` 与版本、相邻页面、注册入口、接口文档；对照各来源是否一致，不一致先问用户 | `workflow.md`、`project-adaptation.md`，跨端项目加 `cross-platform.md` |
| 3. UI 计划 | 有设计稿走还原七步前三步；全新界面先出设计计划 | `ui-restoration.md` 或 `ui-design.md` |
| 4. 组织代码 | 选已有组件与 hooks，规划目录与文件，预估行数 | `development.md`、`ui-components.md` |
| 5. 测试与实现 | 行为改动先写回归测试，再按规范编码 | `code-standards.md`、`ui-components.md` |
| 6. 接口接入 | 删 mock、封装 API、直绑字段、ID 检查、loading 与错误处理 | `api-contract.md`，跨端项目加 `cross-platform.md` |
| 7. 合并审查 | 一次性核对需求、还原度、注释、字段、组件、行数与范围 | `testing-review.md`、`templates/review-checklist.md` |
| 8. 验证 | 跑项目的 lint / 格式化 / 类型检查（清零）、目标测试、按需构建 | `testing-review.md`、`tooling.md` |
| 9. 交付 | 逐文件说明改动、影响、风险，列出未验证与待确认项，请用户确认 | `testing-review.md` |

第 2 步发现未知项或来源矛盾时停下来问用户，确认后再继续；只能先做不受影响的部分。

### 按任务类型的读取顺序

| 任务 | 读取顺序 |
| --- | --- |
| 已有项目新增页面（有设计稿） | `workflow` → `ui-restoration` → `development` → `ui-components` → `code-standards` → `api-contract` → `testing-review` |
| 已有项目新增页面（无设计稿） | `workflow` → `development` → `ui-components` → `code-standards` → `api-contract` → `testing-review`（UI 沿用项目，不读 `ui-design`） |
| 全新项目或全新界面（无设计稿） | `workflow` → `ui-design` → `development` → `ui-components` → `code-standards` → `testing-review` |
| 接口对接 / 替换 mock | `workflow` → `api-contract` → `code-standards` → `testing-review` |
| 修 bug | `workflow` → 与问题相关的一份（组件问题读 `ui-components`，接口问题读 `api-contract`）→ `code-standards` → `testing-review` |
| 代码审查 | `testing-review` → `code-standards` → 按改动涉及的内容补读 `api-contract` / `ui-components` / `development` |
| uni-app / Taro 项目 | 在以上任一顺序中，第 2 步后插入 `cross-platform`，写代码前必须读完 |
| 不熟悉的框架或行业 | 在 `workflow` 之后读 `project-adaptation` |
| 安装或迁移 skill | `model-integration` → `tooling` |

### 模板的使用时机

- `contract-checklist.md`：第 2 步填“基准来源一致性”表；第 6 步填接口事实与 mock 清理。
- `ui-restoration-checklist.md`：第 3 步填输入盘点、tokens 对照与组件树；第 8 步填逐维度对照结果。
- `review-checklist.md`：第 7 步逐项自检；第 9 步按其“交付”格式输出说明。
- `vue-page.vue`、`use-record-list.js`：第 4、5 步需要参考薄页面与单一 hook 写法时查看，不直接复制。

## 检查与验证

在 skill 根目录运行：

```text
python scripts/validate_skill.py .                       # 结构、链接、编码、行数
python -m unittest discover -s tests -v                  # 脚本单元测试
python scripts/check_frontend.py <项目或文件> --json      # 只读扫描目标项目
```

`check_frontend.py` 用正则筛查超 500 行、三元表达式、跨字段候补、ID 转数字、硬编码色值、`!important` 与可能缺失的中文注释。它是启发式工具，结果需要结合上下文判断，不能代替项目自己的 lint / 测试，也不能代替视觉对照。

## 限制

- 规则不能保证模型完全遵守，生成的代码仍需审查与测试。
- 已验证的是文件结构、脚本与导出完整性；`evals/` 中的场景尚未在各厂商模型上实际跑过评测。
- 示例模板使用 Vue，仅作示例，不代表技术栈要求。

## 许可

MIT，见 [LICENSE.txt](LICENSE.txt)。
