# 代码规范

补充十条硬约束之外的通用编码规范。硬约束在任何项目（含已有项目）都必须满足；本文件的 JS / TS 规范在项目未规定处生效，项目已有 lint / 格式化 / 命名约定时以项目为准；「样式」一节在已有项目中完全让位于项目现状，不用于反向改造已有 UI。

## 版本与语法基线

- 编码前从 `package.json` 与锁文件读出框架及主要库的实际安装版本，打开该版本的官方文档确认 API 与推荐写法；记忆中的写法与文档不一致时以文档和 `node_modules` 内的类型定义为准。
- 常见分叉：Vue 2 Options API / Vue 3 Composition API 与 `<script setup>`；React 类组件 / 函数组件、React 18+ 并发特性与 19 的新 hooks；Angular NgModule / standalone、Signals；Vue Router 3/4、Pinia / Vuex、React Router 大版本。只用项目版本支持的能力。
- 不引入项目编译目标或运行时不支持的语法（装饰器提案、新 ECMAScript 特性、实验性 API）；需要时先确认升级。

## 命名

- 组件文件与组件名 PascalCase（`RecordDetailDrawer`）；hooks / composables `use*`；常量 UPPER_SNAKE_CASE；布尔 `is / has / can / should*`；事件处理函数 `handle*`，对外事件名按项目约定（如 `update:modelValue`、`onChange`）。
- 名称表达业务含义：`pendingApprovalCount` 而非 `count1`；`handleDeleteRecord` 而非 `handleClick2`；不用 `temp`、`data`、`info`、`obj` 作为业务变量名。
- 文件名大小写、目录命名与扩展名沿用项目；同一目录内不混用两种风格。
- API 函数名与后端动作对应（`getRecordPage`、`createRecord`），不以 UI 动作命名接口。

## 类型

- TS 项目：props、emits、API 请求 / 响应、store state、函数参数与返回值显式类型；接口类型来自契约，一个响应一个类型，不手写“宽松版”。
- 禁止 `any` 兜底与 `as unknown as`；确实未知时用 `unknown` 并在边界收窄。可选字段与可空字段按契约区分 `?` 与 `| null`。
- JS 项目用 JSDoc 补齐同等信息；枚举值集中定义，不在多处散落字符串字面量。
- ID 字段类型统一 `string` / `string[]`，与 [API 契约](api-contract.md) 一致。

## 组件结构

- 单文件内块顺序按项目约定（如 template / script / style）。脚本内顺序：imports → 类型 / 常量 → props / emits → 响应式状态 → computed → watch → 方法 → 生命周期 → expose。
- 模板只做绑定、循环与简单分支；复杂条件、格式化、组合逻辑进 computed 或具名函数。
- props 只读，不在子组件修改；需要双向绑定时用项目认可的 `v-model` / 受控模式。事件携带的数据结构在 emits 中声明。
- 一个组件一个职责；超过三个业务动作或 500 行时拆分，见 [代码、注释与组织](development.md)。
- Vue 项目 `template` 只保留一个根节点；需要并列元素时用容器包裹，不依赖 Fragment 让 attrs 透传失效。
- 二次封装（包装第三方或全局组件）必须透传 attrs、class / style、事件、具名与作用域插槽，并按需 `expose` 底层实例方法；细则见 [UI 组件](ui-components.md)。
- 不在组件内直接操作全局 DOM、window 或其他组件内部；需要时通过 ref / expose / 事件。

```ts
/** 列表行的删除按钮点击处理，向父级抛出已确认的记录 ID。 */
function handleDeleteRecord(recordId: string) {
  if (recordId === '') {
    return
  }
  emit('delete', recordId)
}
```

## 原子函数与纯函数

- 一个函数只做一件事，名字就是它做的事：取数、转换、校验、提交、编排各自独立；流程函数只按顺序调用原子函数，不夹带细节分支。
- 原子函数输入明确、输出可预期、可单独测试；副作用（请求、store 写入、DOM、本地存储）收敛到少数明确命名的边界函数。
- React：组件与自定义 hooks 是纯函数，相同 props / state 渲染相同结果；渲染期间不修改外部变量、不发请求、不改 props、不原地修改 state 对象，一律不可变更新；副作用只在事件处理与 effect 中执行，effect 有完整依赖与清理。
- Vue computed 与 watch getter、Angular pipe 与模板表达式保持纯，不在其中写请求、赋值或提示。

```ts
/** 按已确认契约把查询表单转换为请求参数；纯函数，不触发请求。 */
function buildRecordQuery(form: RecordQueryForm, pagination: Pagination): RecordQueryParams {
  return { keyword: form.keyword, status: form.status, pageNum: pagination.pageNum, pageSize: pagination.pageSize }
}
```

## 复杂度控制

- 不写 `reduce` 套 `reduce` / `map` / `filter`；需要多步聚合时拆成具名步骤，或改用 `for...of` 配合 `Map` / `Set`。
- 递归只用于天然树形数据，必须有终止条件与循环引用保护；深度不可控时改为显式栈 / 队列迭代；不写递归中再递归的双层结构。
- 场景匹配时使用对应数据结构与设计模式：映射表 / 策略模式替代长 `if-else` 或 `switch` 链；状态机管理多状态流转；`Map` / `Set` 做查找、去重与分组，不用数组 `includes` 嵌套循环；树 / 图用邻接结构；观察者 / 事件总线只用项目已有机制。模式必须解决实际问题，不为用模式而用。
- 单个函数不超过约 40 行、嵌套不超过 3 层、圈复杂度可一屏读懂；超出即拆。

## 简单实用

- 代码写给读者：直白命名、线性流程、必要的中间变量，优于巧妙的一行；宁可多两行也不让人停下来猜。
- 不炫技：不用链式三元、逗号表达式、位运算技巧、隐式类型转换、过度泛型与类型体操、不必要的柯里化与高阶抽象；不用项目未采用的新语法。
- 抽象只在出现真实重复后引入；一个页面只用一次的工具不进公共目录。

## 样式

- 颜色、字号、间距、圆角、阴影、层级一律使用项目 tokens / 语义变量；禁止在组件中写魔法数与硬编码色值，禁止 `!important`。
- 样式作用域化（scoped / CSS Modules / 原子类 / BEM，按项目）；不写未限定的全局标签选择器，不覆盖第三方组件内部结构，除非项目已有约定的覆盖层。
- 多个组件重复出现的 Sass / Less / CSS 片段提取到项目公共样式目录：可变值用变量，带参数的规则用 mixin，纯结构复用用 `%placeholder` + `@extend`（仅同一编译单元内），跨预处理器的通用规则用公共 class；提取后各组件只引用，不再复制。先查项目已有的 variables / mixins 文件，不新建第二套。
- 选择器优先级平直：避免深层嵌套与 ID 选择器；区块间距只由一方负责（父级 gap 或子级 margin），不两头都写。
- 布局用 flex / grid 表达内容关系；绝对定位只用于浮层、角标等确实脱离流的元素。不用 `overflow: hidden` 掩盖溢出，不用固定高度硬凑。
- 响应式按项目断点变量；不复制字面断点值。uni-app 项目尺寸单位一律 `rpx`（750 基准），Taro 按项目 `designWidth` 换算策略；不能用 `*` 选择器，细则见 [跨端适配](cross-platform.md)。

## 语义与可访问性

- 用语义标签：`button` 做动作、`a` 做跳转、`nav / main / section / table / form / label`；不用 `div` 加点击事件代替按钮。
- 图标按钮必须有可读名称（`aria-label` 或可见文字）；图片有有意义的 `alt`，装饰图 `alt=""`。
- 表单控件与 label 关联；错误信息与控件关联（`aria-describedby` 或项目表单组件机制）。
- 所有交互可键盘到达与触发，焦点可见且顺序合理；浮层打开时焦点进入、关闭时归还。
- 文本对比度达到 WCAG AA；动效尊重 `prefers-reduced-motion`；不依赖颜色单独传达状态。

## 性能

- 列表 `key` 使用稳定唯一的实体 ID（字符串），不用索引；图片声明宽高、按需懒加载。
- 不在模板中创建函数、对象或数组字面量；重计算放 computed / memo。
- 路由级与大体积组件按项目约定懒加载；第三方库按需引入。
- 请求去重与防乱序见 [API 契约](api-contract.md)；监听与定时器在卸载时清理。

## 插件与 API 封装层

- 全局插件（权限、埋点、消息、HTTP 客户端等）按项目插件机制维护为 class：构造函数接收配置，`install` / 初始化方法内部检查实例标记，保证单例——重复安装或多处导入都返回同一实例，不重复注册组件、指令或监听器。插件只做全局注册与适配，业务逻辑不进插件。
- API 封装层只做接口请求：一个函数对应一个接口，接收调用方给好的参数、返回统一 HTTP 客户端的响应（或拦截器约定后的 data），不做字段重命名、参数拼装、日期格式化、枚举翻译或业务判断。需要的转换放在调用方 hooks 或具名纯函数中，且遵守 [API 契约](api-contract.md) 的直绑原则。

```ts
/** 分页查询记录；只转发已确认契约的参数，不做任何转换。 */
export function getRecordPage(params: RecordQueryParams) {
  return http.get<RecordPageResponse>('/records/page', { params })
}
```

## 错误处理与副作用

- 每个异步动作：`loading` 置位 → try 请求 → catch 不吞错（交由拦截器或向上抛） → `finally` 释放。失败不进入成功流程、不关闭浮层、不清空用户输入。
- 交互提示只出现一次：接口响应已携带提示文案，或 HTTP 拦截器已统一弹出，业务层不再追加；接口未提供提示时，前端按功能语义补充（“保存成功”“已删除”“导出已开始”），不留无反馈的操作。先读拦截器实现再决定，不凭感觉加 message。
- 删除、冻结、批量提交等危险操作有确认与重复提交保护。
- 不写 `console.log` 调试残留；不留注释掉的代码块与无用导入。

## 提交前自检

- 项目实际配置的 lint / 格式化 / 类型检查（ESLint、Prettier、Biome、Stylelint、oxlint、tsc 等，以项目为准）错误与警告清零；不用禁用注释规避，确需禁用说明原因并获确认。
- 语法与已安装版本一致；函数单一职责、React 纯函数、无嵌套 reduce / 递归；提示不重复。
- 新增文件 ≤500 行；无 `any`、魔法数、硬编码色值、`!important`、跨字段候补、数值 ID 转换。
- 中文注释与行为一致；命名能让不了解上下文的人读懂业务动作。
