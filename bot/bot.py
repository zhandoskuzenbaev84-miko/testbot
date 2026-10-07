"""
DTM Repetitor Agent - Telegram Bot (aiogram 3).
F1 - F5 stsenariylari, rasm tahlili va Guardrails to'liq integratsiya qilingan.
"""
import sys
import os
import io
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import FSInputFile, BufferedInputFile

from config import TELEGRAM_BOT_TOKEN
from agent.repetitor_agent import agent
from core.database import db
from bot.keyboards import (
    get_main_reply_keyboard,
    get_subjects_inline_keyboard,
    get_question_inline_keyboard,
    get_diagnostic_options_keyboard
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Foydalanuvchilarning davom etayotgan diagnostika sessiyalari
user_diagnostic_sessions = {}

dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    name = message.from_user.full_name or "Abituriyent"
    username = message.from_user.username or ""
    db.get_or_create_user(user_id, name, username)

    welcome_text = (
        f"Assalomu alaykum, {name}! 🎓\n\n"
        f"Men **DTM Repetitor-Agentiman**. Maqsadim — sizga DTM testlarida maksimal ball to'plashda yordam berish.\n\n"
        f"📌 **Imkoniyatlarim:**\n"
        f"1. 📝 **Diagnostika (30 savol):** Barcha mavzularni tekshirib, zaif va kuchli tomonlaringiz xaritasini tuzib beraman.\n"
        f"2. 🎯 **Moslashuvchan mashq:** Aynan xato qilayotgan zaif mavzularingizdan savollar beraman.\n"
        f"3. 💡 **Socratic yordam:** 'Tushunmadim' desangiz yoki masala rasmini yuborsangiz, tayyor javobni emas, fikrlash yo'nalishini ko'rsataman.\n"
        f"4. 📅 **Kunlik reja:** Kuniga 20 ta maqsadli savol.\n"
        f"5. 📊 **Progress grafik:** Haftalik natijalar va taxminiy DTM bali.\n\n"
        f"Hozir qaysi fandan boshlaymiz?"
    )
    await message.answer(welcome_text, reply_markup=get_main_reply_keyboard(), parse_mode="Markdown")

@dp.message(F.text == "📚 Fan tanlash")
async def process_subject_select(message: types.Message):
    await message.answer("Tayyorlanmoqchi bo'lgan fanni tanlang:", reply_markup=get_subjects_inline_keyboard())

@dp.callback_query(F.data.startswith("set_subject:"))
async def cb_set_subject(callback: types.CallbackQuery):
    subject = callback.data.split(":", 1)[1]
    db.set_user_subject(callback.from_user.id, subject)
    await callback.message.edit_text(f"✅ Tanlangan fan: **{subject}**\nEndi diagnostika testini topshirishingiz yoki moslashuvchan mashqni boshlashingiz mumkin.", parse_mode="Markdown")
    await callback.answer()

@dp.message(F.text == "🎯 Moslashuvchan mashq")
async def process_adaptive_practice(message: types.Message):
    user_id = message.from_user.id
    subject = db.get_user_subject(user_id)
    ad_info = agent.get_adaptive_question(user_id, subject)
    q = ad_info["question"]

    if "error" in q:
        await message.answer(q["error"])
        return

    text = (
        f"🎯 **{subject} | {q['topic']}** ({q['difficulty'].capitalize()})\n\n"
        f"{q['question_text']}\n\n"
        f"A) {q['options']['A']}\n"
        f"B) {q['options']['B']}\n"
        f"C) {q['options']['C']}\n"
        f"D) {q['options']['D']}"
    )
    await message.answer(text, reply_markup=get_question_inline_keyboard(q["id"]))

@dp.callback_query(F.data.startswith("ans:"))
async def cb_answer(callback: types.CallbackQuery):
    _, q_id_str, user_ans = callback.data.split(":")
    q_id = int(q_id_str)
    user_id = callback.from_user.id

    result = agent.check_user_answer(user_id, q_id, user_ans)

    if result["is_correct"]:
        res_text = f"✅ **To'g'ri!** Barakalla!\n\n{result['explanation']}"
    else:
        res_text = f"❌ **Noto'g'ri.** Siz {user_ans} variantini tanladingiz.\n\n{result['explanation']}"

    await callback.message.answer(res_text, parse_mode="Markdown")

    # Agar xato bo'lsa va o'xshash savol mavjud bo'lsa
    if not result["is_correct"] and result.get("has_similar"):
        sim = result["similar_question"]
        sim_text = (
            f"🔁 **Mavzuni mustahkamlash uchun o'xshash savol:**\n\n"
            f"{sim['question_text']}\n\n"
            f"A) {sim['options']['A']}\n"
            f"B) {sim['options']['B']}\n"
            f"C) {sim['options']['C']}\n"
            f"D) {sim['options']['D']}"
        )
        await callback.message.answer(sim_text, reply_markup=get_question_inline_keyboard(sim["id"]))

    await callback.answer()

@dp.callback_query(F.data.startswith("explain:"))
async def cb_explain(callback: types.CallbackQuery):
    q_id = int(callback.data.split(":")[1])
    user_id = callback.from_user.id

    socratic_res = agent.handle_not_understood(user_id, q_id)
    await callback.message.answer(socratic_res["response"], parse_mode="Markdown")
    await callback.answer()

@dp.message(F.text == "📝 Diagnostika (30 savol)")
async def process_start_diagnostic(message: types.Message):
    user_id = message.from_user.id
    subject = db.get_user_subject(user_id)
    diag_data = agent.start_diagnostic(user_id, subject)

    user_diagnostic_sessions[user_id] = {
        "subject": subject,
        "questions": diag_data["questions"],
        "current_idx": 0,
        "answers": {}
    }

    await message.answer(
        f"🏁 **{subject} fanidan 30 savollik diagnostika testi boshlandi!**\n"
        f"Har bir savolga variant tanlang. Test yakunida zaif va kuchli mavzularingiz xaritasi tuziladi.\n\n"
        f"Keling, 1-savoldan boshlaymiz:"
    )
    await send_diagnostic_question(message, user_id)

async def send_diagnostic_question(message_or_callback, user_id: int):
    session = user_diagnostic_sessions.get(user_id)
    if not session:
        return

    idx = session["current_idx"]
    questions = session["questions"]

    if idx >= len(questions):
        # Diagnostika yakunlandi!
        answers = session["answers"]
        subject = session["subject"]
        result = agent.submit_diagnostic_answers(user_id, subject, answers)

        del user_diagnostic_sessions[user_id]

        report_text = (
            f"🎉 **Diagnostika yakunlandi! ({subject})**\n\n"
            f"📊 Natijalar:\n"
            f"• Jami savollar: {result['total_questions']}\n"
            f"• To'g'ri javoblar: {result['correct_count']}\n"
            f"• Aniqlik: {result['accuracy_percentage']}%\n"
            f"• DTM standarti bo'yicha ball: **{result['dtm_score']} / {result['max_dtm_score']} ball**\n\n"
            f"🔴 **Zaif mavzular (mashq qilish tavsiya etiladi):**\n"
        )
        for wt in result["weak_topics"]:
            report_text += f" • {wt}\n"
        if not result["weak_topics"]:
            report_text += " • Ajoyib! Hech qanday zaif mavzu topilmadi.\n"

        report_text += f"\n🟢 **Kuchli mavzular:**\n"
        for st in result["strong_topics"]:
            report_text += f" • {st}\n"

        report_text += "\nEndi '🎯 Moslashuvchan mashq' tugmasi orqali aynan zaif mavzularingizni mustahkamlashingiz mumkin!"

        if isinstance(message_or_callback, types.Message):
            await message_or_callback.answer(report_text, parse_mode="Markdown")
        else:
            await message_or_callback.message.answer(report_text, parse_mode="Markdown")
        return

    q = questions[idx]
    text = (
        f"📝 **Savol {idx+1}/{len(questions)}** [{q['topic']}]\n\n"
        f"{q['question_text']}\n\n"
        f"A) {q['options']['A']}\n"
        f"B) {q['options']['B']}\n"
        f"C) {q['options']['C']}\n"
        f"D) {q['options']['D']}"
    )

    kb = get_diagnostic_options_keyboard(idx, q["id"])
    if isinstance(message_or_callback, types.Message):
        await message_or_callback.answer(text, reply_markup=kb)
    else:
        await message_or_callback.message.answer(text, reply_markup=kb)

@dp.callback_query(F.data.startswith("diag:"))
async def cb_diag_answer(callback: types.CallbackQuery):
    _, idx_str, q_id_str, ans = callback.data.split(":")
    user_id = callback.from_user.id
    session = user_diagnostic_sessions.get(user_id)

    if session and session["current_idx"] == int(idx_str):
        session["answers"][int(q_id_str)] = ans
        session["current_idx"] += 1
        await callback.answer(f"Javob qabul qilindi: {ans}")
        await send_diagnostic_question(callback, user_id)
    else:
        await callback.answer("Bu savolga allaqachon javob berilgan.")

@dp.message(F.text == "📅 Kunlik reja")
async def process_daily_plan(message: types.Message):
    user_id = message.from_user.id
    plan = agent.get_daily_plan(user_id)
    resp = (
        f"📅 **Bugungi shaxsiy reja:**\n\n"
        f"{plan['plan_summary']}\n\n"
        f"💡 {plan['reminder']}"
    )
    await message.answer(resp, parse_mode="Markdown")

@dp.message(F.text == "📊 Mening progressim")
async def process_progress_report(message: types.Message):
    user_id = message.from_user.id
    report = agent.get_progress_report(user_id, "week")

    text = (
        f"📊 **DTM Progress hisoboti (Haftalik):**\n\n"
        f"• Ishlangan savollar: {report['total_solved']} ta\n"
        f"• To'g'ri ishlangan: {report['correct_solved']} ta\n"
        f"• Umumiy aniqlik: {report['accuracy_percentage']}%\n"
        f"• 🎯 **Taxminiy DTM bali: {report['predicted_dtm_score']} / {report['max_dtm_score']} ball**\n"
    )

    chart_path = report.get("chart_path")
    if chart_path and os.path.exists(chart_path):
        photo = FSInputFile(chart_path)
        await message.answer_photo(photo=photo, caption=text, parse_mode="Markdown")
    else:
        await message.answer(text, parse_mode="Markdown")

@dp.message(F.photo)
async def process_photo_question(message: types.Message, bot: Bot):
    """F3: Rasm orqali berilgan savolni Socratic yechish"""
    user_id = message.from_user.id
    photo = message.photo[-1]
    file_info = await bot.get_file(photo.file_id)
    file_bytes_io = await bot.download_file(file_info.file_path)
    img_bytes = file_bytes_io.read()

    loading_msg = await message.answer("🔍 Masala rasmi tahlil qilinmoqda...")
    res = await agent.tools.solve_from_image(img_bytes, user_id=user_id)

    await loading_msg.delete()
    await message.answer(res["response"], parse_mode="Markdown")

@dp.message(F.text)
async def process_text_message(message: types.Message):
    user_id = message.from_user.id
    user_text = message.text

    # Guardrail xavfsizlik tekshiruvi
    processed = agent.process_message(user_id, user_text)
    if processed["status"] == "rejected_off_topic":
        await message.answer(processed["message"])
        return

    # Agar darsga oid matn bo'lsa
    await message.answer(
        "Savolingiz qabul qilindi. Quyidagi tugmalar orqali mashq qilishni yoki savol yechishni tanlang:",
        reply_markup=get_main_reply_keyboard()
    )

async def start_bot():
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == "your_telegram_bot_token_here":
        print("DIQQAT: TELEGRAM_BOT_TOKEN .env faylda ko'rsatilmagan. Botni ishga tushirishdan oldin tokenni kiriting.")
        return
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    logger.info("Telegram bot ishga tushmoqda...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(start_bot())
