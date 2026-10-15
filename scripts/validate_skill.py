"""验证本包结构、编码、资源引用与维护文件行数。"""

# 导入命令行解析，指定 skill 目录。
import argparse
# 导入 JSON 解析，验证评测场景及 JSON 文件。
import json
# 导入正则，检查名称、简明元数据与资源链接。
import re
# 导入路径对象，实现跨平台只读校验。
from pathlib import Path


def validate(root):
    """校验本包的可移植结构，不执行资源中的业务代码。"""
    root = Path(root)
    errors = []
    main = root / "SKILL.md"
    if not main.exists():
        return ["缺少 SKILL.md"]
    content = main.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        errors.append("frontmatter 必须从首字节开始，不能有 BOM")
    parts = content.split("\n---\n", 1)
    if len(parts) != 2:
        return errors + ["frontmatter 未闭合"]
    metadata = parts[0][4:]
    for field in ["name", "description", "version", "author", "license", "platforms"]:
        if not re.search(rf"^{field}:\s*\S", metadata, re.M):
            errors.append(f"缺少元数据 {field}")
    name = re.search(r"^name:\s*(.*)$", metadata, re.M)
    if name and not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name.group(1)):
        errors.append("name 必须为小写连字符标识")
    description = re.search(r"^description:\s*(.*)$", metadata, re.M)
    # Agent Skills 规范允许 description 最长 1024 字符；过短的描述不利于触发匹配。
    if description and len(description.group(1).strip('\"')) > 1024:
        errors.append("description 超过 1024 字符")
    if not parts[1].strip():
        errors.append("缺少正文")
    required = ["references", "templates", "scripts", "tests", "evals", "agents"]
    for directory in required:
        if not (root / directory).is_dir():
            errors.append(f"缺少资源目录 {directory}")
    for path in sorted(root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.suffix not in {".md", ".py", ".json", ".yaml", ".vue", ".js", ".txt"}:
            continue
        text = path.read_text(encoding="utf-8")
        if text.startswith("\ufeff"):
            errors.append(f"{path.relative_to(root)} 包含 BOM")
        if len(text.splitlines()) > 500:
            errors.append(f"{path.relative_to(root)} 超过 500 行")
        if path.suffix == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as error:
                errors.append(f"{path.name} JSON 无效: {error}")
        if path.suffix == ".md":
            for link in re.findall(r"\[[^\]]*\]\(([^)]+)\)", text):
                if "://" in link or link.startswith("#"):
                    continue
                target = link.split("#", 1)[0]
                if not (path.parent / target).exists():
                    errors.append(f"{path.relative_to(root)} 链接缺失: {target}")
    return errors


def main():
    """输出结构检查结果，失败时返回非零状态。"""
    parser = argparse.ArgumentParser()
    parser.add_argument("path", nargs="?", default=".")
    args = parser.parse_args()
    errors = validate(args.path)
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return int(bool(errors))


if __name__ == "__main__":
    raise SystemExit(main())
