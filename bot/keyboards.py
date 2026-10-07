"""
Telegram bot inline va reply tugmalari (Keyboards).
"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from config import SUBJECTS

def get_main_reply_keyboard() -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi"""
    kb = [
        [KeyboardButton(text="🎯 Moslashuvchan mashq"), KeyboardButton(text="📝 Diagnostika (30 savol)")],
        [KeyboardButton(text="📅 Kunlik reja"), KeyboardButton(text="📊 Mening progressim")],
        [KeyboardButton(text="📚 Fan tanlash"), KeyboardButton(text="ℹ️ Yordam")]
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)

def get_subjects_inline_keyboard() -> InlineKeyboardMarkup:
    """Fanlar ro'yxati inline tugmalari"""
    buttons = []
    for s in SUBJECTS:
        buttons.append([InlineKeyboardButton(text=f"📖 {s}", callback_data=f"set_subject:{s}")])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_question_inline_keyboard(question_id: int) -> InlineKeyboardMarkup:
    """Savol variantlari va Socratic 'Tushunmadim' tugmasi"""
    row1 = [
        InlineKeyboardButton(text="A", callback_data=f"ans:{question_id}:A"),
        InlineKeyboardButton(text="B", callback_data=f"ans:{question_id}:B"),
        InlineKeyboardButton(text="C", callback_data=f"ans:{question_id}:C"),
        InlineKeyboardButton(text="D", callback_data=f"ans:{question_id}:D"),
    ]
    row2 = [
        InlineKeyboardButton(text="💡 Tushunmadim (Yordam)", callback_data=f"explain:{question_id}")
    ]
    return InlineKeyboardMarkup(inline_keyboard=[row1, row2])

def get_diagnostic_options_keyboard(question_index: int, question_id: int) -> InlineKeyboardMarkup:
    """Diagnostika testi variantlari"""
    buttons = [
        [
            InlineKeyboardButton(text="A", callback_data=f"diag:{question_index}:{question_id}:A"),
            InlineKeyboardButton(text="B", callback_data=f"diag:{question_index}:{question_id}:B"),
            InlineKeyboardButton(text="C", callback_data=f"diag:{question_index}:{question_id}:C"),
            InlineKeyboardButton(text="D", callback_data=f"diag:{question_index}:{question_id}:D"),
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)
