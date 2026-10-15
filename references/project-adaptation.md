# 跨行业、跨框架的项目适配

## 技术中立

1. 核实 Vue、React/Next、Angular、Svelte、Solid、原生 Web、Web Components、React Native、Flutter/Dart、跨端或桌面 UI 的实际框架和版本，并以该版本官方文档为语法依据。uni-app / Taro 项目另按 [跨端适配](cross-platform.md) 执行 rpx、条件编译、API 兼容表与 App Android 核对。
2. 所有项目执行中文注释、唯一后端字段、字符串实体 ID、500 行、确认未知业务及模块化；设计稿还原与无设计稿设计决策同样跨框架适用，tokens 真源按项目实际形式（CSS 变量、主题对象、原子类配置、原生样式资源）读取。
3. JS/TS 用标准注释；JSX 用 JSX 注释；Vue/HTML 用模板注释；Dart/原生语言用合法语言注释。
4. hooks 表示职责分离：React custom hooks、Vue composables、Angular services、Svelte 状态模块或其它框架等价能力。不把 React 生命周期套给其它框架。
5. props/emits 在其它框架对应 inputs/outputs、callbacks、bindings；保持同一单向数据边界。
6. 不将某仓库组件、useList/useNavigate、目录、权限白名单、Pinia、OpenSpec、命令和 i18n key 套给其它项目。
7. 自动检查主要覆盖 Web 文本和 JS/TS；其它语言用项目实际 lint/test，不声称正则覆盖所有框架。

## 领域中立

适用于 ERP、CRM、电商、内容、教育、医疗、门户、可视化、财务等，不内置任何领域的权限、流程或字段。
金额精度、隐私、安全、时区和行业特性来自真实需求及接口，不能由 skill 自行决定。

## 环境中立

不绑定个人绝对路径，不要求特定模型、API Key 或组件库；读取规则只需要 Markdown。
Python 仅用于可选检查/导出，没有解释器时说明未运行，不能假装执行。
项目不存在 package.json 时读取其实际依赖与构建清单，而不是强行引入 Node 工具链。
