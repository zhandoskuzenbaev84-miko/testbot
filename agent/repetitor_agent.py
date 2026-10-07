"""
DTM Repetitor-Agent asosiy boshqaruvchi klassi.
F1 - F5 stsenariylarini to'liq qamrab oladi.
"""
from typing import Dict, Any, Optional, List
from core.database import db
from core.guardrails import guardrails
from core.topic_tree import topic_tree
from tools.repetitor_tools import tools
from agent.socratic import socratic_manager

class RepetitorAgent:
    def __init__(self):
        self.tools = tools
        self.guardrails = guardrails
        self.socratic = socratic_manager

    def process_message(self, user_id: int, message_text: str) -> Dict[str, Any]:
        """
        Foydalanuvchi matnli xabarini qabul qilish va Guardrails orqali tekshirish.
        """
        is_safe, redirect_msg = self.guardrails.check_input_safety(message_text)
        if not is_safe:
            return {
                "status": "rejected_off_topic",
                "message": redirect_msg
            }
        return {"status": "ok", "message": message_text}

    def start_diagnostic(self, user_id: int, subject: str) -> Dict[str, Any]:
        """
        F1: Fan tanlash va 30 ta savolli diagnostika testini boshlash.
        """
        db.set_user_subject(user_id, subject)
        diagnostic_data = self.tools.diagnose(subject=subject)
        return {
            "status": "diagnostic_started",
            "subject": subject,
            "total_questions": diagnostic_data["total_questions"],
            "questions": diagnostic_data["questions"]
        }

    def submit_diagnostic_answers(self, user_id: int, subject: str, answers: Dict[int, str]) -> Dict[str, Any]:
        """
        F1: Diagnostika natijalarini hisoblash va zaif/kuchli mavzular xaritasini shakllantirish.
        """
        result = self.tools.diagnose(subject=subject, answers=answers)

        # Barcha javoblarni progress bazasiga yozish
        for q_id, ans in answers.items():
            q = db.get_question_by_id(q_id)
            if q:
                is_correct = (ans.strip().upper() == q.correct_option.strip().upper())
                self.tools.update_progress(
                    user_id=user_id,
                    topic=q.topic,
                    result=is_correct,
                    question_id=q_id,
                    answer=ans,
                    subject=subject
                )

        return result

    def get_adaptive_question(self, user_id: int, subject: Optional[str] = None) -> Dict[str, Any]:
        """
        F2: Moslashuvchan mashq:
        - Zaif mavzuni aniqlaydi va birinchi navbatda shu mavzudan savol tanlaydi.
        - Agar zaif mavzular bo'lmasa, hali yechilmagan savollarni taqdim etadi.
        """
        current_subject = subject or db.get_user_subject(user_id)
        topic_stats = db.get_user_topic_stats(user_id, current_subject)

        # Zaif mavzularni tartiblash (aniqligi eng past bo'lganlar)
        weak_topics = [
            t for t, s in topic_stats.items()
            if s["accuracy"] < 0.60
        ]

        target_topic = None
        if weak_topics:
            target_topic = weak_topics[0]
        else:
            all_topics = topic_tree.get_topics(current_subject)
            # Foydalanuvchi hali kam ishlagan mavzuni olish
            untested = [t for t in all_topics if t not in topic_stats]
            target_topic = untested[0] if untested else (all_topics[0] if all_topics else None)

        # Yechilgan savollarni takrorlamaslik uchun exclude_ids
        solved_ids = db.get_user_solved_ids(user_id, current_subject)

        question = self.tools.get_question(
            subject=current_subject,
            topic=target_topic,
            exclude_ids=solved_ids
        )

        return {
            "mode": "adaptive",
            "subject": current_subject,
            "target_topic": target_topic,
            "question": question
        }

    def check_user_answer(self, user_id: int, question_id: int, answer: str) -> Dict[str, Any]:
        """
        F2: Javobni tekshirish:
        - to'g'ri bo'lsa: tasdiqlash va progressni yangilash
        - xato bo'lsa: bosqichma-bosqich tushuntirish va o'xshash savol taklif qilish
        """
        result = self.tools.check_answer(question_id, answer)
        q = db.get_question_by_id(question_id)

        if q:
            self.tools.update_progress(
                user_id=user_id,
                topic=q.topic,
                result=result["is_correct"],
                question_id=question_id,
                answer=answer,
                subject=q.subject
            )

        if not result["is_correct"] and q:
            # Xato qilingan mavzudan o'xshash savol tayyorlash
            similar_q = self.tools.get_question(
                subject=q.subject,
                topic=q.topic,
                exclude_ids=[question_id]
            )
            result["similar_question"] = similar_q
            result["has_similar"] = True if "id" in similar_q else False
        else:
            result["has_similar"] = False

        return result

    def explain_step(self, question_id: int, step: int = 1) -> Dict[str, Any]:
        """
        Bosqichma-bosqich yechimni ko'rsatish.
        """
        return self.tools.explain_solution(question_id, step)

    def handle_not_understood(self, user_id: int, question_id: int) -> Dict[str, Any]:
        """
        F3: 'Tushunmadim' so'rovi (Socratic).
        """
        return self.socratic.handle_not_understood(user_id, question_id)

    def get_daily_plan(self, user_id: int) -> Dict[str, Any]:
        """
        F4: Kunlik reja olish.
        """
        current_subject = db.get_user_subject(user_id)
        return self.tools.daily_plan(user_id, current_subject)

    def get_progress_report(self, user_id: int, period: str = "week") -> Dict[str, Any]:
        """
        F5: Progress hisoboti va DTM ball prognozi.
        """
        current_subject = db.get_user_subject(user_id)
        return self.tools.progress_report(user_id, period, current_subject)

agent = RepetitorAgent()
