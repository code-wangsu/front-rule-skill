"""只读扫描前端代码风险；正则结果需要结合语义人工确认。"""

# 导入命令行解析，以选择扫描目录和严格审查模式。
import argparse
# 导入 JSON 输出，便于 CI 和 Agent 汇总扫描结果。
import json
# 导入正则表达式，仅用于启发式风险筛查。
import re
# 导入路径对象，以跨平台遍历源码而不调用 shell。
from pathlib import Path

# 默认跳过第三方、版本控制、构建产物与缓存目录。
SKIP_DIRS = {".git", "node_modules", "dist", "build", "coverage", ".cache", "__pycache__"}
# 可读维护文件后缀，不读取环境变量和二进制凭据。
SUFFIXES = {".vue", ".nvue", ".uvue", ".js", ".ts", ".uts", ".jsx", ".tsx", ".mjs", ".cjs", ".css", ".scss", ".less", ".html", ".json", ".md"}
# 识别中文注释的最低文字特征，不判断注释业务正确性。
CHINESE = re.compile(r"[\u4e00-\u9fff]")
# 识别对象字段候补链；它是待审风险，不是 AST 语义判定。
FALLBACK = re.compile(r"(?:\b[\w$]+(?:\?\.)?\.[\w$]+|\b[\w$]*[Ii][Dd])\s*(?:\|\||\?\?)\s*(?:[\w$]+(?:\?\.)?\.[\w$]+|[\w$]*[Ii][Dd])")
# 筛查可能的三元表达式，排除部分可选链和空值合并。
TERNARY = re.compile(r"(?<!\?)\?(?![?.])[^\n;]*:")
# 筛查 ID 转数字代码，仍需确认字段实体标识语义。
ID_NUMBER = re.compile(r"\b(?:Number|parseInt|parseFloat)\s*\([^\n)]*(?:\bid\b|\w+Id\b|\w+ID\b)", re.I)
# 声明筛查覆盖 import/export/函数/常量；多行回调需另行审查。
DECLARATION = re.compile(r"^\s*(?:import\b|export\b|(?:async\s+)?function\b|(?:const|let|var)\s+)")
# 筛查组件与样式中的硬编码色值；token 真源文件不在此列。
HARDCODED_COLOR = re.compile(r"(?<![\w&])#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b|\b(?:rgba?|hsla?)\(")
# 筛查 !important；它通常意味着优先级冲突被硬压而非被解决。
IMPORTANT = re.compile(r"!\s*important\b")
# 样式类规则只应用于源码与样式文件，不扫描文档与数据文件。
STYLE_SUFFIXES = {".vue", ".nvue", ".uvue", ".jsx", ".tsx", ".js", ".ts", ".uts", ".css", ".scss", ".less", ".html"}
# 文件名含以下词视为 tokens / 主题真源，允许出现字面色值。
TOKEN_FILE_HINTS = ("token", "theme", "variable", "palette", "color")


def is_style_target(path):
    """判断文件是否需要执行硬编码色值与 !important 筛查。"""
    candidate = Path(path)
    if candidate.suffix.lower() not in STYLE_SUFFIXES:
        return False
    stem = candidate.stem.lower()
    for hint in TOKEN_FILE_HINTS:
        if hint in stem:
            return False
    return True


def preceding_chinese_comment(lines, index):
    """检查声明正上方是否存在包含中文的邻接注释。"""
    cursor = index - 1
    while cursor >= 0 and not lines[cursor].strip():
        cursor -= 1
    if cursor < 0:
        return False
    text = lines[cursor].strip()
    if text.endswith("*/"):
        block = []
        while cursor >= 0:
            block.append(lines[cursor])
            if "/*" in lines[cursor]:
                break
            cursor -= 1
        return bool(CHINESE.search("\n".join(block)))
    if text.startswith("//"):
        return bool(CHINESE.search(text))
    return False


def scan_text(text, path="<input>"):
    """报告物理行数和启发式风险，不修改源码或输出源码内容。"""
    lines = text.splitlines()
    issues = []
    if len(lines) > 500:
        issues.append({"path": path, "line": 501, "severity": "error", "rule": "file-lines", "message": f"文件共 {len(lines)} 行，超过 500 行"})
    # 通用逻辑风险对所有文件生效；样式风险仅对源码与样式文件生效。
    checks = [(FALLBACK, "field-fallback", "可能存在跨字段候补取值"), (TERNARY, "ternary", "可能存在三元表达式"), (ID_NUMBER, "numeric-id", "可能将实体 ID 转为数字")]
    if is_style_target(path):
        checks.append((HARDCODED_COLOR, "hardcoded-color", "可能存在硬编码色值，应使用项目 token"))
        checks.append((IMPORTANT, "important", "使用了 !important，应解决选择器优先级"))
    for index, line in enumerate(lines):
        if line.lstrip().startswith(("//", "*", "<!--")):
            continue
        for pattern, rule, message in checks:
            if pattern.search(line):
                issues.append({"path": path, "line": index + 1, "severity": "review", "rule": rule, "message": message})
        if DECLARATION.search(line) and not preceding_chinese_comment(lines, index):
            issues.append({"path": path, "line": index + 1, "severity": "review", "rule": "chinese-comment", "message": "声明前可能缺少独立中文注释"})
    return {"path": path, "lines": len(lines), "issues": issues}


def scan_path(root, excludes=()):
    """扫描单文件或目录，跳过已声明的第三方和生成目录。"""
    root = Path(root)
    if not root.exists():
        raise FileNotFoundError(root)
    excluded = SKIP_DIRS.union(excludes)
    candidates = [root] if root.is_file() else sorted(root.rglob("*"))
    reports = []
    for path in candidates:
        if not path.is_file() or path.suffix.lower() not in SUFFIXES:
            continue
        if any(part in excluded for part in path.parts):
            continue
        if path.name in {"package-lock.json", "yarn.lock", "pnpm-lock.yaml"}:
            continue
        reports.append(scan_text(path.read_text(encoding="utf-8-sig"), str(path)))
    return reports


def main():
    """运行只读检查，严重问题返回非零，待审项按选项阻断。"""
    parser = argparse.ArgumentParser(description="前端规范启发式检查，不自动修改代码")
    parser.add_argument("path")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--strict-review", action="store_true")
    args = parser.parse_args()
    reports = scan_path(args.path, args.exclude)
    issues = [issue for report in reports for issue in report["issues"]]
    summary = {"files": len(reports), "errors": sum(i["severity"] == "error" for i in issues), "review": sum(i["severity"] == "review" for i in issues), "reports": reports}
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        print(f"扫描 {summary['files']} 文件；超限 {summary['errors']}；待审 {summary['review']}")
        for issue in issues:
            print(f"{issue['severity']} {issue['path']}:{issue['line']} {issue['rule']} {issue['message']}")
    if summary["errors"] or (args.strict_review and summary["review"]):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
