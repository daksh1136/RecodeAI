from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .analyzer import (
    analyze,
    create_plan,
    create_summary,
    normalize_language,
)
from .models import (
    AnalysisResponse,
    CodeRequest,
    ModernizeRequest,
    ModernizeResponse,
)
from .modernizer import modernize


app = FastAPI(
    title="RecodeAI API",
    description=(
        "Explainable legacy-code analysis and conservative "
        "software modernization engine."
    ),
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://recodeai-site.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SUPPORTED_LANGUAGES = {
    "python",
    "javascript",
    "java",
}


def validate_language(language: str) -> str:
    normalized = normalize_language(language)

    if normalized not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language: {language}",
        )

    return normalized


@app.get("/")
def root():
    return {
        "name": "RecodeAI",
        "version": "0.2.0",
        "message": "Modernize legacy software with explainable analysis.",
    }


@app.get("/api/health")
def health():
    return {
        "status": "healthy",
        "service": "RecodeAI API",
        "version": "0.2.0",
    }


@app.get("/api/languages")
def languages():
    return {
        "languages": sorted(SUPPORTED_LANGUAGES),
    }


@app.post(
    "/api/analyze",
    response_model=AnalysisResponse,
)
def analyze_code(request: CodeRequest):
    language = validate_language(request.language)

    findings, scores = analyze(
        request.code,
        language,
    )

    return AnalysisResponse(
        language=language,
        lines_of_code=len(request.code.splitlines()),
        findings=findings,
        scores=scores,
        modernization_plan=create_plan(findings),
        summary=create_summary(
            findings,
            scores.overall,
        ),
    )


@app.post(
    "/api/modernize",
    response_model=ModernizeResponse,
)
def modernize_code(request: ModernizeRequest):
    language = validate_language(request.language)

    before_findings, before_scores = analyze(
        request.code,
        language,
    )

    if request.apply_safe_fixes:
        modernized_code, changes, diff = modernize(
            request.code,
            language,
        )
    else:
        modernized_code = request.code
        changes = [
            "Safe transformations were disabled for this request."
        ]
        diff = ""

    after_findings, after_scores = analyze(
        modernized_code,
        language,
    )

    return ModernizeResponse(
        language=language,
        original_code=request.code,
        modernized_code=modernized_code,
        changes=changes,
        unified_diff=diff,

        before_scores=before_scores,
        after_scores=after_scores,

        before_findings=len(before_findings),
        after_findings=len(after_findings),

        score_improvement=(
            after_scores.overall - before_scores.overall
        ),

        findings_resolved=max(
            0,
            len(before_findings) - len(after_findings),
        ),
    )
