"""
Socratic metodikasi boshqaruv moduli.
Qoidalar:
- Javob darhol berilmaydi
- 1-so'rovda: Yo'naltiruvchi savol yoki maslahat
- 2-so'rovda: To'liq qadamma-qadam yechim
"""
from typing import Dict, Any, Optional
from core.database import db
from core.guardrails import guardrails

class SocraticManager:
    @staticmethod
    def handle_not_understood(user_id: int, question_id: int) -> Dict[str, Any]:
        """
        Talaba 'Tushunmadim' deb so'raganda Socratic bosqichni boshqarish.
        """
        q = db.get_question_by_id(question_id)
        if not q:
            return {"error": "Savol topilmadi"}

        # Foydalanuvchining ushbu savol bo'yicha nechanchi so'rovi ekanligini olish va oshirish
        req_count = db.increment_socratic_count(user_id, question_id)

        steps = q.explanation_steps
        if not steps:
            steps = [f"Ushbu savolning to'g'ri javobi: {q.correct_option}) {q.options.get(q.correct_option)}"]

        response_text = guardrails.get_socratic_response(
            question_text=q.question_text,
            explanation_steps=steps,
            request_count=req_count
        )

        return {
            "question_id": question_id,
            "request_count": req_count,
            "is_full_solution": (req_count >= 2),
            "response": response_text
        }

socratic_manager = SocraticManager()
