"""验证跨客户端导出完整性、分部拆分与覆盖保护。"""
# 导入路径操作，定位技能源码。
from pathlib import Path
# 导入临时目录，隔离测试文件。
import tempfile
# 导入测试框架，执行可重复断言。
import unittest
# 导入模块加载器，读取导出脚本。
import importlib.util

# 当前技能源码目录。
ROOT = Path(__file__).resolve().parents[1]
# 导出脚本加载规格。
SPEC = importlib.util.spec_from_file_location('export_rules', ROOT / 'scripts/export_rules.py')
# 待测导出脚本模块。
EXPORTER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(EXPORTER)
# 每个客户端合并后必须包含的关键规则片段。
REQUIRED_SNIPPETS = [
    '中文注释', '500', '字符串', 'mock.js', '本规范不指定任何组件库', '沿用项目既有规范与封装',
    '相邻已有页面', '保证单例', '只负责发请求', '确认唯一基准', 'UI 样式以项目现状为准',
    'UI 还原七步', '模板化特征校准', '硬编码色值', '版本对应语法', '纯函数', '只提示一次', '交付说明并请用户确认',
    'rpx', '#ifdef APP-PLUS', 'onBackPress', 'Taro',
    '长连接', '空状态', 'placeholder', '标签与按钮', '滚动条出现在内容区域',
]


class ExportTests(unittest.TestCase):
    """覆盖客户端输出、分部拆分、硬约束保留、行数与覆盖保护。"""

    def test_export_clients(self):
        """每个客户端生成全部分部文件，合并后保留规则且每个文件不超过 500 行。"""
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / 'outputs'
            manifest = EXPORTER.export_rules(ROOT, output)
            parts = manifest['parts']
            self.assertEqual(parts, len(EXPORTER.PARTS))
            self.assertEqual(len(manifest['files']), len(EXPORTER.TARGETS) * parts + 1)
            for client, filename in EXPORTER.TARGETS.items():
                merged = ''
                for index in range(1, parts + 1):
                    path = output / client / EXPORTER.part_filename(filename, index)
                    text = path.read_text(encoding='utf-8')
                    self.assertLessEqual(len(text.splitlines()), 500)
                    self.assertIn(f'第 {index}/{parts} 部分', text)
                    if client == 'cursor':
                        self.assertTrue(text.startswith('---\n'))
                        self.assertIn('alwaysApply: true', text)
                    merged += text
                for snippet in REQUIRED_SNIPPETS:
                    self.assertIn(snippet, merged, f'{client} 缺少 {snippet}')
            self.assertEqual(manifest['part_lines'], [len(p.splitlines()) for p in EXPORTER.aggregate_parts(ROOT)])

    def test_part_filename(self):
        """第一部分保留原名，后续部分追加序号且保留扩展名。"""
        self.assertEqual(EXPORTER.part_filename('AGENTS.md', 1), 'AGENTS.md')
        self.assertEqual(EXPORTER.part_filename('AGENTS.md', 2), 'AGENTS-2.md')
        self.assertEqual(EXPORTER.part_filename('front-rule.mdc', 2), 'front-rule-2.mdc')

    def test_part_limit(self):
        """每个分部都低于上限，且任一分部超限时抛错而非截断。"""
        for part in EXPORTER.aggregate_parts(ROOT):
            self.assertLessEqual(len(part.splitlines()), EXPORTER.PART_LIMIT)
        original = EXPORTER.PART_LIMIT
        EXPORTER.PART_LIMIT = 10
        try:
            with self.assertRaises(ValueError):
                EXPORTER.aggregate_parts(ROOT)
        finally:
            EXPORTER.PART_LIMIT = original

    def test_refuse_overwrite(self):
        """非空输出目录不得被覆盖。"""
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            (output / 'user.md').write_text('用户规则', encoding='utf-8')
            with self.assertRaises(ValueError):
                EXPORTER.export_rules(ROOT, output)

    def test_no_self_export(self):
        """拒绝将输出写入技能源码内形成递归。"""
        with self.assertRaises(ValueError):
            EXPORTER.export_rules(ROOT, ROOT / 'generated')


if __name__ == '__main__':
    unittest.main()
