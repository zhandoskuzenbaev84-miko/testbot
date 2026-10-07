"""
DTM Repetitor Agent - Terminal orqali interaktiv ishlash interfeysi (CLI).
Har qanday muhitda bot tokensiz ham barcha funksiyalarni to'liq tekshirish imkonini beradi.
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")

ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agent.repetitor_agent import agent
from core.database import db
from core.topic_tree import topic_tree

def print_header(title: str):
    print("\n" + "=" * 60)
    print(f"   {title.center(54)}")
    print("=" * 60 + "\n")

def run_cli():
    print_header("DTM REPETITOR-AGENT (CLI REJIMI)")
    user_id = 1001
    user = db.get_or_create_user(user_id, full_name="Abituriyent", username="test_user")

    current_subject = db.get_user_subject(user_id)
    print(f"Assalomu alaykum! Tanlangan fan: {current_subject}")

    while True:
        print("\n--- ASOSIY MENYU ---")
        print("1. Fan tanlash (Matematika / Fizika)")
        print("2. F1: 30 savollik diagnostika testini boshlash")
        print("3. F2: Moslashuvchan mashq (Zaif mavzudan savol yechish)")
        print("4. F4: Kunlik reja (Bugungi 20 savol rejasi)")
        print("5. F5: Progress hisoboti va grafik (Taxminiy DTM ball)")
        print("6. Guardrails / Savol berish (Erkin matnli muloqot)")
        print("0. Chiqish")

        choice = input("\nTanlovingizni kiriting [0-6]: ").strip()

        if choice == "0":
            print("Xayr! O'qishlaringizda omad tilaymiz!")
            break

        elif choice == "1":
            print("\nMavjud fanlar:")
            subjects = topic_tree.get_subjects()
            for idx, s in enumerate(subjects, 1):
                print(f"{idx}. {s}")
            s_idx = input("Fan raqamini tanlang: ").strip()
            if s_idx.isdigit() and 1 <= int(s_idx) <= len(subjects):
                selected = subjects[int(s_idx) - 1]
                db.set_user_subject(user_id, selected)
                current_subject = selected
                print(f"Fan muvaffaqiyatli o'zgartirildi: {current_subject}")
            else:
                print("Noto'g'ri tanlov!")

        elif choice == "2":
            print_header(f"DIAGNOSTIKA TESTI: {current_subject} (30 savol)")
            diag = agent.start_diagnostic(user_id, current_subject)
            questions = diag["questions"]
            answers = {}

            print(f"Jami {len(questions)} ta savol beriladi. Har biriga A, B, C yoki D deb javob bering.\n")
            for idx, q in enumerate(questions, 1):
                print(f"{idx}. [{q['topic']}] {q['question_text']}")
                for opt_k, opt_v in q["options"].items():
                    print(f"   {opt_k}) {opt_v}")
                ans = input("Javobingiz [A/B/C/D] (yoki 'skip'): ").strip().upper()
                if ans in ["A", "B", "C", "D"]:
                    answers[q["id"]] = ans
                print("-" * 40)

            print("\nNatijalar hisoblanmoqda...")
            res = agent.submit_diagnostic_answers(user_id, current_subject, answers)
            print_header("DIAGNOSTIKA NATIJALARI")
            print(f"Jami savollar: {res['total_questions']}")
            print(f"To'g'ri javoblar: {res['correct_count']}")
            print(f"Aniqlik darajasi: {res['accuracy_percentage']}%")
            print(f"DTM standarti bo'yicha taxminiy ball: {res['dtm_score']} / {res['max_dtm_score']}")

            print("\n🔴 ZAIF MAVZULAR (qayta ishlash kerak):")
            for wt in res["weak_topics"]:
                print(f" - {wt}")
            if not res["weak_topics"]:
                print(" - Ajoyib! Zaif mavzular aniqlanmadi.")

            print("\n🟢 KUCHLI MAVZULAR:")
            for st in res["strong_topics"]:
                print(f" - {st}")

        elif choice == "3":
            print_header(f"MOSLASHUVCHAN MASHQ: {current_subject}")
            adaptive_info = agent.get_adaptive_question(user_id, current_subject)
            q = adaptive_info["question"]
            if "error" in q:
                print(q["error"])
                continue

            print(f"Mavzu: {q['topic']} | Qiyinlik: {q['difficulty']}")
            print(f"\nSavol: {q['question_text']}")
            for opt_k, opt_v in q["options"].items():
                print(f"  {opt_k}) {opt_v}")

            while True:
                user_ans = input("\nJavobingizni kiriting [A/B/C/D] (yoki 'tushunmadim'): ").strip()
                if user_ans.lower() in ["tushunmadim", "help", "qanday yechiladi"]:
                    socratic_res = agent.handle_not_understood(user_id, q["id"])
                    print("\n" + socratic_res["response"] + "\n")
                    if socratic_res["is_full_solution"]:
                        break
                    continue

                check_res = agent.check_user_answer(user_id, q["id"], user_ans)
                print("\n" + check_res["explanation"])

                if not check_res["is_correct"] and check_res.get("has_similar"):
                    sim = check_res["similar_question"]
                    print("\n🔁 Ushbu mavzuni mustahkamlash uchun o'xshash yangi savol:")
                    print(f"Savol: {sim['question_text']}")
                    for opt_k, opt_v in sim["options"].items():
                        print(f"  {opt_k}) {opt_v}")
                    sim_ans = input("\nJavobingiz [A/B/C/D]: ").strip()
                    sim_check = agent.check_user_answer(user_id, sim["id"], sim_ans)
                    print("\n" + sim_check["explanation"])

                break

        elif choice == "4":
            print_header("KUNLIK REJA")
            plan = agent.get_daily_plan(user_id)
            print(plan["plan_summary"])
            print("\n" + plan["reminder"])

        elif choice == "5":
            print_header("PROGRESS VA DTM BALL PROGNOZI")
            report = agent.get_progress_report(user_id, "week")
            print(f"Jami ishlangan savollar: {report['total_solved']}")
            print(f"To'g'ri ishlangan: {report['correct_solved']}")
            print(f"Umumiy aniqlik: {report['accuracy_percentage']}%")
            print(f"DTM formatida taxminiy ball: {report['predicted_dtm_score']} / {report['max_dtm_score']}")
            print(f"Grafik saqlandi: {report['chart_path']}")

        elif choice == "6":
            print_header("GUARDRAILS VA ERKIN SAVOL BERISH")
            user_msg = input("Savolingizni yoki xabaringizni yozing: ").strip()
            processed = agent.process_message(user_id, user_msg)
            if processed["status"] == "rejected_off_topic":
                print("\n🛑 Guardrail himoyasi:")
                print(processed["message"])
            else:
                print("\nXabar o'quv mavzusiga mos. Qaysi fan bo'yicha masalani yechamiz?")

if __name__ == "__main__":
    run_cli()
