# uni-app / Taro 跨端项目适配

本规范的全部硬约束与代码规范同样适用于 uni-app、Taro 项目；本文件只补充跨端特有的核实项与写法。uni-app 官方文档：https://uniapp.dcloud.net.cn/ ；Taro 官方文档：https://docs.taro.zone/ 。

## 先识别项目与目标平台

1. uni-app：读 `manifest.json`（`vueVersion`、`app-plus` 配置、各平台 appid）、`pages.json`（页面、分包、tabBar、`globalStyle`、`navigationStyle`）、`uni.scss`；CLI 项目再读 `package.json` 中 `@dcloudio/*` 版本，HBuilderX 项目没有 `package.json` 时以 HBuilderX 版本与 `manifest.json` 为准。区分 uni-app（Vue 2 / Vue 3）与 uni-app x（uvue / uts），二者语法与 API 不通用。
2. Taro：读 `config/index.*`（`framework`：react / vue3、`designWidth`、`deviceRatio`）、`app.config.*`、`package.json` 中 `@tarojs/*` 版本。
3. 列出项目实际要编译的目标：App Android / App iOS / 微信等小程序 / H5。每个需求都要说明在这些目标上分别如何表现；不能只在 H5 或微信开发者工具里跑通就算完成。
4. 页面类型：uni-app 的 vue 页面（webview 渲染）、nvue 页面（原生渲染，CSS 子集、只支持 flex、不支持百分比与全局样式）、uvue 页面各有限制，先看文件后缀再决定写法。

## 写代码前先查官方文档

- 用到任何 `uni.xx` / `Taro.xx` API、内置组件（`view`、`scroll-view`、`picker`、`web-view` 等）、页面生命周期（`onLoad`、`onShow`、`onReachBottom`、`onBackPress` 等）前，先打开对应官方文档页，核对：参数与返回值、**平台兼容表**（App / 各小程序 / H5 分别是否支持、最低版本）、异步 / 同步版本差异、已废弃或被拆分的 API（如系统信息类 API 在新版本按已安装版本文档选择）。
- 凭记忆写 Web API 是跨端项目最常见的错误：没有 `window`、`document`、`localStorage`、DOM 事件与 `axios` 默认适配器；用 `uni.request` / `Taro.request`、`uni.setStorage`、`uni.createSelectorQuery` 等替代。项目已有请求 / 存储封装时沿用封装。
- 第三方组件与插件只用项目已引入的（uni-ui、uView、NutUI、Taro UI 等以项目 `package.json` / `uni_modules` 为准），并核对该组件的平台支持说明，不默认所有端都可用。
- 查到“不支持”或“部分支持”时，不自行 polyfill；按条件编译或平台分支实现，并在交付中写明哪个端有差异。

## 请求 loading（uni-app）

- 除长连接（`uni.connectSocket` / WebSocket、SSE、长轮询）外，每个接口请求都必须有 loading：请求前 `uni.showLoading`（按需 `mask: true` 防重复点击），成功、失败、超时都在 `complete` / `finally` 中 `uni.hideLoading`。
- 先读项目请求封装：已统一 showLoading / hideLoading 时业务层不再重复调用；需要静默请求时用封装提供的开关，不绕过封装。
- 并发请求用计数或封装的队列控制，最后一个请求结束才关闭，避免先返回的请求关掉其它请求的 loading。
- `uni.showLoading` 与 `uni.showToast` 同一时间只能显示一个：先 `hideLoading` 再 `showToast`，否则提示会被覆盖或关闭；下拉刷新结束同时调用 `uni.stopPullDownRefresh`。

## 条件编译与平台分支（uni-app）

- 语法：js / uts 用 `// #ifdef %PLATFORM%` … `// #endif`，css 与各预处理器必须用 `/* #ifdef %PLATFORM% */` … `/* #endif */`，模板用 `<!-- #ifdef %PLATFORM% -->` … `<!-- #endif -->`；`#ifndef` 为排除，`||` 多平台，`pages.json` 与 `static/` 子目录也支持。
- 常用平台名：`APP-PLUS`（App，含 nvue）、`APP-NVUE`、`WEB` / `H5`、`MP-WEIXIN`、`MP`（全部小程序）、`VUE3`；uni-app x 另有 `UNI-APP-X`、`APP-ANDROID`、`APP-IOS`。
- 重要：uni-app（js 引擎版）**不能用条件编译区分 Android 与 iOS**，`APP-ANDROID` / `APP-IOS` 只在 uts 文件与 uni-app x 中生效；运行时区分用系统信息 API 的 `platform` 字段（按已安装版本文档选择 `uni.getSystemInfoSync` 或拆分后的 API）。
- 条件编译前后文件都必须语法正确：json 不能留多余逗号，js 不能重复 import；`plus.*`、`weex`、微信原生组件等平台专有代码一律包在对应 `#ifdef` 内。
- Taro 用 `process.env.TARO_ENV`（`weapp` / `h5` / `rn` 等）做平台分支，配合各平台 `config` 与文件后缀多态（`index.weapp.tsx`）。

## 样式与单位

- uni-app 项目 CSS 一律使用 `rpx`：以 750 宽为基准，`750rpx` = 屏幕宽度。换算公式 `rpx = 750 × 设计稿尺寸 / 设计稿宽度`（750 稿 1:1，375 稿 ×2，640 稿 ×1.17）。字号、固定高度、1px 边框按设计意图决定：需要随屏宽缩放用 `rpx`，需要固定时用 `px`，并说明理由。
- 例外必须按文档：`pages.json` 的 `titleNView` 与 `plus` API 只支持 `px`；nvue weex 模式的 `px` 语义等同 rpx；HBuilderX 旧项目的 `upx` 统一改为 `rpx` 需用户确认。
- Taro 项目按 `designWidth` / `deviceRatio` 配置：默认写 `px` 由编译器换算为 rpx / rem，不想换算写 `Px` / `PX`，JS 中用 `Taro.pxTransform`；项目已直接写 `rpx` 则沿用。同一项目不混用两套单位策略。
- 选择器限制：不能用 `*`；微信自定义组件内只支持 class 选择器；`page` 相当于 `body`，页面级 `page {}` 不能加 `scoped`。布局优先 flex。
- 小程序 CSS 不能引用本地背景图与字体文件（<40kb 会自动转 base64，更大需网络地址或自行 base64）；网络字体必须带 `https`。
- 状态栏 / 导航 / tabBar 高度用内置变量 `--status-bar-height`、`--window-top`、`--window-bottom`，不写死数值；nvue 不支持这些变量，用系统信息的 `statusBarHeight` 绑定。
- 模板单根节点、不用 DOM 选择器、不依赖 `document` 查询尺寸，用 `uni.createSelectorQuery().in(this)` / Taro 等价 API。

## App Android 端必须核对的项

- 权限：`manifest.json → app-plus → distribute → android → permissions` 声明所需 Android 权限；运行时权限（相机、相册、定位、存储等）在调用前按官方文档流程申请与处理拒绝分支，`plus.android.*` 只能出现在 `#ifdef APP-PLUS` 内。隐私合规（`androidPrivacy.json` 隐私弹窗、`targetSdkVersion`）按项目现有配置与官方最新说明核实，不自行猜测。
- 返回键：Android 物理 / 手势返回触发页面 `onBackPress`，需要拦截（二次确认、关闭弹层、自定义返回）时在其中处理并返回 `true`；tabBar 首页的退出确认按项目既有实现。
- 布局：自定义导航（`navigationStyle: custom`）时顶部留 `--status-bar-height`；底部按 `--window-bottom` 与安全区（`safeAreaInsets`）处理；键盘弹起用输入组件的 `adjust-position` / `cursor-spacing`，不自行监听 window resize。
- 性能与渲染：长列表优先 `scroll-view` + 分页或项目已有虚拟列表；vue 页面 webview 渲染，频繁动画 / 大列表可评估 nvue（其 CSS 限制见上）；App 端 `box-shadow`、`filter`、`position: fixed` 等在 Android 低版本 webview 表现需真机确认。
- 网络与文件：App 端 `uni.request` 无跨域限制但需核实后端对 App 的鉴权方式；文件路径区分 `_doc/`、`_downloads/`、`_www/`；下载 / 打开文件用 `uni.downloadFile` + `uni.openDocument` 或 `plus.runtime`，均在条件编译内。
- 验证：Android 端只有真机或自定义基座运行才算验证，模拟器与 H5 不能代替；交付时分端报告（Android / iOS / 小程序 / H5）各自验证状态。

## 交付与审查补充

- 说明本次改动覆盖的平台、使用了哪些 `uni.xx` / `Taro.xx` API 及其兼容结论、条件编译块的位置与原因、`rpx` 换算依据。
- 审查项：无 Web 专有 API 与 DOM 操作、无 `px` 误用、平台专有代码都在条件编译内、非长连接请求都有 loading 且必定关闭、Android 权限与返回键已处理、每个目标端有验证或已标注未验证。
