"""导出主流客户端规则素材，不修改项目或客户端配置。"""
# 导入路径操作，实现跨平台资源读取。
from pathlib import Path
# 导入参数解析，要求用户明确输出目录。
import argparse
# 导入正则，仅剥离元数据与转换本地链接。
import re
# 导入 JSON，用于生成输出清单。
import json
# 导入目录复制，用于保留 Hermes 原生 skill 的完整资源。
import shutil

# 各客户端素材名称；不声明它们都能自动识别此目录。
TARGETS = {
    "codex": "AGENTS.md", "claude-code": "CLAUDE.md", "cursor": "front-rule.mdc",
    "gemini": "GEMINI.md", "antigravity": "frontend-rules.md",
    "glm": "system-prompt.md", "kimi": "system-prompt.md",
    "deepseek": "system-prompt.md", "qwen": "system-prompt.md", "generic": "system-prompt.md",
}
# 导出按逻辑分组拆成多个部分；第一部分固定包含 SKILL.md 主体。
PARTS = [
    ("核心约束、代码规范与跨端适配", ["code-standards.md", "development.md", "api-contract.md", "cross-platform.md"]),
    ("UI 还原、组件、流程与测试", ["ui-restoration.md", "ui-design.md", "ui-components.md", "workflow.md", "testing-review.md", "project-adaptation.md"]),
]
# 单个导出文件的行数上限；留出余量以保证始终小于 500 行。
PART_LIMIT = 490
# Cursor 规则文件的元数据头。
CURSOR_HEADER = "---\ndescription: 前端 UI 还原与代码规范、真实接口约束\nglobs: \nalwaysApply: true\n---\n"


def strip_links(text):
    """把本地 Markdown 链接退化为纯文本，保留外部链接。"""
    return re.sub(r"\[([^\]]+)\]\((?!https?://)[^)]+\)", r"\1", text)


def compact(text):
    """移除空行，保持导出紧凑且可按行计数。"""
    lines = [line for line in text.splitlines() if line.strip()]
    return "\n".join(lines) + "\n"


def aggregate_parts(root):
    """按 PARTS 分组生成多段独立提示文本，每段不超过 PART_LIMIT 行。"""
    root = Path(root)
    main = (root / "SKILL.md").read_text(encoding="utf-8").split("\n---\n", 1)[1]
    core = main.split("## 按需参考", 1)[0]
    total = len(PARTS)
    parts = []
    for index, (title, names) in enumerate(PARTS, start=1):
        chunks = []
        if index == 1:
            chunks.append(core)
        for name in names:
            chunks.append((root / "references" / name).read_text(encoding="utf-8"))
        header = f"本文件是 front-rule-skill 导出规则第 {index}/{total} 部分（{title}）；全部 {total} 个部分须一起加载，缺一不可。"
        content = compact(strip_links(header + "\n\n" + "\n\n".join(chunks)))
        if len(content.splitlines()) > PART_LIMIT:
            raise ValueError(f"导出第 {index} 部分超过 {PART_LIMIT} 行，须调整 PARTS 分组或精简内容，不能静默截断")
        parts.append(content)
    return parts


def part_filename(filename, index):
    """第一部分保留原文件名，其余部分追加序号。"""
    if index == 1:
        return filename
    path = Path(filename)
    return f"{path.stem}-{index}{path.suffix}"


def export_rules(root, output):
    """向新目录导出规则，拒绝覆盖现有文件。"""
    root = Path(root).resolve()
    output = Path(output).resolve()
    if output == root or root in output.parents:
        raise ValueError("输出不能放入技能源码目录")
    if output.exists() and any(output.iterdir()):
        raise ValueError("输出目录必须为空，禁止覆盖既有规则")
    output.mkdir(parents=True, exist_ok=True)
    parts = aggregate_parts(root)
    paths = []
    for client, filename in TARGETS.items():
        for index, content in enumerate(parts, start=1):
            target = output / client / part_filename(filename, index)
            target.parent.mkdir(parents=True, exist_ok=True)
            text = content
            if client == "cursor":
                text = CURSOR_HEADER + content
            target.write_text(text, encoding="utf-8")
            paths.append(str(target.relative_to(output)))
    # Hermes 原生 skill 保留全部资源，避免脚本引用失效。
    destination = output / "hermes" / root.name
    shutil.copytree(root, destination, ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    paths.append(str((destination / "SKILL.md").relative_to(output)))
    manifest = {
        "files": paths,
        "parts": len(parts),
        "part_lines": [len(part.splitlines()) for part in parts],
        "mode": "rule-materials-not-auto-install",
        "model_benchmarks_run": False,
    }
    (output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    return manifest


def main():
    """解析输出目录并执行显式导出。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    print(json.dumps(export_rules(root, args.output), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
