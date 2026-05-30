import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from scripts.check_resume_html import validate

REPO_ROOT = Path(__file__).resolve().parents[1]

VALID_HTML = """<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="候选人面向产品运营岗位，具备用户增长、数据复盘和项目推进经验。">
  <title>李明 - 产品运营</title>
  <style>
    @media (max-width: 720px) { main { max-width: 100%; } }
    @page { size: A4; margin: 12mm; }
    @media print { body { color: #111; } }
  </style>
  <script type="application/ld+json">
    {"@context":"https://schema.org","@type":"Person","name":"李明","jobTitle":"产品运营"}
  </script>
</head>
<body>
<main>
  <h1>李明</h1>
  <section><h2>个人优势</h2><ul>
    <li>面向产品运营岗位，具备用户增长、活动运营、数据复盘和跨团队推进经验。</li>
    <li>策划并落地 4 场用户活动，覆盖 1,200+ 目标用户，沉淀活动复盘模板。</li>
  </ul></section>
  <section><h2>实习经历</h2><ul>
    <li>维护 3 个用户反馈渠道，标注 420+ 条问题并输出周报，推动 4 个产品修复项进入排期。</li>
  </ul></section>
  <section><h2>项目经历</h2><ul>
    <li>整理 8 周转化漏斗数据，按渠道拆解流失节点，提出 3 条优化建议。</li>
  </ul></section>
  <section><h2>工作方法</h2>
    <p>围绕岗位目标拆解日常任务，先确认业务背景、用户对象、数据口径和协作边界，再把需求整理成可执行清单，便于团队在同一节奏下推进。</p>
    <p>日常记录活动方案、用户反馈、渠道数据和复盘结论，形成清晰的问题描述、原因判断和后续动作，让每一次项目经历都能留下可追踪的过程材料。</p>
    <p>面对跨团队事项时，先对齐时间节点、输入材料和验收标准，再通过周报同步风险、依赖和下一步安排，减少反复沟通带来的信息损耗。</p>
    <p>在简历表达上保持事实优先，使用真实项目、真实动作和真实结果呈现能力，避免空泛自评，让招聘方可以快速判断岗位匹配度。</p>
    <p>求职材料围绕产品运营岗位展开，重点呈现活动策划、用户反馈整理、数据分析、项目排期沟通和复盘材料建设，内容保持可核验、可追溯、可用于面试追问。</p>
    <p>候选人关注业务目标和用户体验之间的连接，会把问题拆成背景、对象、现象、原因、动作和结果，帮助团队更快形成一致判断。</p>
    <p>过往练习中持续整理案例库、指标口径和复盘框架，便于在新项目中快速迁移方法。</p>
    <p>沟通材料会保留背景说明、关键结论、后续动作和时间节点，方便导师、同学或业务同伴快速读取上下文。</p>
    <p>偏好用事实说话，表达清晰。</p>
  </section>
  <section><h2>教育背景</h2><p>华东大学 本科 2022-2026</p></section>
  <section><h2>技能</h2><p>SQL, Excel, 数据复盘, 用户调研, SOP</p></section>
  <section><h2>荣誉证书</h2><p>CET-6</p></section>
  <p>liming@example.com 138-1234-5678</p>
</main>
</body>
</html>"""


class CheckResumeHtmlContentQualityTests(unittest.TestCase):
    def validate_html(self, html: str):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "resume.html"
            path.write_text(html, encoding="utf-8")
            return validate(path, allow_placeholders=True)

    def test_clean_resume_has_no_content_quality_warnings(self):
        failures, warnings = self.validate_html(VALID_HTML)
        self.assertEqual([], failures)
        joined = "\n".join(warnings)
        self.assertNotIn("weak claim wording", joined)
        self.assertNotIn("Too few bullets include", joined)

    def test_weak_claim_wording_warns(self):
        html = VALID_HTML.replace(
            "策划并落地 4 场用户活动，覆盖 1,200+ 目标用户，沉淀活动复盘模板。",
            "负责活动运营，沟通能力良好，认真踏实。"
        )
        failures, warnings = self.validate_html(html)
        self.assertEqual([], failures)
        self.assertTrue(any("weak claim wording" in warning for warning in warnings))

    def test_low_evidence_bullets_warn(self):
        html = VALID_HTML.replace(
            "面向产品运营岗位，具备用户增长、活动运营、数据复盘和跨团队推进经验。",
            "面向产品运营岗位，具备活动运营、数据复盘和跨团队沟通经验。"
        )
        html = html.replace(
            "策划并落地 4 场用户活动，覆盖 1,200+ 目标用户，沉淀活动复盘模板。",
            "策划并落地用户活动，整理活动复盘模板。"
        )
        html = html.replace(
            "维护 3 个用户反馈渠道，标注 420+ 条问题并输出周报，推动 4 个产品修复项进入排期。",
            "维护用户反馈渠道，标注用户问题并输出周报。"
        )
        html = html.replace(
            "整理 8 周转化漏斗数据，按渠道拆解流失节点，提出 3 条优化建议。",
            "整理漏斗数据，按渠道拆解流失节点，提出优化建议。"
        )
        failures, warnings = self.validate_html(html)
        self.assertEqual([], failures)
        self.assertTrue(any("Too few bullets include" in warning for warning in warnings))

    def test_chinese_impact_without_digits_counts_as_evidence(self):
        html = VALID_HTML.replace(
            "面向产品运营岗位，具备用户增长、活动运营、数据复盘和跨团队推进经验。",
            "面向产品运营岗位，具备活动运营、数据复盘和跨团队沟通经验。"
        )
        html = html.replace(
            "策划并落地 4 场用户活动，覆盖 1,200+ 目标用户，沉淀活动复盘模板。",
            "策划用户活动，提升转化并覆盖核心用户，整理活动复盘模板。"
        )
        html = html.replace(
            "整理 8 周转化漏斗数据，按渠道拆解流失节点，提出 3 条优化建议。",
            "整理漏斗数据，按渠道拆解流失节点，提出优化建议。"
        )
        failures, warnings = self.validate_html(html)
        self.assertEqual([], failures)
        self.assertFalse(any("Too few bullets include" in warning for warning in warnings))

    def test_template_like_visible_title_warns(self):
        html = VALID_HTML.replace("<h1>李明</h1>", "<h1>应届毕业生简历模板</h1>")
        failures, warnings = self.validate_html(html)
        self.assertEqual([], failures)
        self.assertTrue(any("Template-like title text remains" in warning for warning in warnings))

    def test_hidden_css_with_whitespace_warns(self):
        html = VALID_HTML.replace(
            "@media (max-width: 720px) { main { max-width: 100%; } }",
            ".hidden { display: none; visibility: hidden; }\n"
            "    @media (max-width: 720px) { main { max-width: 100%; } }"
        )
        failures, warnings = self.validate_html(html)
        self.assertEqual([], failures)
        self.assertTrue(any("Hidden text detected" in warning for warning in warnings))

    def test_decorative_pseudo_element_hidden_css_does_not_warn(self):
        html = VALID_HTML.replace(
            "@media (max-width: 720px) { main { max-width: 100%; } }",
            ".page::before { display: none; }\n"
            "    .item:last-child::after { visibility: hidden; }\n"
            "    @media (max-width: 720px) { main { max-width: 100%; } }"
        )
        failures, warnings = self.validate_html(html)
        self.assertEqual([], failures)
        self.assertFalse(any("Hidden text detected" in warning for warning in warnings))

    def test_grouped_real_selector_with_pseudo_element_hidden_css_warns(self):
        html = VALID_HTML.replace(
            "@media (max-width: 720px) { main { max-width: 100%; } }",
            ".hidden, .page::before { display: none; }\n"
            "    @media (max-width: 720px) { main { max-width: 100%; } }"
        )
        failures, warnings = self.validate_html(html)
        self.assertEqual([], failures)
        self.assertTrue(any("Hidden text detected" in warning for warning in warnings))

    def test_inline_hidden_style_warns(self):
        html = VALID_HTML.replace(
            "<main>",
            '<main><span style="display: none">隐藏关键词</span>'
        )
        failures, warnings = self.validate_html(html)
        self.assertEqual([], failures)
        self.assertTrue(any("Hidden text detected" in warning for warning in warnings))

    def test_nested_list_capture_keeps_outer_weak_wording(self):
        html = VALID_HTML.replace(
            "策划并落地 4 场用户活动，覆盖 1,200+ 目标用户，沉淀活动复盘模板。",
            "负责活动运营项目<ul><li>交付 2 份活动复盘材料。</li></ul>"
        )
        failures, warnings = self.validate_html(html)
        self.assertEqual([], failures)
        self.assertTrue(any("weak claim wording" in warning for warning in warnings))

    def test_non_jsonld_script_does_not_satisfy_person_schema(self):
        html = VALID_HTML.replace(
            '<script type="application/ld+json">',
            '<script type="application/json">'
        )
        failures, _ = self.validate_html(html)
        self.assertIn("Missing schema.org Person JSON-LD.", failures)

    def test_default_unittest_discovers_suite_from_repo_root(self):
        if os.environ.get("CHECK_RESUME_HTML_DISCOVERY_CHILD"):
            return
        env = os.environ.copy()
        env["CHECK_RESUME_HTML_DISCOVERY_CHILD"] = "1"
        result = subprocess.run(
            [sys.executable, "-m", "unittest"],
            cwd=REPO_ROOT,
            env=env,
            text=True,
            capture_output=True,
            check=False,
        )
        output = result.stdout + result.stderr
        self.assertEqual(0, result.returncode, output)
        self.assertNotIn("Ran 0 tests", output)
        self.assertRegex(output, r"Ran [1-9]\d* tests")


if __name__ == "__main__":
    unittest.main()
