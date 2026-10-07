"""
Guardrails xavfsizlik va pedagogik qoidalar moduli.
Talablar:
- Voyaga yetmaganlarga moslik
- O'quv mavzusidan tashqari so'rovlarni 100% rad etish va o'qishga qaytarish
- Kamsitmaslik va soxta maqtamaslik
- Socratic metodikasi (1-so'rovda yo'naltiruvchi savol/maslahat, 2-so'rovda to'liq yechim)
- Matematik tekshiruvsiz savolni bazaga kiritmaslik
"""
import re
from typing import Tuple, Optional
from core.sympy_checker import sympy_checker

# O'quv mavzusidan tashqari kalit so'zlar va mavzular
OFF_TOPIC_PATTERNS = [
    r"\b(siyosat|prezident|saylov|urush|qurol|hujum|davlat to'ntarishi)",
    r"\b(sevgi|oshiq|qizlar|yigitlar|tanishuv|sevgilim|sevishganlar)",
    r"\b(kripto|bitcoin|valyuta|pul ishlash|kazino|stavka|1xbet|qimor)",
    r"\b(kino|film|serial|tiktok|instagram|trend|pubg|dota|free fire)",
    r"\b(ob-havo|bugun havo|g'iybat|hazil|latifa|qo'shiq|musiqa)",
    r"\b(spirtli|aroq|pivo|sigaret|narkotik|veyp)"
]

# Zararli yoki haqoratli so'zlar
HARMFUL_PATTERNS = [
    r"\b(ahmoq|tentak|jinni|so'kish|iflos|haromi|onangni|it emgan)\b",
    r"\b(o'zini o'ldirish|suitsid|zo'ravonlik|o'ldirish)\b"
]

# Soxta maqtov yoki kamsitish iboralari
BIASED_PRAISE_PATTERNS = [
    r"sen dunyodagi eng dahosan",
    r"sen tengsiz daho ekansan",
    r"senga hech kim teng kelolmaydi"
]

CONDESCENDING_PATTERNS = [
    r"buni ham bilmaysanmi",
    r"juda sodda narsani bilmading",
    r"nahotki shuni bilmasang",
    r"kallang ishlamayaptimi"
]

OFF_TOPIC_REDIRECT_MESSAGE = (
    "Men faqat DTM testlari va o'quv fanlari (Matematika, Fizika, Tarix, Ona tili va b.) "
    "bo'yicha yordam beruvchi repetitor-agentman.\n\n"
    "Keling, diqqatimizni darsga va maqsadimiz bo'lgan talaba bo'lishga qaratamiz! "
    "Qaysi mavzu yoki masalani yechishni xohlaysiz?"
)

class Guardrails:
    @staticmethod
    def check_input_safety(user_text: str) -> Tuple[bool, Optional[str]]:
        """
        Foydalanuvchi xabarini tekshirish.
        Returns: (is_safe, redirect_or_error_message)
        """
        text = user_text.lower().strip()

        # Zararli kontentni tekshirish
        for pattern in HARMFUL_PATTERNS:
            if re.search(pattern, text):
                return False, (
                    "Kechirasiz, odob-axloq qoidalariga zid yoki noo'rin so'rovlarga javob berolmayman. "
                    "Iltimos, darsga oid savol yuboring."
                )

        # O'quv mavzusidan tashqari so'rovlar
        for pattern in OFF_TOPIC_PATTERNS:
            if re.search(pattern, text):
                return False, OFF_TOPIC_REDIRECT_MESSAGE

        return True, None

    @staticmethod
    def sanitize_response(response_text: str) -> str:
        """
        Agent javobidagi kamsitish yoki soxta maqtovlarni tozalash,
        samimiy va pedagogik professional ohangni ta'minlash.
        """
        cleaned = response_text
        for pattern in BIASED_PRAISE_PATTERNS:
            cleaned = re.sub(pattern, "Barakalla, to'g'ri yechdingiz", cleaned, flags=re.IGNORECASE)

        for pattern in CONDESCENDING_PATTERNS:
            cleaned = re.sub(pattern, "Bu masalani bosqichma-bosqich ko'rib chiqamiz", cleaned, flags=re.IGNORECASE)

        return cleaned

    @staticmethod
    def get_socratic_response(question_text: str, explanation_steps: list, request_count: int) -> str:
        """
        Socratic Guardrail:
        - 1-so'rovda ('Tushunmadim'): to'g'ridan-to'g'ri javob berilmaydi, yo'naltiruvchi savol/formula eslatiladi.
        - 2-so'rovda: To'liq bosqichma-bosqich yechim taqdim etiladi.
        """
        if request_count <= 1:
            hint = explanation_steps[0] if explanation_steps else "Masalani shartini tahlil qilib ko'ring."
            return (
                f"💡 **Yo'naltiruvchi maslahat (1-qadam):**\n\n"
                f"{hint}\n\n"
                f"❓ *O'ylab ko'ring:* Ushbu masalani yechish uchun qaysi formulani qo'llash kerak deb o'ylaysiz? "
                f"Javob berishga urinib ko'ring yoki agar hali ham tushunmagan bo'lsangiz, yana 'Tushunmadim' deb yozing, "
                f"to'liq yechimni ko'rsataman."
            )
        else:
            full_steps = "\n\n".join(
                f"**{i+1}-qadam:** {step}" for i, step in enumerate(explanation_steps)
            ) if explanation_steps else "Yechim bosqichlari mavjud emas."
            return (
                f"📘 **To'liq bosqichma-bosqich yechim:**\n\n"
                f"{full_steps}\n\n"
                f"Endi ushbu usulni tushungan bo'lsangiz, shunga o'xshash yangi savol yechib ko'ramizmi?"
            )

    @staticmethod
    def validate_question_for_db(q_data: dict) -> Tuple[bool, str]:
        """
        Tekshiruvsiz savol bazaga kirmaydi:
        - Shart va variantlar mavjudligi
        - To'g'ri javob ko'rsatilganligi
        - SymPy orqali formula tekshiruvi (agar formula berilgan bo'lsa)
        """
        if not q_data.get("question_text"):
            return False, "Savol matni bo'sh bo'lishi mumkin emas"

        options = q_data.get("options", {})
        if not isinstance(options, dict) or set(options.keys()) != {"A", "B", "C", "D"}:
            return False, "Variantlar aniq A, B, C, D bo'lishi shart"

        correct = q_data.get("correct_option")
        if correct not in {"A", "B", "C", "D"}:
            return False, "To'g'ri variant A, B, C yoki D bo'lishi kerak"

        formula = q_data.get("formula_or_expr")
        correct_val = options[correct]

        if formula:
            is_valid, comp_res = sympy_checker.verify_solution(formula, correct_val)
            if not is_valid:
                return False, f"SymPy tekshiruvi xato natija berdi: hisoblangan={comp_res}, kutilgan={correct_val}"

        return True, "Savol to'liq tasdiqlandi"

guardrails = Guardrails()
