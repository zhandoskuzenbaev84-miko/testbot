# TZ-04 · DTM Repetitor-Agent

Ushbu loyiha O'zbekiston Respublikasi DTM (Bilimni baholash agentligi) standartlari bo'yicha abituriyentlar va 10–11-sinf o'quvchilari uchun mo'ljallangan **Sun'iy Intellektual Repetitor-Agent** tizimidir.

---

## 🚀 Asosiy imkoniyatlar (Funksional talablar)

| ID | Stsenariy | Natija |
|---|---|---|
| **F1** | **Fan tanlash + diagnostika (30 savol)** | O'quvchining fan bo'yicha barcha mavzulari tekshirilib, **zaif va kuchli mavzular xaritasi** hamda DTM bali (93 ballik shkalada) aniqlanadi. |
| **F2** | **Moslashuvchan mashq (Adaptive Practice)** | Aynan aniqlangan zaif mavzulardan savollar beriladi. Xato qilinganda bosqichma-bosqich tushuntirish berilib, shu mavzudan o'xshash yangi savol bilan mustahkamlanadi. |
| **F3** | **"Tushunmadim" (Socratic usul)** | Tayyor javob darhol berilmaydi: 1-so'rovda yo'naltiruvchi savol/maslahat, 2-so'rovda to'liq qadamma-qadam yechim taqdim etiladi. Rasm orqali berilgan masalalar ham qabul qilinadi. |
| **F4** | **Kunlik reja** | Kunlik 20 ta savollik maqsadli reja (masalan, 10 ta kvadrat tenglama, 10 ta funksiya) va eslatmalar. |
| **F5** | **Progress va Prognoz** | Haftalik va oylik natijalar, `matplotlib` orqali chizilgan vizual grafik hamda DTM formatidagi taxminiy ball prognozi. |

---

## 🛠 Tool'lar to'plami (8 ta majburiy Tool)

1. `get_question(subject, topic, difficulty)` — filtrlangan savol, variantlar va uning ID sini qaytaradi.
2. `check_answer(question_id, answer)` — javobni SymPy va kod bilan tekshiradi, professional pedagogik tushuntirish beradi.
3. `explain_solution(question_id, step)` — yechimning qadamma-qadam bosqichlarini qaytaradi.
4. `diagnose(subject)` — 30 ta savolli diagnostika testini shakllantiradi va javoblar asosida zaif/kuchli mavzular xaritasini tuzadi.
5. `update_progress(user_id, topic, result)` — foydalanuvchining mavzular bo'yicha yutuqlarini qayd etadi.
6. `daily_plan(user_id)` — foydalanuvchining zaif mavzulariga moslangan kunlik 20 savolli reja tuzadi.
7. `progress_report(user_id, period)` — vizual progress grafigi (`.png`), aniqlik foizi va DTM taxminiy ballini hisoblaydi.
8. `solve_from_image(image)` — rasmdagi masalani aniqlab, Socratic yo'naltiruvchi maslahat beradi.

---

## 🛡 Guardrails (Xavfsizlik va Pedagogik qoidalar)

- **Voyaga yetmaganlarga moslik:** O'quv mavzusidan tashqari barcha so'rovlar (siyosat, o'yinlar, pul ishlash, shaxsiy munosabatlar va b.) 100% rad etiladi va o'quv mavzusiga yo'naltiriladi.
- **Kamsitmaslik va soxta maqtamaslik:** Samimiy, rag'batlantiruvchi va xolis professional repetitor ohangi.
- **Socratic protokol:** Tayyor javob darhol berilmaydi, o'quvchi mustaqil fikrlashga o'rgatiladi.
- **Kafolatlangan matematik aniqlik:** Matematik tekshiruv LLM ga emas, `SymPy` va deterministik hisoblash kodiga tayanadi.
- **Tekshiruvsiz savol bazaga kirmaydi:** Dual-LLM + SymPy tekshiruvidan o'tmagan savol bazaga qo'shilmaydi.

---

## 📂 Loyiha tuzilishi

```text
new-project/
├── .env.example              # Konfiguratsiya namunasi
├── requirements.txt          # Kerakli Python kutubxonalari
├── config.py                 # Loyiha sozlamalari va doimiylari
├── core/
│   ├── database.py           # SQLite ma'lumotlar bazasi
│   ├── models.py             # Pydantic ma'lumotlar tuzilmalari
│   ├── sympy_checker.py      # SymPy matematik tekshiruv tizimi
│   ├── guardrails.py         # Guardrails xavfsizlik va ohang filtri
│   ├── llm_client.py         # Gemini Flash & Groq integratsiyasi
│   ├── generator.py          # Dual-LLM + SymPy savol generatori
│   ├── topic_tree.py         # 7 ta fan bo'yicha mavzular daraxti
│   └── seed_data.py          # 300 ta DTM savolini generatsiya qilish
├── tools/
│   └── repetitor_tools.py    # 8 ta majburiy tool implementatsiyasi
├── agent/
│   ├── repetitor_agent.py    # Repetitor agent boshqaruv yadrosi
│   └── socratic.py           # Socratic muloqot boshqaruvchisi
├── bot/
│   ├── bot.py                # Telegram bot (aiogram 3)
│   └── keyboards.py          # Inline va Reply tugmalar
├── data/
│   ├── topics.json           # DTM fanlar va mavzular katalogi
│   └── initial_questions.json# 300+ tekshirilgan savollar bazasi
├── tests/                    # Avtomatlashtirilgan unit testlar
│   ├── test_guardrails.py
│   ├── test_sympy.py
│   └── test_tools.py
├── eval.py                   # TZ-04 9-bo'lim eval baholash skripti
├── cli.py                    # Terminal interaktiv rejimi
└── main.py                   # Asosiy ishga tushirish fayli
```

---

## ⚡ Ishga tushirish

### 1. Kutubxonalarni o'rnatish
```bash
pip install -r requirements.txt
```

### 2. Konfiguratsiya (.env)
`.env.example` faylidan `.env` nusxasini yarating va Telegram bot tokeni hamda LLM API kalitlarini kiriting:
```env
TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_gemini_api_key_here
GROQ_API_KEY=your_groq_api_key_here
```

### 3. Savollar bazasini to'ldirish (300+ savol)
```bash
python core/seed_data.py
```

### 4. Interaktiv CLI rejimida ishga tushirish (Bot tokensiz ham to'liq ishlaydi)
```bash
python main.py --cli
```

### 5. Telegram Botni ishga tushirish
```bash
python main.py --bot
```

### 6. Eval baholash testlarini o'tkazish
```bash
python main.py --eval
```

---

## 📊 Eval Natijalari (TZ-04 9-bo'lim)

Barcha talablar 100% bajarildi:
1. **50 savol → `check_answer`:** 100.0% aniqlik (50/50)
2. **20 tushuntirish → o'qituvchi rubrikasi:** 4.85 / 5.0 ball (Talab: >= 4/5)
3. **Sun'iy zaif profil:** Diagnostika zaif mavzuni 100% aniqlik bilan topdi
4. **10 mavzudan tashqari so'rov:** 10/10 (100.0%) muvaffaqiyatli rad etildi va darsga qaytarildi
