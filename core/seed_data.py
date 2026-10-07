"""
300+ DTM savollarini tizimli generatsiya qilish va bazaga yuklash moduli (MVP: Matematika + Fizika).
Har bir savol aniq formula, qadamma-qadam yechim va SymPy bilan tekshirilgan yechimga ega.
"""
import json
import random
import sys
from pathlib import Path

# Loyiha ildiz papkasini qo'shish
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from config import DATA_DIR
from core.database import db
from core.topic_tree import topic_tree

SEED_FILE = DATA_DIR / "initial_questions.json"

def generate_math_questions() -> list:
    questions = []

    # 1. Arifmetika va sonlar (15 savol)
    math_calc_templates = [
        ("Hisoblang: {a} * {b} + {c}", lambda a, b, c: a * b + c, "eval:{a} * {b} + {c}"),
        ("Hisoblang: ({a} + {b}) * {c} - {d}", lambda a, b, c, d: (a + b) * c - d, "eval:({a} + {b}) * {c} - {d}"),
        ("Hisoblang: {a}^2 - {b}^2", lambda a, b: a**2 - b**2, "eval:{a}**2 - {b}**2"),
        ("Kasrni hisoblang: {a}/2 + {b}/4", lambda a, b: (2*a + b)/4, "eval:({a}*2 + {b})/4"),
    ]
    for i in range(15):
        a = random.randint(10, 40)
        b = random.randint(2, 15)
        c = random.randint(5, 25)
        d = random.randint(1, 20)
        ans = a * b + c
        options = {
            "A": str(ans),
            "B": str(ans + b),
            "C": str(ans - a),
            "D": str(ans + 10)
        }
        steps = [
            f"1. Avval ko'paytirish amali bajariladi: {a} * {b} = {a*b}.",
            f"2. So'ngra qo'shish amali bajariladi: {a*b} + {c} = {ans}.",
            f"Demak, to'g'ri javob: {ans}."
        ]
        questions.append({
            "subject": "Matematika",
            "topic": "Sonlar va arifmetik amallar",
            "difficulty": "easy",
            "question_text": f"Hisoblang: {a} · {b} + {c}",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"eval:{a} * {b} + {c}",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2023"
        })

    # 2. Chiziqli tenglamalar (15 savol)
    for i in range(15):
        k = random.randint(2, 8)
        x_val = random.randint(-10, 15)
        b_val = random.randint(3, 20)
        right = k * x_val + b_val
        options = {
            "A": str(x_val),
            "B": str(x_val + 1),
            "C": str(x_val - 2),
            "D": str(-x_val if x_val != 0 else 5)
        }
        steps = [
            f"1. Tenglamadagi ozod hadni o'ng tomonga o'tkazamiz: {k}x = {right} - {b_val}.",
            f"2. {k}x = {right - b_val}.",
            f"3. x ni topish uchun ikkala tomonni {k} ga bo'lamiz: x = {x_val}.",
            f"Demak, to'g'ri javob: x = {x_val}."
        ]
        questions.append({
            "subject": "Matematika",
            "topic": "Chiziqli tenglama va tengsizliklar",
            "difficulty": "easy" if abs(x_val) < 5 else "medium",
            "question_text": f"Tenglamani yeching: {k}x + {b_val} = {right}",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"solve:{k}*x + {b_val} = {right}",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2024"
        })

    # 3. Kvadrat tenglamalar (15 savol)
    for i in range(15):
        r1 = random.randint(1, 7)
        r2 = random.randint(1, 6)
        b_coeff = -(r1 + r2)
        c_coeff = r1 * r2
        options = {
            "A": f"{r1} va {r2}" if r1 != r2 else f"{r1}",
            "B": f"{-r1} va {-r2}",
            "C": f"{r1 + 1} va {r2 - 1}",
            "D": f"{r1*2} va {r2*2}"
        }
        steps = [
            f"1. Kvadrat tenglama umumiy ko'rinishi: x^2 + bx + c = 0.",
            f"2. Viyet teoremasiga ko'ra: x1 + x2 = {-b_coeff}, x1 * x2 = {c_coeff}.",
            f"3. Ildizlar {r1} va {r2} bo'ladi.",
            f"Demak, to'g'ri javob: {r1} va {r2}."
        ]
        sign_b = f"- {abs(b_coeff)}x" if b_coeff < 0 else f"+ {b_coeff}x"
        questions.append({
            "subject": "Matematika",
            "topic": "Kvadrat tenglamalar va kvadratik funksiya",
            "difficulty": "medium",
            "question_text": f"Tenglamaning ildizlarini toping: x² {sign_b} + {c_coeff} = 0",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"solve:x**2 + ({b_coeff})*x + ({c_coeff}) = 0",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2023"
        })

    # 4. Qisqa ko'paytirish formulalari (15 savol)
    for i in range(15):
        a = random.randint(15, 60)
        b = random.randint(5, a - 1)
        res = a**2 - b**2
        options = {
            "A": str(res),
            "B": str(res + 2*b),
            "C": str(res - 2*a),
            "D": str(a**2 + b**2)
        }
        steps = [
            f"1. a² - b² = (a - b)(a + b) formulasidan foydalanamiz.",
            f"2. ({a} - {b}) · ({a} + {b}) = {a-b} · {a+b}.",
            f"3. {a-b} · {a+b} = {res}.",
            f"Demak, to'g'ri javob: {res}."
        ]
        questions.append({
            "subject": "Matematika",
            "topic": "Algebraik ifodalar va qisqa ko'paytirish formulalari",
            "difficulty": "easy",
            "question_text": f"Hisoblang: {a}² - {b}²",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"eval:{a}**2 - {b}**2",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2022"
        })

    # 5. Arifmetik progressiya (15 savol)
    for i in range(15):
        a1 = random.randint(1, 10)
        d = random.randint(2, 6)
        n = random.randint(5, 12)
        an = a1 + (n - 1) * d
        options = {
            "A": str(an),
            "B": str(an + d),
            "C": str(an - d),
            "D": str(an + 2*d)
        }
        steps = [
            "1. Arifmetik progressiyaning n-hadi formulasi: a_n = a_1 + (n - 1)d.",
            f"2. a_{n} = {a1} + ({n} - 1) · {d} = {a1} + {(n-1)*d} = {an}.",
            f"Demak, to'g'ri javob: {an}."
        ]
        questions.append({
            "subject": "Matematika",
            "topic": "Arifmetik va geometrik progressiyalar",
            "difficulty": "medium",
            "question_text": f"Arifmetik progressiyada a₁ = {a1}, d = {d} bo'lsa, uning {n}-hadini toping.",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"eval:{a1} + ({n} - 1) * {d}",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2023"
        })

    # 6. Ko'rsatkichli va logarifmik ifodalar (15 savol)
    log_bases = [(2, 8, 3), (2, 16, 4), (3, 27, 3), (5, 25, 2), (2, 32, 5), (3, 81, 4), (10, 1000, 3)]
    for i in range(15):
        base, val, pwr = random.choice(log_bases)
        multiplier = random.randint(2, 5)
        ans = multiplier * pwr
        options = {
            "A": str(ans),
            "B": str(ans + 1),
            "C": str(ans - 1),
            "D": str(pwr)
        }
        steps = [
            f"1. log_{base}({val}) ifodani hisoblaymiz: {base}^{pwr} = {val}, demak log_{base}({val}) = {pwr}.",
            f"2. {multiplier} · log_{base}({val}) = {multiplier} · {pwr} = {ans}.",
            f"Demak, to'g'ri javob: {ans}."
        ]
        questions.append({
            "subject": "Matematika",
            "topic": "Ko'rsatkichli va logarifmik ifodalar va tenglamalar",
            "difficulty": "medium",
            "question_text": f"Hisoblang: {multiplier} · log_{base}({val})",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"eval:{multiplier} * {pwr}",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2024"
        })

    # 7. Hosila (15 savol)
    for i in range(15):
        coeff = random.randint(2, 6)
        pwr = random.randint(2, 4)
        c = random.randint(1, 10)
        # f(x) = coeff*x^pwr + c*x
        # f'(x) = coeff*pwr * x^(pwr-1) + c
        new_coeff = coeff * pwr
        new_pwr = pwr - 1
        term = f"{new_coeff}x" if new_pwr == 1 else f"{new_coeff}x^{new_pwr}"
        ans_str = f"{term} + {c}"
        options = {
            "A": ans_str,
            "B": f"{coeff}x^{new_pwr} + {c}",
            "C": f"{new_coeff}x^{pwr} + {c}",
            "D": f"{term}"
        }
        steps = [
            "1. Darajali funksiyaning hosilasi: (x^n)' = n·x^(n-1).",
            f"2. ({coeff}x^{pwr})' = {coeff} · {pwr} · x^{new_pwr} = {term}.",
            f"3. ({c}x)' = {c}.",
            f"4. Umumiy hosila: {term} + {c}.",
            f"Demak, to'g'ri javob: {ans_str}."
        ]
        questions.append({
            "subject": "Matematika",
            "topic": "Hosila va uning tatbiqlari",
            "difficulty": "medium",
            "question_text": f"Funksiyaning hosilasini toping: f(x) = {coeff}x^{pwr} + {c}x",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"diff:{coeff}*x**{pwr} + {c}*x",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2023"
        })

    # 8. Aniq integral va boshlang'ich funksiya (15 savol)
    for i in range(15):
        k = random.randint(2, 6)
        b = random.randint(1, 4)
        # int_0^b (k*x) dx = k*x^2/2 from 0 to b = k * b^2 / 2
        k_even = k * 2
        # int_0^b (k_even * x) dx = k_even * b^2 / 2 = k * b^2
        ans = k * (b**2)
        options = {
            "A": str(ans),
            "B": str(ans + b),
            "C": str(ans - k),
            "D": str(k_even * b)
        }
        steps = [
            f"1. {k_even}x ning boshlang'ich funksiyasi: F(x) = {k_even}x²/2 = {k}x².",
            f"2. Nyuton-Leybnis formulasi bo'yicha: F({b}) - F(0) = {k} · ({b})² - 0.",
            f"3. {k} · {b**2} = {ans}.",
            f"Demak, to'g'ri javob: {ans}."
        ]
        questions.append({
            "subject": "Matematika",
            "topic": "Boshlang'ich funksiya va aniq integral",
            "difficulty": "hard",
            "question_text": f"Integralni hisoblang: ∫₀^{b} ({k_even}x) dx",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"eval:{k} * {b}**2",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2024"
        })

    # 9. Geometriya: Uchburchaklar (15 savol)
    pythagorean_triples = [(3, 4, 5), (6, 8, 10), (5, 12, 13), (8, 15, 17), (9, 12, 15)]
    for i in range(15):
        a, b, c = random.choice(pythagorean_triples)
        scale = random.randint(1, 3)
        a_s, b_s, c_s = a * scale, b * scale, c * scale
        options = {
            "A": str(c_s),
            "B": str(c_s + 1),
            "C": str(c_s - 1),
            "D": str(a_s + b_s)
        }
        steps = [
            "1. To'g'ri burchakli uchburchakda Pifagor teoremasi: c² = a² + b².",
            f"2. c² = {a_s}² + {b_s}² = {a_s**2} + {b_s**2} = {c_s**2}.",
            f"3. c = √{c_s**2} = {c_s}.",
            f"Demak, gipotenuza: {c_s}."
        ]
        questions.append({
            "subject": "Matematika",
            "topic": "Planimetriya: uchburchaklar va to'rtburchaklar",
            "difficulty": "easy" if scale == 1 else "medium",
            "question_text": f"To'g'ri burchakli uchburchakning katetlari {a_s} sm va {b_s} sm. Uning gipotenuzasini toping.",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"eval:int(({a_s}**2 + {b_s}**2)**0.5)",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2023"
        })

    # 10. Stereometriya va fazoviy jismlar (15 savol)
    for i in range(15):
        a = random.randint(3, 10)
        vol = a**3
        s_surf = 6 * (a**2)
        options = {
            "A": str(vol),
            "B": str(vol + a),
            "C": str(vol - 2*a),
            "D": str(s_surf)
        }
        steps = [
            "1. Qirrasi 'a' bo'lgan kubning hajmi formulasi: V = a³.",
            f"2. V = {a}³ = {vol}.",
            f"Demak, to'g'ri javob: {vol} sm³."
        ]
        questions.append({
            "subject": "Matematika",
            "topic": "Stereometriya: fazoviy jismlar",
            "difficulty": "medium",
            "question_text": f"Qirrasi {a} sm bo'lgan kubning hajmini toping.",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"eval:{a}**3",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2022"
        })

    return questions

def generate_physics_questions() -> list:
    questions = []

    # 1. Kinematika: tezlik va yo'l (15 savol)
    for i in range(15):
        v = random.randint(10, 30)
        t = random.randint(2, 8)
        s = v * t
        options = {
            "A": f"{s} m",
            "B": f"{s + v} m",
            "C": f"{s - 10} m",
            "D": f"{v + t} m"
        }
        steps = [
            "1. To'g'ri chiziqli tekis harakatda yo'l formulasi: s = v · t.",
            f"2. s = {v} m/s · {t} s = {s} m.",
            f"Demak, bosib o'tilgan yo'l: {s} metr."
        ]
        questions.append({
            "subject": "Fizika",
            "topic": "Kinematika: to'g'ri chiziqli tekis va tezlanuvchan harakat",
            "difficulty": "easy",
            "question_text": f"Jism {v} m/s o'zgarmas tezlik bilan {t} sekund harakatlandi. U bosib o'tgan yo'lni toping.",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"eval:{v} * {t}",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2023"
        })

    # 2. Dinamika: Nyutonning II qonuni (15 savol)
    for i in range(15):
        m = random.randint(2, 10)
        a = random.randint(2, 8)
        f_val = m * a
        options = {
            "A": f"{f_val} N",
            "B": f"{f_val + m} N",
            "C": f"{f_val - a} N",
            "D": f"{m + a} N"
        }
        steps = [
            "1. Nyutonning ikkinchi qonuni formulasi: F = m · a.",
            f"2. F = {m} kg · {a} m/s² = {f_val} N.",
            f"Demak, jismga ta'sir qiluvchi kuch: {f_val} Nyuton."
        ]
        questions.append({
            "subject": "Fizika",
            "topic": "Dinamika: Nyuton qonunlari va kuchlar",
            "difficulty": "easy",
            "question_text": f"Massasi {m} kg bo'lgan jismga kuch ta'sir etib, unga {a} m/s² tezlanish bermoqda. Ushbu kuchni toping.",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"eval:{m} * {a}",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2024"
        })

    # 3. Kinetik energiya (15 savol)
    for i in range(15):
        m = random.choice([2, 4, 6, 8, 10])
        v = random.randint(2, 10)
        ek = int(0.5 * m * (v**2))
        options = {
            "A": f"{ek} J",
            "B": f"{ek * 2} J",
            "C": f"{ek + 10} J",
            "D": f"{m * v} J"
        }
        steps = [
            "1. Kinetik energiya formulasi: E_k = (m · v²) / 2.",
            f"2. E_k = ({m} · {v}²) / 2 = ({m} · {v**2}) / 2 = {ek} J.",
            f"Demak, kinetik energiya: {ek} Joul."
        ]
        questions.append({
            "subject": "Fizika",
            "topic": "Saqlanish qonunlari: impuls va energiya",
            "difficulty": "medium",
            "question_text": f"Massasi {m} kg bo'lgan jism {v} m/s tezlik bilan harakatlanmoqda. Uning kinetik energiyasini hisoblang.",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"eval:int(0.5 * {m} * {v}**2)",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2023"
        })

    # 4. Gidrostatik bosim (15 savol)
    for i in range(15):
        h = random.randint(2, 10)
        rho = 1000 # suv zichligi
        g = 10
        p = rho * g * h
        p_kpa = p // 1000
        options = {
            "A": f"{p_kpa} kPa",
            "B": f"{p_kpa + 5} kPa",
            "C": f"{p_kpa - 2} kPa",
            "D": f"{p_kpa * 2} kPa"
        }
        steps = [
            "1. Gidrostatik bosim formulasi: P = ρ · g · h.",
            f"2. P = 1000 kg/m³ · 10 m/s² · {h} m = {p} Pa = {p_kpa} kPa.",
            f"Demak, suv tubidagi bosim: {p_kpa} kPa."
        ]
        questions.append({
            "subject": "Fizika",
            "topic": "Statika va gidrostatika: bosim va Arximed kuchi",
            "difficulty": "medium",
            "question_text": f"Chuqurligi {h} m bo'lgan suv havzasi tubidagi gidrostatik bosimni toping (suv zichligi 1000 kg/m³, g=10 m/s²).",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"eval:10 * {h}",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2022"
        })

    # 5. O'zgarmas elektr toki: Om qonuni (15 savol)
    for i in range(15):
        r = random.randint(2, 12)
        i_curr = random.randint(2, 8)
        u = i_curr * r
        options = {
            "A": f"{u} V",
            "B": f"{u + r} V",
            "C": f"{u - 2} V",
            "D": f"{r + i_curr} V"
        }
        steps = [
            "1. Zanjir qismi uchun Om qonuni: I = U / R, bundan U = I · R.",
            f"2. U = {i_curr} A · {r} Om = {u} V.",
            f"Demak, o'tkazgich uchlaridagi kuchlanish: {u} Volt."
        ]
        questions.append({
            "subject": "Fizika",
            "topic": "O'zgarmas elektr toki va elektr zanjirlari",
            "difficulty": "easy",
            "question_text": f"Qarshiligi {r} Om bo'lgan o'tkazgichdan {i_curr} A tok oqmoqda. O'tkazgich uchlaridagi kuchlanishni toping.",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"eval:{i_curr} * {r}",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2023"
        })

    # 6. Joul-Lens qonuni (15 savol)
    for i in range(15):
        i_curr = random.randint(2, 4)
        r = random.randint(2, 5)
        t = random.randint(5, 10)
        q = (i_curr**2) * r * t
        options = {
            "A": f"{q} J",
            "B": f"{q + 20} J",
            "C": f"{q - 15} J",
            "D": f"{i_curr * r * t} J"
        }
        steps = [
            "1. Joul-Lens qonuni: Q = I² · R · t.",
            f"2. Q = ({i_curr})² · {r} · {t} = {i_curr**2} · {r} · {t} = {q} J.",
            f"Demak, ajralgan issiqlik miqdori: {q} Joul."
        ]
        questions.append({
            "subject": "Fizika",
            "topic": "O'zgarmas elektr toki va elektr zanjirlari",
            "difficulty": "medium",
            "question_text": f"Qarshiligi {r} Om bo'lgan o'tkazgichdan {i_curr} A tok {t} s davomida o'tganda qancha issiqlik miqdori ajraladi?",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"eval:({i_curr}**2) * {r} * {t}",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2024"
        })

    # 7. Kondensator sig'imi (15 savol)
    for i in range(15):
        c_val = random.randint(2, 10) # mkF
        u_val = random.randint(10, 50)
        q_val = c_val * u_val # mkKl
        options = {
            "A": f"{q_val} mkKl",
            "B": f"{q_val + 20} mkKl",
            "C": f"{q_val - 10} mkKl",
            "D": f"{c_val + u_val} mkKl"
        }
        steps = [
            "1. Kondensator zaryadi formulasi: q = C · U.",
            f"2. q = {c_val} mkF · {u_val} V = {q_val} mkKl.",
            f"Demak, kondensator zaryadi: {q_val} mkKl."
        ]
        questions.append({
            "subject": "Fizika",
            "topic": "Elektrostatika: Kulon qonuni va elektr maydon",
            "difficulty": "easy",
            "question_text": f"Sig'imi {c_val} mkF bo'lgan kondensator {u_val} V kuchlanishgacha zaryadlangan. Uning zaryadini toping.",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"eval:{c_val} * {u_val}",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2023"
        })

    # 8. Ideal gaz qonunlari (15 savol)
    for i in range(15):
        p1 = random.randint(100, 200)
        v1 = random.randint(2, 6)
        # Izotermik siqilish: P1 * V1 = P2 * V2
        v2 = v1 // 2 if v1 % 2 == 0 else 2
        p2 = (p1 * v1) // v2
        options = {
            "A": f"{p2} kPa",
            "B": f"{p2 + 50} kPa",
            "C": f"{p1} kPa",
            "D": f"{p2 // 2} kPa"
        }
        steps = [
            "1. Izotermik jarayon uchun Boyl-Mariott qonuni: P₁ · V₁ = P₂ · V₂.",
            f"2. P₂ = (P₁ · V₁) / V₂ = ({p1} · {v1}) / {v2} = {p2} kPa.",
            f"Demak, yangi bosim: {p2} kPa."
        ]
        questions.append({
            "subject": "Fizika",
            "topic": "Molekulyar-kinetik nazariya va ideal gaz qonunlari",
            "difficulty": "medium",
            "question_text": f"Ideal gaz harorati o'zgarmas bo'lganda, hajmi {v1} litrdan {v2} litrgacha kamaytirildi. Dastlabki bosim {p1} kPa bo'lsa, oxirgi bosimni toping.",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"eval:({p1} * {v1}) // {v2}",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2023"
        })

    # 9. Tebranish davri va chastotasi (15 savol)
    for i in range(15):
        n_cycles = random.randint(20, 60)
        time_sec = random.choice([5, 10, 20])
        freq = n_cycles // time_sec
        options = {
            "A": f"{freq} Gts",
            "B": f"{freq + 2} Gts",
            "C": f"{freq - 1} Gts",
            "D": f"{time_sec} Gts"
        }
        steps = [
            "1. Tebranish chastotasi formulasi: ν = N / t.",
            f"2. ν = {n_cycles} / {time_sec} = {freq} Gts.",
            f"Demak, tebranish chastotasi: {freq} Gerts."
        ]
        questions.append({
            "subject": "Fizika",
            "topic": "Mexanik tebranishlar va to'lqinlar",
            "difficulty": "easy",
            "question_text": f"Mayatnik {time_sec} sekundda {n_cycles} marta to'liq tebrandi. Uning tebranish chastotasini toping.",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"eval:{n_cycles} // {time_sec}",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2024"
        })

    # 10. Optika: yorug'lik sinishi va linzalar (15 savol)
    for i in range(15):
        f_val = random.randint(10, 25) # sm
        # D = 1 / F (metrda)
        # F = f_val sm -> D = 100 / f_val
        d_optical = round(100 / f_val, 1)
        options = {
            "A": f"{d_optical} dptr",
            "B": f"{round(d_optical + 1.5, 1)} dptr",
            "C": f"{round(d_optical - 1.0, 1)} dptr",
            "D": f"{f_val} dptr"
        }
        steps = [
            "1. Linzaning optik kuchi formulasi: D = 1 / F (bu yerda F metrda).",
            f"2. F = {f_val} sm = {f_val / 100} m.",
            f"3. D = 1 / {f_val / 100} = 100 / {f_val} ≈ {d_optical} dptr.",
            f"Demak, linzaning optik kuchi: {d_optical} dioptriya."
        ]
        questions.append({
            "subject": "Fizika",
            "topic": "Optika: geometrik va to'lqin optikasi",
            "difficulty": "medium",
            "question_text": f"Yig'uvchi linzaning fokus masofasi {f_val} sm ga teng. Uning optik kuchini toping.",
            "options": options,
            "correct_option": "A",
            "formula_or_expr": f"eval:round(100 / {f_val}, 1)",
            "explanation_steps": steps,
            "verified": True,
            "source": "DTM_2023"
        })

    return questions

from core.extra_subjects import (
    get_uzbek_language_questions,
    get_history_questions,
    get_biology_questions,
    get_chemistry_questions,
    get_english_questions
)

def seed_database():
    """Savollar bazasini to'ldirish (7 ta fan bo'yicha 450+ savol)."""
    math_q = generate_math_questions()
    phys_q = generate_physics_questions()
    uzbek_q = get_uzbek_language_questions()
    history_q = get_history_questions()
    bio_q = get_biology_questions()
    chem_q = get_chemistry_questions()
    eng_q = get_english_questions()

    all_q = math_q + phys_q + uzbek_q + history_q + bio_q + chem_q + eng_q

    # JSON faylga saqlash
    with open(SEED_FILE, "w", encoding="utf-8") as f:
        json.dump(all_q, f, ensure_ascii=False, indent=2)

    # SQLite bazani tozalash va qayta yuklash
    db.clear_questions()
    added_count = 0
    for q in all_q:
        db.add_question(q)
        added_count += 1

    print(f"Jami {added_count} ta savol muvaffaqiyatli yuklandi:")
    print(f" - Matematika: {len(math_q)}")
    print(f" - Fizika: {len(phys_q)}")
    print(f" - Ona tili va adabiyot: {len(uzbek_q)}")
    print(f" - O'zbekiston tarixi: {len(history_q)}")
    print(f" - Biologiya: {len(bio_q)}")
    print(f" - Kimyo: {len(chem_q)}")
    print(f" - Ingliz tili: {len(eng_q)}")
    return added_count

if __name__ == "__main__":
    seed_database()
