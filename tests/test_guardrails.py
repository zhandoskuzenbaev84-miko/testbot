"""
Guardrails xavfsizlik va pedagogik filtrlash testlari
"""
import unittest
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.guardrails import guardrails

class TestGuardrails(unittest.TestCase):
    def test_off_topic_detection(self):
        off_topic_samples = [
            "Bugun ob-havo qanday?",
            "Kriptovalyuta kurslari qayerda?",
            "PUBG mobileda yangi sezon qachon?",
            "Prezident saylovida kim yutadi?",
            "Menga qizlar bilan tanishish sirini o'rgat"
        ]
        for query in off_topic_samples:
            is_safe, msg = guardrails.check_input_safety(query)
            self.assertFalse(is_safe, f"Query '{query}' rad etilishi kerak edi")
            self.assertTrue("repetitor" in msg.lower() and "dtm" in msg.lower())

    def test_educational_topic_allowed(self):
        educational_samples = [
            "Kvadrat tenglamani yechish formulasini tushuntirib ber",
            "Fizikadan Nyutonning 2-qonuni nima?",
            "Integral hisoblashda Nyuton-Leybnis formulasi",
            "Om qonunini tushunmadim"
        ]
        for query in educational_samples:
            is_safe, msg = guardrails.check_input_safety(query)
            self.assertTrue(is_safe, f"O'quv so'rovi '{query}' qabul qilinishi kerak edi")

    def test_socratic_step_control(self):
        steps = ["1. Formulani eslang", "2. Qiymatlarni qo'ying: x=5", "3. Natija: 5"]
        # 1-so'rovda to'liq yechim berilmasligi kerak
        res1 = guardrails.get_socratic_response("Masala", steps, request_count=1)
        self.assertIn("Yo'naltiruvchi maslahat", res1)
        self.assertNotIn("To'liq bosqichma-bosqich yechim", res1)

        # 2-so'rovda to'liq yechim berilishi kerak
        res2 = guardrails.get_socratic_response("Masala", steps, request_count=2)
        self.assertIn("To'liq bosqichma-bosqich yechim", res2)

if __name__ == "__main__":
    unittest.main()
