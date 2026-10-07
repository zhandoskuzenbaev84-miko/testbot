"""
Repetitor Tool'lar uchun unit testlar (barcha 8 ta tool)
"""
import unittest
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from tools.repetitor_tools import tools
from core.database import db

class TestRepetitorTools(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.user_id = 9999
        db.get_or_create_user(cls.user_id, "Test Foydalanuvchi")

    def test_tool_1_get_question(self):
        q = tools.get_question(subject="Matematika")
        self.assertIn("id", q)
        self.assertIn("options", q)
        self.assertEqual(len(q["options"]), 4)

    def test_tool_2_check_answer(self):
        q = tools.get_question(subject="Matematika")
        db_q = db.get_question_by_id(q["id"])
        res = tools.check_answer(q["id"], db_q.correct_option)
        self.assertTrue(res["is_correct"])

    def test_tool_3_explain_solution(self):
        q = tools.get_question(subject="Matematika")
        exp = tools.explain_solution(q["id"], step=1)
        self.assertIn("step_text", exp)
        self.assertEqual(exp["current_step"], 1)

    def test_tool_4_diagnose(self):
        diag = tools.diagnose(subject="Matematika")
        self.assertIn("questions", diag)
        self.assertGreaterEqual(len(diag["questions"]), 15)

    def test_tool_5_update_progress(self):
        res = tools.update_progress(self.user_id, "Sonlar va arifmetik amallar", True)
        self.assertEqual(res["user_id"], self.user_id)
        self.assertIn("topic_stats", res)

    def test_tool_6_daily_plan(self):
        plan = tools.daily_plan(self.user_id)
        self.assertIn("plan_summary", plan)
        self.assertIn("items", plan)

    def test_tool_7_progress_report(self):
        rep = tools.progress_report(self.user_id, period="week")
        self.assertIn("predicted_dtm_score", rep)
        self.assertIn("chart_path", rep)

    def test_tool_8_solve_from_image(self):
        import asyncio
        res = asyncio.run(tools.solve_from_image("test_dummy.png", user_id=self.user_id))
        self.assertIn("response", res)

if __name__ == "__main__":
    unittest.main()
