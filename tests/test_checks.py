"""验证检查脚本的边界与风险识别，使用临时目录隔离文件写入。"""

# 导入文件路径模块，定位当前 skill 和测试临时目录。
from pathlib import Path
# 导入临时目录工具，避免改变真实项目。
import tempfile
# 导入单元测试框架，使用 Python 标准库执行。
import unittest
# 导入模块加载器，读取待测试脚本。
import importlib.util


def load_script(name):
    """从当前 skill scripts 目录加载测试目标。"""
    path = Path(__file__).resolve().parents[1] / "scripts" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# 加载只读前端检查模块，用于风险边界断言。
checker = load_script("check_frontend")
# 加载技能结构检查模块，用于资源链接断言。
validator = load_script("validate_skill")


class CheckTests(unittest.TestCase):
    """覆盖行数、候补字段、注释、ID 转换与扫描排除。"""

    def test_line_limit(self):
        """500 行合法，501 行必须阻断。"""
        self.assertFalse(checker.scan_text("x\n" * 500)["issues"])
        self.assertEqual(checker.scan_text("x\n" * 501)["issues"][0]["rule"], "file-lines")

    def test_fallback(self):
        """识别字段候补链，不将纯布尔条件判成字段候补。"""
        report = checker.scan_text("detailId || id || mountId\nrow.storyId ?? row.id")
        self.assertEqual(sum(i["rule"] == "field-fallback" for i in report["issues"]), 2)
        self.assertFalse(checker.FALLBACK.search("isOpen || isLoading"))

    def test_comments(self):
        """中文注释能够覆盖相邻声明，无注释必须待审。"""
        good = "/** 导入响应式状态。 */\nimport { ref } from 'vue'"
        self.assertFalse(checker.scan_text(good)["issues"])
        bad = "import { ref } from 'vue'"
        self.assertEqual(checker.scan_text(bad)["issues"][0]["rule"], "chinese-comment")

    def test_ternary_and_numeric_id(self):
        """三元和实体 ID 数值转换进入待审清单。"""
        report = checker.scan_text("value = open ? 'a' : 'b'\nvalue = Number(recordId)")
        rules = {i["rule"] for i in report["issues"]}
        self.assertIn("ternary", rules)
        self.assertIn("numeric-id", rules)

    def test_hardcoded_color_and_important(self):
        """源码与样式文件中的硬编码色值和 !important 进入待审；token 真源与文档不报。"""
        style = "/* 中文说明。 */\n.title { color: #1f2937; background: rgba(0, 0, 0, .1); }\n.card { margin: 0 !important; }"
        rules = [i["rule"] for i in checker.scan_text(style, "page.scss")["issues"]]
        self.assertEqual(rules.count("hardcoded-color"), 1)
        self.assertEqual(rules.count("important"), 1)
        self.assertFalse(checker.scan_text(style, "tokens.scss")["issues"])
        self.assertFalse(checker.scan_text("颜色约 #F4F1EA 是模板痕迹", "guide.md")["issues"])
        self.assertFalse(checker.HARDCODED_COLOR.search("<template #default>"))

    def test_skip_dependencies(self):
        """扫描不读取依赖目录和环境密钥文件。"""
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "node_modules").mkdir()
            (root / "node_modules" / "bad.js").write_text("x\n" * 501, encoding="utf-8")
            (root / ".env").write_text("SECRET=do-not-read", encoding="utf-8")
            (root / "ok.js").write_text("/** 中文说明。 */\nconst id = '9223372036854775807'", encoding="utf-8")
            self.assertEqual(len(checker.scan_path(root)), 1)

    def test_complete_skill(self):
        """当前交付包结构与链接必须全部有效。"""
        root = Path(__file__).resolve().parents[1]
        self.assertEqual(validator.validate(root), [])


if __name__ == "__main__":
    unittest.main()
