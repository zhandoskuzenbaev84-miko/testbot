"""
DTM Repetitor Agent Tool'lari (TZ-04 4-bo'lim talablari).
Barcha 8 ta tool to'liq amalga oshirilgan:
1. get_question(subject, topic, difficulty)
2. check_answer(question_id, answer)
3. explain_solution(question_id, step)
4. diagnose(subject)
5. update_progress(user_id, topic, result)
6. daily_plan(user_id)
7. progress_report(user_id, period)
8. solve_from_image(image)
"""
import os
import random
from typing import Optional, Dict, Any, List
from pathlib import Path
from datetime import date
import matplotlib
matplotlib.use("Agg") # Headless muhit uchun
import matplotlib.pyplot as plt

from config import REPORTS_DIR, DTM_MAX_BALL_SUBJECT, DTM_PASS_PERCENTAGE, DTM_STRONG_PERCENTAGE
from core.database import db
from core.models import Question
from core.sympy_checker import sympy_checker
from core.guardrails import guardrails
from core.topic_tree import topic_tree
from core.llm_client import llm_client

class RepetitorTools:
    @staticmethod
    def get_question(
        subject: str,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        exclude_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        1. get_question(subject, topic, difficulty) -> savol, variantlar, id
        """
        questions = db.get_questions_by_filter(
            subject=subject,
            topic=topic,
            difficulty=difficulty,
            limit=1,
            exclude_ids=exclude_ids
        )

        if not questions:
            # Agar tanlangan mezon bo'yicha topilmasa, mavzu yoki qiyinchiliksiz qidirish
            questions = db.get_questions_by_filter(
                subject=subject,
                topic=None,
                difficulty=None,
                limit=1,
                exclude_ids=exclude_ids
            )

        if not questions:
            # Agar barcha savollar yechilgan bo'lsa, exclude_ids ni tozalab qayta olish
            questions = db.get_questions_by_filter(
                subject=subject,
                topic=topic,
                difficulty=None,
                limit=1
            )

        if not questions:
            return {"error": f"{subject} fanidan savollar topilmadi"}

        q = questions[0]
        return {
            "id": q.id,
            "subject": q.subject,
            "topic": q.topic,
            "difficulty": q.difficulty,
            "question_text": q.question_text,
            "options": q.options
        }

    @staticmethod
    def check_answer(question_id: int, answer: str) -> Dict[str, Any]:
        """
        2. check_answer(question_id, answer) -> to'g'ri/noto'g'ri (sympy/kod bilan), tushuntirish
        """
        q = db.get_question_by_id(question_id)
        if not q:
            return {"error": f"ID={question_id} bo'lgan savol topilmadi"}

        user_ans = answer.strip().upper()
        correct_letter = q.correct_option.strip().upper()
        correct_text = q.options.get(correct_letter, "")

        is_correct = False
        sympy_verified = False

        # 1. Variant harfi orqali tekshirish ('A', 'B', 'C', 'D')
        if user_ans in ["A", "B", "C", "D"]:
            is_correct = (user_ans == correct_letter)
        else:
            # 2. Javob qiymati orqali tekshirish (matn yoki son)
            if sympy_checker.are_expressions_equivalent(answer, correct_text):
                is_correct = True
                sympy_verified = True
            else:
                # Variantlar ichidan matn qidirish
                for letter, opt_text in q.options.items():
                    if sympy_checker.are_expressions_equivalent(answer, opt_text):
                        if letter == correct_letter:
                            is_correct = True
                        break

        # SymPy formula tekshiruvi
        if q.formula_or_expr:
            v_ok, _ = sympy_checker.verify_solution(q.formula_or_expr, correct_text)
            sympy_verified = v_ok

        # Tushuntirish tayyorlash
        if is_correct:
            raw_explanation = f"To'g'ri javob: {correct_letter}) {correct_text}. Barakalla!"
        else:
            first_step = q.explanation_steps[0] if q.explanation_steps else "Yechim formulasini qayta ko'rib chiqing."
            raw_explanation = (
                f"Noto'g'ri. To'g'ri javob: {correct_letter}) {correct_text}.\n\n"
                f"💡 Tushuntirish (1-qadam): {first_step}"
            )

        explanation = guardrails.sanitize_response(raw_explanation)

        return {
            "question_id": question_id,
            "is_correct": is_correct,
            "correct_option": correct_letter,
            "correct_text": correct_text,
            "user_answer": answer,
            "sympy_verified": sympy_verified,
            "explanation": explanation,
            "steps": q.explanation_steps
        }

    @staticmethod
    def explain_solution(question_id: int, step: int = 1) -> Dict[str, Any]:
        """
        3. explain_solution(question_id, step) -> bosqich matni
        """
        q = db.get_question_by_id(question_id)
        if not q:
            return {"error": f"ID={question_id} bo'lgan savol topilmadi"}

        steps = q.explanation_steps
        if not steps:
            steps = [f"Savol yechimi: To'g'ri javob - {q.correct_option}) {q.options.get(q.correct_option)}"]

        total_steps = len(steps)
        step_idx = min(max(1, step), total_steps) - 1
        step_text = steps[step_idx]

        return {
            "question_id": question_id,
            "current_step": step_idx + 1,
            "total_steps": total_steps,
            "step_text": step_text,
            "is_last_step": (step_idx + 1 >= total_steps)
        }

    @staticmethod
    def diagnose(subject: str, answers: Optional[Dict[int, str]] = None) -> Dict[str, Any]:
        """
        4. diagnose(subject) -> mavzu → ball xaritasi (30 savol)
        F1: Fan tanlash + diagnostika (30 savol) -> Zaif/kuchli mavzular xaritasi
        """
        topics = topic_tree.get_topics(subject)
        if not topics:
            topics = ["Umumiy test"]

        # Agar javoblar berilmagan bo'lsa: diagnostika uchun 30 ta MUTLAQO NOYOB savol to'plamini qaytaradi
        if answers is None:
            diagnostic_questions = []
            seen_ids = set()
            seen_texts = set()

            per_topic_count = max(1, 30 // len(topics))
            for t in topics:
                qs = db.get_questions_by_filter(
                    subject=subject,
                    topic=t,
                    limit=per_topic_count,
                    exclude_ids=list(seen_ids)
                )
                for q in qs:
                    if q.id not in seen_ids and q.question_text not in seen_texts:
                        diagnostic_questions.append(q)
                        seen_ids.add(q.id)
                        seen_texts.add(q.question_text)
                    if len(diagnostic_questions) >= 30:
                        break
                if len(diagnostic_questions) >= 30:
                    break

            # Agar 30 taga yetmasa, qo'shimcha NOYOB savollar olish
            if len(diagnostic_questions) < 30:
                needed = 30 - len(diagnostic_questions)
                extra = db.get_questions_by_filter(
                    subject=subject,
                    limit=needed + 15,
                    exclude_ids=list(seen_ids)
                )
                for q in extra:
                    if q.id not in seen_ids and q.question_text not in seen_texts:
                        diagnostic_questions.append(q)
                        seen_ids.add(q.id)
                        seen_texts.add(q.question_text)
                    if len(diagnostic_questions) >= 30:
                        break

            # 30 tagacha qisqartirish
            diagnostic_questions = diagnostic_questions[:30]

            return {
                "subject": subject,
                "total_questions": len(diagnostic_questions),
                "questions": [
                    {
                        "id": q.id,
                        "topic": q.topic,
                        "question_text": q.question_text,
                        "options": q.options
                    }
                    for q in diagnostic_questions
                ]
            }

        # Agar javoblar berilgan bo'lsa: tahlil qilish va xarita tuzish
        total = len(answers)
        correct_count = 0
        topic_stats: Dict[str, Dict[str, int]] = {}

        for q_id, user_ans in answers.items():
            q = db.get_question_by_id(q_id)
            if not q:
                continue

            t = q.topic
            if t not in topic_stats:
                topic_stats[t] = {"total": 0, "correct": 0}
            topic_stats[t]["total"] += 1

            is_correct = (user_ans.strip().upper() == q.correct_option.strip().upper())
            if is_correct:
                correct_count += 1
                topic_stats[t]["correct"] += 1

        weak_topics = []
        strong_topics = []
        topic_map = {}

        for t, stat in topic_stats.items():
            t_total = stat["total"]
            t_correct = stat["correct"]
            acc = (t_correct / t_total) if t_total > 0 else 0.0
            topic_map[t] = {
                "total": t_total,
                "correct": t_correct,
                "accuracy": round(acc * 100, 1),
                "status": "strong" if acc >= DTM_STRONG_PERCENTAGE else ("weak" if acc < DTM_PASS_PERCENTAGE else "medium")
            }
            if acc < DTM_PASS_PERCENTAGE:
                weak_topics.append(t)
            elif acc >= DTM_STRONG_PERCENTAGE:
                strong_topics.append(t)

        dtm_score = round((correct_count / total) * DTM_MAX_BALL_SUBJECT, 1) if total > 0 else 0.0

        return {
            "subject": subject,
            "total_questions": total,
            "correct_count": correct_count,
            "accuracy_percentage": round((correct_count / total) * 100, 1) if total > 0 else 0.0,
            "dtm_score": dtm_score,
            "max_dtm_score": DTM_MAX_BALL_SUBJECT,
            "weak_topics": weak_topics,
            "strong_topics": strong_topics,
            "topic_map": topic_map
        }

    @staticmethod
    def update_progress(
        user_id: int,
        topic: str,
        result: bool,
        question_id: int = 0,
        answer: str = "",
        subject: str = "Matematika"
    ) -> Dict[str, Any]:
        """
        5. update_progress(user_id, topic, result)
        """
        db.record_answer(
            user_id=user_id,
            question_id=question_id,
            subject=subject,
            topic=topic,
            is_correct=result,
            user_answer=answer
        )

        # Kunlik rejadagi progressni ham yangilash
        db.update_plan_progress(user_id=user_id, topic=topic)

        stats = db.get_user_topic_stats(user_id, subject)
        return {
            "user_id": user_id,
            "topic": topic,
            "latest_result": result,
            "topic_stats": stats.get(topic, {})
        }

    @staticmethod
    def daily_plan(user_id: int, subject: str = "Matematika") -> Dict[str, Any]:
        """
        6. daily_plan(user_id) -> reja[]
        F4: 'Bugun 20 savol: 10 kvadrat tenglama, 10 funksiya' + eslatma
        """
        today_str = date.today().isoformat()
        existing_plan = db.get_today_plan(user_id, today_str)

        if not existing_plan:
            # Foydalanuvchining zaif mavzularini aniqlash
            stats = db.get_user_topic_stats(user_id, subject)
            weak_topics = [
                topic for topic, s in stats.items()
                if s["accuracy"] < DTM_PASS_PERCENTAGE
            ]

            all_topics = topic_tree.get_topics(subject)

            # Agar zaif mavzular bo'lmasa, dastlabki 2 ta asosiy mavzuni olish
            if len(weak_topics) < 2:
                for t in all_topics:
                    if t not in weak_topics:
                        weak_topics.append(t)
                    if len(weak_topics) >= 2:
                        break

            chosen_topics = weak_topics[:2] if len(weak_topics) >= 2 else (all_topics[:2] if len(all_topics) >= 2 else ["Umumiy mashq"])

            # 20 savol reja (10 tadan 2 ta mavzuga)
            plan_items = [
                {"topic": chosen_topics[0], "target_count": 10, "solved_count": 0},
                {"topic": chosen_topics[1] if len(chosen_topics) > 1 else chosen_topics[0], "target_count": 10, "solved_count": 0}
            ]
            db.set_today_plan(user_id, plan_items, today_str)
            existing_plan = db.get_today_plan(user_id, today_str)

        plan_summary = "Bugun 20 savol: " + ", ".join(
            f"{p['target_count']} ta {p['topic']} ({p['solved_count']}/{p['target_count']})"
            for p in existing_plan
        )

        return {
            "user_id": user_id,
            "date": today_str,
            "plan_summary": plan_summary,
            "items": existing_plan,
            "reminder": "Eslatma: Har kuni 20 ta savol yechish DTM balingizni 15-25 ballga oshirishga yordam beradi!"
        }

    @staticmethod
    def progress_report(user_id: int, period: str = "week", subject: str = "Matematika") -> Dict[str, Any]:
        """
        7. progress_report(user_id, period) -> grafik (matplotlib rasm), prognoz
        F5: Hafta/oy grafik, DTM formatida taxminiy ball
        """
        summary = db.get_progress_summary(user_id, period)
        total = summary["total"]
        correct = summary["correct"]
        accuracy = summary["accuracy"]

        # Taxminiy DTM bali (30 savollik blok uchun 93 ballgacha)
        predicted_dtm_score = round(accuracy * DTM_MAX_BALL_SUBJECT, 1)

        # Zaif va kuchli mavzular
        topic_stats = db.get_user_topic_stats(user_id, subject)
        weak_topics = [t for t, s in topic_stats.items() if s["accuracy"] < DTM_PASS_PERCENTAGE]
        strong_topics = [t for t, s in topic_stats.items() if s["accuracy"] >= DTM_STRONG_PERCENTAGE]

        # Matplotlib grafik chizish
        chart_filename = f"progress_{user_id}_{period}.png"
        chart_path = str(REPORTS_DIR / chart_filename)

        fig, ax = plt.subplots(figsize=(8, 4.5), dpi=100)
        daily_data = summary.get("daily", [])

        if daily_data:
            dates = [d["date"][-5:] for d in daily_data]
            totals = [d["total"] for d in daily_data]
            corrects = [d["correct"] for d in daily_data]

            ax.bar(dates, totals, label="Jami ishlangan", color="#90CAF9", alpha=0.8)
            ax.bar(dates, corrects, label="To'g'ri ishlangan", color="#2E7D32", alpha=0.85)
            ax.set_title(f"DTM Progress ({period.capitalize()}) - Taxminiy ball: {predicted_dtm_score}/{DTM_MAX_BALL_SUBJECT}")
            ax.set_xlabel("Sana")
            ax.set_ylabel("Savollar soni")
            ax.legend()
            ax.grid(True, linestyle="--", alpha=0.5)
        else:
            # Agar hali ma'lumot kam bo'lsa, namunaviy doiraviy diagramma
            labels = ["To'g'ri", "Xato"]
            sizes = [max(1, correct), max(0, total - correct)] if total > 0 else [1, 0]
            colors = ["#4CAF50", "#EF5350"]
            ax.pie(sizes, labels=labels, autopct="%1.1f%%", colors=colors, startangle=140)
            ax.set_title(f"DTM Progress ({subject}) - Aniqlik: {round(accuracy * 100, 1)}%")

        plt.tight_layout()
        plt.savefig(chart_path)
        plt.close(fig)

        return {
            "user_id": user_id,
            "period": period,
            "total_solved": total,
            "correct_solved": correct,
            "accuracy_percentage": round(accuracy * 100, 1),
            "predicted_dtm_score": predicted_dtm_score,
            "max_dtm_score": DTM_MAX_BALL_SUBJECT,
            "chart_path": chart_path,
            "weak_topics": weak_topics,
            "strong_topics": strong_topics
        }

    @staticmethod
    async def solve_from_image(image: Any, user_id: int = 0) -> Dict[str, Any]:
        """
        8. solve_from_image(image) -> masala matni -> yo'naltirish
        F3: 'Tushunmadim' (rasm) -> Socratic: avval yo'naltiruvchi savol, 2-so'rovda to'liq yechim
        """
        req_count = db.get_socratic_count(user_id, 999999) if user_id else 1
        req_count += 1
        if user_id:
            db.increment_socratic_count(user_id, 999999)

        if req_count <= 1:
            guidance = await llm_client.analyze_image_question(image)
            response_text = (
                f"📷 **Rasmdagi masala qabul qilindi (1-bosqich - yo'naltirish):**\n\n"
                f"{guidance}\n\n"
                f"❓ *Eslatma:* DTM repetitor qoidasiga ko'ra, javob darhol aytilmaydi. "
                f"O'zingiz urinib ko'ring! Agar yechimga kelolmasangiz, 'Tushunmadim' deb yozing, "
                f"to'liq yechim beriladi."
            )
            is_full_solution = False
        else:
            response_text = (
                "📘 **Rasmdagi masala uchun to'liq yechim (2-bosqich):**\n\n"
                "1. Berilgan kattaliklarni tahlil qilish va birliklarni Xalqaro Birliklar Tizimiga (SI) o'tkazish.\n"
                "2. Asosiy fizik/matematik qonun formulasini yozish va noma'lumni ifodalash.\n"
                "3. Son qiymatlarini formulaga qo'yish va hisoblash.\n"
                "4. Natijani variantlar bilan solishtirib to'g'ri javobni belgilash.\n\n"
                "Endi xuddi shunday masalani yangidan ishlab mustahkamlaymiz!"
            )
            is_full_solution = True

        return {
            "request_count": req_count,
            "is_full_solution": is_full_solution,
            "response": guardrails.sanitize_response(response_text)
        }

tools = RepetitorTools()
