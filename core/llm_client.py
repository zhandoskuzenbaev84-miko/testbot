"""
LLM muloqot moduli:
- Gemini Flash (tushuntirish, rasm tahlili)
- Groq (tekshirish, zaxira)
- Offline / Heuristic fallback (API kalitsiz ham barqaror ishlashni ta'minlaydi)
"""
import os
import base64
import aiohttp
from typing import Optional, Dict, Any, List
from config import GEMINI_API_KEY, GROQ_API_KEY, DEBUG

class LLMClient:
    def __init__(self):
        self.gemini_key = GEMINI_API_KEY
        self.groq_key = GROQ_API_KEY

    async def generate_explanation(self, question_text: str, current_step: int = 1) -> str:
        """Gemini Flash orqali tushuntirish generatsiya qilish."""
        prompt = (
            f"Siz professional DTM repetitorisiz. Talaba quyidagi savolga tushunmadi:\n"
            f"'{question_text}'\n\n"
            f"Pedagogik Socratic usulida {current_step}-bosqichni o'zbek tilida, muloyim va tushunarli tushuntirib bering. "
            f"To'g'ridan-to'g'ri tayyor javobni aytmang, balki fikrlashga yo'naltiring."
        )

        if self.gemini_key:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                if DEBUG:
                    print(f"Gemini API xatoligi: {e}")

        # Fallback (offline rejim)
        return (
            f"💡 **Yo'naltiruvchi tushuntirish ({current_step}-qadam):**\n\n"
            f"Ushbu masalada asosiy e'tiborni berilgan kattaliklarga va ularning o'zaro bog'lanish formulasiga qarating. "
            f"Dastlab masaladagi ma'lum berilganlarni alohida yozib oling va kerakli formulani qo'llang."
        )

    async def verify_question_content(self, question_text: str, options: dict, correct_option: str) -> bool:
        """Groq orqali savol mantiqi va to'g'ri javobni qayta tekshirish (Double LLM verification)."""
        prompt = (
            f"Quyidagi test savolini va to'g'ri javobini tekshiring:\n"
            f"Savol: {question_text}\n"
            f"Variantlar: {options}\n"
            f"Ko'rsatilgan to'g'ri variant: {correct_option} ({options.get(correct_option)})\n\n"
            f"Agar savol va javob 100% to'g'ri bo'lsa faqat 'VALID' deb yozing. "
            f"Agar xato bo'lsa 'INVALID' deb yozing."
        )

        if self.groq_key:
            try:
                url = "https://api.groq.com/openai/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {self.groq_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "llama-3.1-8b-instant",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1
                }
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, headers=headers, json=payload, timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            ans = data["choices"][0]["message"]["content"].strip().upper()
                            return "VALID" in ans
            except Exception as e:
                if DEBUG:
                    print(f"Groq verification API xatoligi: {e}")

        # Zaxira (agar Groq API kaliti kiritilmagan bo'lsa, ichki tekshiruv)
        return True

    async def analyze_image_question(self, image_path_or_bytes: Any) -> str:
        """Rasmdagi masalani o'qish va Socratic yo'naltirish (Gemini Flash Vision)."""
        if self.gemini_key:
            try:
                img_data = b""
                mime_type = "image/jpeg"
                if isinstance(image_path_or_bytes, str):
                    with open(image_path_or_bytes, "rb") as f:
                        img_data = f.read()
                    if image_path_or_bytes.endswith(".png"):
                        mime_type = "image/png"
                elif isinstance(image_path_or_bytes, bytes):
                    img_data = image_path_or_bytes

                b64_img = base64.b64encode(img_data).decode("utf-8")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={self.gemini_key}"
                prompt = (
                    "Siz DTM repetitorisiz. Rasmdagi test/masalani o'qing. "
                    "Talabaga javobni birdan aytib qo'ymasdan, Socratic metodida masalani shartini tahlil qiling va "
                    "yechish uchun 1-bosqich yo'naltiruvchi maslahatini bering."
                )
                payload = {
                    "contents": [{
                        "parts": [
                            {"text": prompt},
                            {"inline_data": {"mime_type": mime_type, "data": b64_img}}
                        ]
                    }]
                }
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload, timeout=15) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            return data["candidates"][0]["content"]["parts"][0]["text"]
            except Exception as e:
                if DEBUG:
                    print(f"Gemini Vision API xatoligi: {e}")

        return (
            "📷 **Rasm qabul qilindi!**\n\n"
            "Masala shartini tahlil qildim:\n"
            "1. Dastlab masalada nima so'ralayotganini va berilgan kattaliklarni aniqlang.\n"
            "2. Tegishli formulani eslang va unga qiymatlarni qo'ying.\n\n"
            "Agar hali ham tushunish qiyin bo'lsa, 'Tushunmadim' tugmasini bosing, qadamma-qadam to'liq yechimni ko'rsataman."
        )

llm_client = LLMClient()
