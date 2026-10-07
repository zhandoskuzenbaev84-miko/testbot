"""
Pydantic ma'lumotlar modellari
"""
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class Question(BaseModel):
    id: int
    subject: str
    topic: str
    difficulty: str = Field(..., description="easy, medium, hard")
    question_text: str
    options: Dict[str, str] = Field(..., description="Variantlar: {'A': ..., 'B': ..., 'C': ..., 'D': ...}")
    correct_option: str = Field(..., description="'A', 'B', 'C' yoki 'D'")
    formula_or_expr: Optional[str] = Field(default=None, description="SymPy ifodasi yoki hisoblash kodi")
    explanation_steps: List[str] = Field(default_factory=list, description="Qadamma-qadam tushuntirish bosqichlari")
    verified: bool = Field(default=True, description="Matematik/kod bilan tekshirilganmi")
    source: str = Field(default="DTM_baza")

class CheckAnswerResult(BaseModel):
    is_correct: bool
    correct_option: str
    user_answer: str
    explanation: str
    sympy_verified: bool
    step_by_step: List[str] = Field(default_factory=list)

class ExplainStepResult(BaseModel):
    question_id: int
    current_step: int
    total_steps: int
    step_text: str
    is_last_step: bool

class DiagnosticResult(BaseModel):
    subject: str
    total_questions: int
    correct_count: int
    score: float
    weak_topics: List[str]
    strong_topics: List[str]
    topic_breakdown: Dict[str, Dict[str, Any]]

class DailyPlanItem(BaseModel):
    topic: str
    target_count: int
    solved_count: int = 0

class DailyPlan(BaseModel):
    user_id: int
    date: str
    items: List[DailyPlanItem]
    is_completed: bool = False

class ProgressReport(BaseModel):
    user_id: int
    period: str
    total_solved: int
    correct_solved: int
    accuracy_percentage: float
    predicted_dtm_score: float
    chart_path: Optional[str] = None
    weak_topics: List[str] = Field(default_factory=list)
    strong_topics: List[str] = Field(default_factory=list)
