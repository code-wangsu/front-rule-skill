# 代码、注释与模块组织

## 先沿用真实项目

读取实际目录、框架、状态管理、组件注册和已安装版本；不把某个框架、状态管理或组件库写成所有项目的前提。语法以 `package.json` / 锁文件中实际安装版本对应的官方文档为准，不套用其它大版本写法。
Vue 的 Composition API/script setup、React 的函数组件/hooks、Angular 的组件/services、Svelte 的组件/reactivity 都按项目真实版本采用，不能互相套用。原生 HTML/JS、Web Components、Solid、跨端/桌面框架同样执行通用约束。
Vue SFC 的 template/script/style 顺序、CSS Modules、SCSS、Tailwind、CSS-in-JS 等按仓库有效约定；不为通用 skill 强制迁移技术栈。
命名、类型、样式、可访问性与错误处理的通用规范见 [代码规范](code-standards.md)；本文件聚焦注释粒度与模块组织。

## 注释粒度

1. 每条 import 上方说明来源和使用目的，包括副作用样式导入。
2. 每条 export / re-export 上方说明对外暴露的能力；export function 的同一注释可兼顾函数职责。
3. 模块级 / 全局变量、常量、refs、计算属性上方独立注释；props/emits 逐项注释。
4. 每个普通、异步、箭头、回调、事件、getter/setter 函数上方说明输入、结果或副作用。
5. 模板查询、列表、分页、权限分支、复杂子组件和浮层挂载点上方加 HTML 注释。
6. 关键基础控件使用也说明意图；重复循环控件在循环块上方说明共同职责，不生成几百条重复注释。
7. 注释必须与行为一致。把“查询记录”写在删除函数上视为不合格。
8. 不能用一个笼统“工具方法”注释覆盖十个声明；注释与目标保持紧邻。

```js
/** 导入 Vue 响应式状态，用于当前页加载状态。 */
import { ref } from 'vue'

/** 当前页查询是否正在执行。 */
const loading = ref(false)

/** 导出只读加载状态，供页面展示。 */
export { loading }
```

复杂内联回调提取为具名函数，既便于注释也便于测试。局部临时变量按可读性补说明，不要求所有循环下标堆注释。

## 目录建议（先服从项目）

已有项目中新增页面或模块时，先打开一个功能相近的相邻页面，照它的实际层级与命名建目录（api、components、hooks、config、样式、测试各放哪、如何命名、是否按模块聚合），并复用它引用的全局组件、第三方组件、hooks、插件、指令与工具函数。
下面的目录只是项目没有可参照页面时的默认建议，不能用来改造已有项目的组织方式。

```text
module/
  api/records.js
  pages/record-list/index.vue
  pages/record-list/components/RecordQuery.vue
  pages/record-list/components/RecordTable.vue
  pages/record-list/components/RecordDetailDrawer.vue
  pages/record-list/hooks/useRecordList.js
  pages/record-list/hooks/useCreateRecord.js
  pages/record-list/hooks/useUpdateRecord.js
  pages/record-list/config/columns.js
  pages/record-list/config/constant.js
```

- 页面负责组合，不把复杂表单、评论、附件、日志、明细塞入同一个 SFC。
- hooks/composables 保持业务局部，跨页确实复用再提升到模块公共目录。
- 配置保存不可变常量、选项、字典编码；不要把请求、watch 或可变状态塞进 constant.js。
- 动态列依赖翻译/格式化时使用列工厂；不创建第二套静态字段真源。
- API 文件仅封装接口请求，不做参数与数据转换；不要为单个接口引入万能工厂。
- 插件以 class 维护并保证单例，只承载真实全局注册和适配；不能把业务逻辑逃逸到巨型 plugin 文件。
- 多组件共用的样式提取为变量 / mixin / 继承或公共样式文件，放在项目既有的样式目录。

## 单一职责

查询、新增、编辑、删除、导出分别命名入口及状态。允许一个业务动作串联必要步骤，但函数内不分支执行不同业务动作。
禁止 handleSubmit(mode) 同时选新增/编辑接口；可以共享视图、确定的纯校验和无动作分支的纯参数差异处理。

## 显式逻辑

```js
/** 检查记录是否具有当前接口要求的 ID。 */
function hasRecordId(record) {
  if (record.id === null || record.id === undefined || record.id === '') {
    return false
  }
  return true
}
```

不使用 `detailId || id`、`row.title ?? row.name`，不用其它字段填空；空态来自明确契约。
默认不用三元表达式；展示逻辑放简单 computed/具名函数，不把复杂条件放模板。
同字段占位不能误吞 0/false；用明确空值判断。

## 500 行拆分

按物理行计数，含中文注释。写入前预估，写入后实测。超过 500 不靠删必要注释、压缩空行或混淆一行实现过关。
按业务边界拆，保持 imports、props、emits、依赖方向清楚；拆分后测试与引用同步修改。
已有超限文件按当前范围拆，涉及公共接口变更或显著扩大影响须先向用户确认；不继续加行。
