from typing import Literal

from pydantic import BaseModel, Field


Severity = Literal["low", "medium", "high", "critical"]


class CodeRequest(BaseModel):
    code: str = Field(min_length=1, max_length=50000)
    language: str = Field(default="python", min_length=1, max_length=30)


class Finding(BaseModel):
    id: str
    category: str
    severity: Severity
    title: str
    description: str
    line: int | None = None
    recommendation: str


class ScoreBreakdown(BaseModel):
    security: int
    maintainability: int
    modernization: int
    overall: int


class AnalysisResponse(BaseModel):
    language: str
    lines_of_code: int
    findings: list[Finding]
    scores: ScoreBreakdown
    modernization_plan: list[str]
    summary: str


class ModernizeRequest(CodeRequest):
    apply_safe_fixes: bool = True


class ModernizeResponse(BaseModel):
    language: str
    original_code: str
    modernized_code: str
    changes: list[str]
    unified_diff: str

    before_scores: ScoreBreakdown
    after_scores: ScoreBreakdown

    before_findings: int
    after_findings: int

    score_improvement: int
    findings_resolved: int
