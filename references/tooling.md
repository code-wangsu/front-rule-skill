# 检查工具使用与边界

## validate_skill.py

Python 标准库，无网络、无第三方包、无项目写入；检查 SKILL.md 必需元数据、名称、描述长度、资源链接、UTF-8、JSON 语法、每文件 500 行。
只解析本包规定的简明 frontmatter；不宣称是通用 YAML 解析器。复杂 YAML 由使用客户端或已有 YAML validator 再校验。

## check_frontend.py

只读扫描 vue/nvue/uvue/js/ts/uts/jsx/tsx/mjs/cjs/css/scss/less/html/json/md，跳过 .git、node_modules、dist/build、coverage、缓存、lock 文件。uni-app 的 `unpackage` 等构建目录用 `--exclude` 排除。
用 --exclude 增加已确认的生成目录；默认不替用户删除或拆文件。
报告两层：error 是行数超限；review 是正则发现的三元表达式、多字段候补、ID 数值转换、硬编码色值、`!important`、可能缺中文注释。
硬编码色值与 `!important` 只在源码和样式文件中筛查，文件名含 token / theme / variables / palette 的 token 真源文件不报；Markdown 不报。
正则不是 AST，字符串、类型、注释、跨行定义可能误报或漏报。review 必须读上下文，不自动修改，也不证明所有函数都有注释。
中文注释准确性、回调/getter、导出逐项含义和模板关键区分由人工/Agent补审。
--strict-review 可让待审项返回非零，适合作为确认前阻断，不表示已证实语义违规。
机器生成文件无需手工拆，须明确排除而非把业务超限文件加入忽略名单。

## export_rules.py

按 `PARTS` 分组把 SKILL.md 主体与 references 导出为每客户端多个部分，每部分独立校验 ≤490 行，超限直接报错而不截断；需要新增内容时优先调整分组或新增部分，不删规则。
输出目录必须为空且不在技能源码内；`manifest.json` 的 `parts` / `part_lines` 用于核对导出完整性。

## 命令

通过 terminal 执行，在 skill 根目录：

```text
python scripts/validate_skill.py .
python scripts/check_frontend.py <source-directory> --json
python scripts/check_frontend.py <file.vue> --strict-review
python -m unittest discover -s tests -v
```

默认 stdout 打印路径/行数和风险，不输出源码或凭据。不扫描 .env、证书、二进制或密钥目录。
扫描结果与 lint/test/build 是补充关系，不能代替真实接口核验和 UI 可见性验证。
