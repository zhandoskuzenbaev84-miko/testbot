"""
SymPy va hisoblash orqali matematik/fizik tekshiruv moduli.
Guardrails: 'Matematik tekshiruv LLM'ga emas — kodga'.
"""
import math
import re
from typing import Tuple, Any, Optional
import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor
)

TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

class SympyChecker:
    @staticmethod
    def safe_parse_expr(expr_str: str) -> Optional[sp.Expr]:
        """Matnli ifodani xavfsiz SymPy ob'ektiga aylantirish."""
        try:
            cleaned = expr_str.strip().replace("^", "**")
            # x = 5 kabi tengliklarni ajratish
            if "=" in cleaned:
                left, right = cleaned.split("=", 1)
                return parse_expr(f"({left}) - ({right})", transformations=TRANSFORMATIONS)
            return parse_expr(cleaned, transformations=TRANSFORMATIONS)
        except Exception:
            return None

    @staticmethod
    def are_expressions_equivalent(expr1_str: str, expr2_str: str) -> bool:
        """Ikki matematik ifodaning aynan tengligini tekshirish."""
        try:
            e1 = SympyChecker.safe_parse_expr(expr1_str)
            e2 = SympyChecker.safe_parse_expr(expr2_str)
            if e1 is None or e2 is None:
                # Matnli taqqoslash
                return expr1_str.strip().lower() == expr2_str.strip().lower()
            diff = sp.simplify(e1 - e2)
            return diff == 0 or diff.evalf() == 0
        except Exception:
            return expr1_str.strip().lower() == expr2_str.strip().lower()

    @staticmethod
    def are_numbers_close(val1: float, val2: float, rel_tol: float = 1e-2, abs_tol: float = 1e-2) -> bool:
        """Fizik/sonli qiymatlarni yaqinlikka tekshirish (yaxlitlashlarni inobatga olgan holda)."""
        try:
            return math.isclose(float(val1), float(val2), rel_tol=rel_tol, abs_tol=abs_tol)
        except Exception:
            return False

    @staticmethod
    def verify_solution(formula_or_code: str, expected_answer: str) -> Tuple[bool, str]:
        """
        Savolning to'g'ri javobini formula yoki kod yordamida tekshirish.
        Returns: (is_valid, computed_result_str)
        """
        if not formula_or_code:
            return True, expected_answer

        formula = formula_or_code.strip()

        # Agar formula 'solve:' bilan boshlansa (tenglama yechish)
        if formula.startswith("solve:"):
            eq_text = formula[len("solve:"):].strip()
            try:
                x = sp.symbols('x')
                if "=" in eq_text:
                    left, right = eq_text.split("=")
                    eq = sp.Eq(sp.sympify(left), sp.sympify(right))
                else:
                    eq = sp.sympify(eq_text)
                solutions = sp.solve(eq, x)
                sol_str = ", ".join(str(s) for s in solutions)
                is_match = any(SympyChecker.are_expressions_equivalent(str(s), expected_answer) for s in solutions)
                if not is_match and str(solutions) == expected_answer:
                    is_match = True
                return is_match, sol_str
            except Exception as e:
                return False, f"Xato: {e}"

        # Agar formula 'eval:' bilan boshlansa (arifmetik hisob)
        if formula.startswith("eval:"):
            eval_text = formula[len("eval:"):].strip()
            try:
                val = sp.sympify(eval_text)
                simplified = sp.simplify(val)
                res_str = str(simplified)
                # Raqamli tekshirish
                try:
                    num_res = float(simplified.evalf())
                    num_exp = float(sp.sympify(expected_answer).evalf())
                    return SympyChecker.are_numbers_close(num_res, num_exp), res_str
                except Exception:
                    return SympyChecker.are_expressions_equivalent(res_str, expected_answer), res_str
            except Exception as e:
                return False, f"Xato: {e}"

        # Agar formula 'diff:' bo'lsa (hosila)
        if formula.startswith("diff:"):
            diff_text = formula[len("diff:"):].strip()
            try:
                x = sp.symbols('x')
                derivative = sp.diff(sp.sympify(diff_text), x)
                res_str = str(derivative)
                return SympyChecker.are_expressions_equivalent(res_str, expected_answer), res_str
            except Exception as e:
                return False, f"Xato: {e}"

        # Agar formula 'integrate:' bo'lsa (integral)
        if formula.startswith("integrate:"):
            int_text = formula[len("integrate:"):].strip()
            try:
                x = sp.symbols('x')
                integral = sp.integrate(sp.sympify(int_text), x)
                res_str = str(integral)
                return SympyChecker.are_expressions_equivalent(res_str, expected_answer), res_str
            except Exception as e:
                return False, f"Xato: {e}"

        # Umumiy ifodani tekshirish
        try:
            parsed = SympyChecker.safe_parse_expr(formula)
            if parsed is not None:
                res = sp.simplify(parsed)
                return SympyChecker.are_expressions_equivalent(str(res), expected_answer), str(res)
        except Exception:
            pass

        return True, expected_answer

sympy_checker = SympyChecker()
