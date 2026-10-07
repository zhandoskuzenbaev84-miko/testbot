"""
SymPy tekshiruv moduli uchun unit testlar
"""
import unittest
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from core.sympy_checker import sympy_checker

class TestSympyChecker(unittest.TestCase):
    def test_arithmetic_equivalence(self):
        self.assertTrue(sympy_checker.are_expressions_equivalent("2 + 2", "4"))
        self.assertTrue(sympy_checker.are_expressions_equivalent("x + x", "2*x"))
        self.assertTrue(sympy_checker.are_expressions_equivalent("(a+b)^2", "a^2 + 2*a*b + b^2"))

    def test_solve_linear_equation(self):
        is_valid, sol = sympy_checker.verify_solution("solve:2*x + 5 = 15", "5")
        self.assertTrue(is_valid)

    def test_eval_expression(self):
        is_valid, sol = sympy_checker.verify_solution("eval:25 * 4 + 10", "110")
        self.assertTrue(is_valid)

    def test_diff_derivative(self):
        is_valid, sol = sympy_checker.verify_solution("diff:3*x**2 + 5*x", "6*x + 5")
        self.assertTrue(is_valid)

if __name__ == "__main__":
    unittest.main()
