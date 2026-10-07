"""
Savollarni generatsiya qilish va 2-bosqichli tekshiruv (Dual LLM + SymPy) quvuri.
Talab: 'LLM yaratadi → ikkinchi LLM chaqiruvi + sympy tekshiradi → o'tgani bazaga'
"""
import json
import re
from typing import Optional, Dict, Any, Tuple
from core.llm_client import llm_client
from core.sympy_checker import sympy_checker
from core.guardrails import guardrails
from core.database import db

class QuestionGenerator:
    @staticmethod
    async def generate_and_verify_question(
        subject: str,
        topic: str,
        difficulty: str = "medium"
    ) -> Tuple[bool, Optional[Dict[str, Any]], str]:
        """
        Dual-LLM + SymPy quvuri orqali yangi savol yaratish va tekshirish.
        Returns: (is_success, question_dict, message)
        """
        # 1-bosqich: Savol andozasi / LLM generatsiyasi
        # Agar API kalit bo'lsa LLM orqali yaratiladi, bo'lmasa matematik shablon orqali
        prompt = (
            f"DTM standarti bo'yicha {subject} fanidan '{topic}' mavzusida {difficulty} qiyinlikdagi bitta test savoli tuzing.\n"
            f"Faqat quyidagi JSON formatida javob bering:\n"
            "{\n"
            '  "question_text": "Savol matni",\n'
            '  "options": {"A": "javob 1", "B": "javob 2", "C": "javob 3", "D": "javob 4"},\n'
            '  "correct_option": "A",\n'
            '  "formula_or_expr": "eval: 2+2",\n'
            '  "explanation_steps": ["1-qadam...", "2-qadam..."]\n'
            "}"
        )

        # 1-bosqich: Dastlabki savolni shakllantirish
        raw_q = None
        if llm_client.gemini_key:
            try:
                ans_text = await llm_client.generate_explanation(prompt, current_step=1)
                match = re.search(r"\{.*\}", ans_text, re.DOTALL)
                if match:
                    raw_q = json.loads(match.group(0))
            except Exception:
                pass

        # Agar LLM ulanmagan bo'lsa yoki xato bersa, parametrik generator ishlaydi
        if not raw_q:
            import random
            a = random.randint(5, 25)
            b = random.randint(2, 10)
            res = a * b
            raw_q = {
                "question_text": f"Quyidagi ifodaning qiymatini hisoblang: {a} · {b}",
                "options": {
                    "A": str(res),
                    "B": str(res + b),
                    "C": str(res - a),
                    "D": str(res + 5)
                },
                "correct_option": "A",
                "formula_or_expr": f"eval:{a} * {b}",
                "explanation_steps": [
                    f"1. Ko'paytirish amali: {a} · {b}.",
                    f"2. Natija: {res}."
                ]
            }

        raw_q["subject"] = subject
        raw_q["topic"] = topic
        raw_q["difficulty"] = difficulty
        raw_q["source"] = "LLM_generated_verified"

        # 2-bosqich: Ikkinchi LLM tekshiruvi (Groq)
        is_llm_valid = await llm_client.verify_question_content(
            raw_q["question_text"],
            raw_q["options"],
            raw_q["correct_option"]
        )
        if not is_llm_valid:
            return False, None, "2-LLM (Groq) tekshiruvidan o'tmadi"

        # 3-bosqich: SymPy orqali matematik/kod tekshiruvi
        formula = raw_q.get("formula_or_expr")
        correct_val = raw_q["options"][raw_q["correct_option"]]
        if formula:
            is_sympy_valid, comp_res = sympy_checker.verify_solution(formula, correct_val)
            if not is_sympy_valid:
                return False, None, f"SymPy tekshiruvidan o'tmadi: kutilgan={correct_val}, hisoblangan={comp_res}"

        # 4-bosqich: Guardrails tekshiruvi
        is_safe, msg = guardrails.validate_question_for_db(raw_q)
        if not is_safe:
            return False, None, f"Guardrails qoidasidan o'tmadi: {msg}"

        # Barcha tekshiruvlardan o'tgach, bazaga qo'shish
        q_id = db.add_question(raw_q)
        raw_q["id"] = q_id
        return True, raw_q, "Savol to'liq tasdiqlandi va bazaga kiritildi"

question_generator = QuestionGenerator()
