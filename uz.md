# TZ-04 · DTM repetitor-agent

| | |
|---|---|
| **Mas'ul** | Mirlan |
| **Versiya** | 1.0 · 12.09.2026 |
| **Muddat** | ___ |
| **Umumiy talablar** | `00_umumiy_talablar.md` — majburiy |

## 1. Muammo
Yiliga 1 mln+ abituriyent. Repetitor 500k–2 mln so'm/oy, qishloqda yo'q. Testlar bor, "nega noto'g'ri" tushuntiruvchi yo'q. O'quvchi zaif mavzusini bilmay hammasini qayta o'qiydi.

## 2. Foydalanuvchi
10–11-sinf, abituriyent. Telefon, Telegram, o'zbek. **Voyaga yetmagan bo'lishi mumkin** — faqat o'quv mavzusi.

## 3. Funksional talablar
| ID | Stsenariy | Natija |
|---|---|---|
| F1 | Fan tanlash + diagnostika (30 savol) | Zaif/kuchli mavzular xaritasi |
| F2 | Moslashuvchan mashq | Zaif mavzudan savol; xato → bosqichma-bosqich tushuntirish → o'xshash savol |
| F3 | "Tushunmadim" (rasm) | Socratic: avval yo'naltiruvchi savol, 2-so'rovda to'liq yechim |
| F4 | Kunlik reja | "Bugun 20 savol: 10 kvadrat tenglama, 10 funksiya" + eslatma |
| F5 | Progress | Hafta/oy grafik, DTM formatida taxminiy ball |

## 4. Tool'lar
| Tool | Chiqish |
|---|---|
| `get_question(subject, topic, difficulty)` | savol, variantlar, id |
| `check_answer(question_id, answer)` | to'g'ri/noto'g'ri (sympy/kod bilan), tushuntirish |
| `explain_solution(question_id, step)` | bosqich matni |
| `diagnose(subject)` | mavzu → ball xaritasi |
| `update_progress(user_id, topic, result)` | |
| `daily_plan(user_id)` | reja[] |
| `progress_report(user_id, period)` | grafik (matplotlib rasm), prognoz |
| `solve_from_image(image)` | masala matni → yo'naltirish |

## 5. Ma'lumot manbalari
- DTM ochiq test to'plamlari (o'tgan yillar) — baza
- Darslik mavzular daraxti
- Generatsiya: LLM yaratadi → **ikkinchi LLM chaqiruvi + sympy tekshiradi** → o'tgani bazaga

## 6. Arxitektura
Gemini Flash (tushuntirish, rasm), Groq (tekshirish, zaxira). sympy — matematik tekshiruv. SQLite/Postgres (questions, users, progress). matplotlib.

## 7. Guardrails
- Javob darhol berilmaydi — Socratic; 2-so'rovda to'liq
- Matematik tekshiruv LLM'ga emas — kodga
- Tekshiruvsiz savol bazaga kirmaydi
- Kamsitmaydi, soxta maqtamaydi
- O'quv mavzusidan tashqari → qaytaradi; voyaga yetmaganlarga mos

## 8. Bosqichlar
**MVP:** matematika + fizika, 300 savol, F1/F2, progress.
**To'liq:** 7 fan, F3/F4/F5, generatsiya.

## 9. Eval
- 50 savol → `check_answer` 100%
- 20 tushuntirish → o'qituvchi: to'g'ri, tushunarli, bosqichma-bosqich (≥ 4/5)
- Sun'iy zaif profil → diagnostika zaif mavzuni topadi
- 10 mavzudan tashqari so'rov → 100% qaytaradi

## 10. Qabul mezonlari
10 o'quvchi 2 hafta → diagnostika +15%; "repetitorsiz tushundim" 7/10.
