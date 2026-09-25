import re
from collections import Counter

from .models import Finding, ScoreBreakdown


WEIGHTS = {
    "low": 4,
    "medium": 10,
    "high": 18,
    "critical": 28,
}


LANGUAGE_ALIASES = {
    "py": "python",
    "python3": "python",
    "js": "javascript",
    "node": "javascript",
    "nodejs": "javascript",
}


RULES = {
    "python": [
        (
            r"\beval\s*\(",
            "security",
            "critical",
            "Dynamic eval() usage",
            "eval() executes dynamically supplied expressions and can enable arbitrary code execution.",
            "Replace eval() with explicit parsing or a safe structured-data parser.",
        ),
        (
            r"\bexec\s*\(",
            "security",
            "critical",
            "Dynamic exec() usage",
            "exec() dynamically executes Python code and substantially increases attack surface.",
            "Replace dynamic execution with explicit functions or controlled dispatch.",
        ),
        (
            r"\bos\.system\s*\(",
            "security",
            "high",
            "Shell command execution",
            "os.system() invokes a system shell and may expose the application to command injection.",
            "Use subprocess.run() with an explicit argument list and shell=False.",
        ),
        (
            r"subprocess\..*shell\s*=\s*True",
            "security",
            "high",
            "Subprocess shell mode enabled",
            "Executing commands through a shell increases command-injection risk.",
            "Use explicit argument arrays with shell=False.",
        ),
        (
            r"except\s*:",
            "maintainability",
            "medium",
            "Bare except block",
            "A bare except can hide unexpected programming and system errors.",
            "Catch specific exception types and handle them explicitly.",
        ),
        (
            r"\bprint\s*\(",
            "observability",
            "low",
            "Console print used for application output",
            "Scattered print statements provide limited control over production diagnostics.",
            "Use structured logging with appropriate severity levels.",
        ),
        (
            r"hashlib\.md5\s*\(|\bmd5\s*\(",
            "security",
            "high",
            "Legacy MD5 hashing",
            "MD5 has known cryptographic weaknesses.",
            "Use an algorithm appropriate to the security requirement, such as SHA-256 or a password-hashing function.",
        ),
        (
            r"hashlib\.sha1\s*\(|\bsha1\s*\(",
            "security",
            "high",
            "Legacy SHA-1 hashing",
            "SHA-1 is unsuitable for collision-resistant security applications.",
            "Use a modern hashing algorithm appropriate to the use case.",
        ),
        (
            r"pickle\.loads?\s*\(",
            "security",
            "high",
            "Potentially unsafe pickle deserialization",
            "Unpickling untrusted data can execute attacker-controlled code.",
            "Use a safe serialization format for untrusted input.",
        ),
    ],
    "javascript": [
        (
            r"\beval\s*\(",
            "security",
            "critical",
            "JavaScript eval() usage",
            "eval() executes arbitrary JavaScript and creates substantial security risk.",
            "Replace dynamic evaluation with explicit parsing or function dispatch.",
        ),
        (
            r"\bvar\s+",
            "legacy",
            "low",
            "Legacy var declaration",
            "var uses function scope and can produce unexpected behavior in modern JavaScript.",
            "Prefer const by default and let when reassignment is necessary.",
        ),
        (
            r"(?<![=!])==(?!=)",
            "quality",
            "medium",
            "Loose equality comparison",
            "Loose equality performs implicit type coercion.",
            "Prefer strict equality (===) where behavior permits.",
        ),
        (
            r"(?<![=!])!=(?!=)",
            "quality",
            "medium",
            "Loose inequality comparison",
            "Loose inequality performs implicit type coercion.",
            "Prefer strict inequality (!==) where behavior permits.",
        ),
        (
            r"\bdocument\.write\s*\(",
            "legacy",
            "medium",
            "document.write() usage",
            "document.write() is an outdated DOM-writing technique that can produce unsafe or disruptive behavior.",
            "Use explicit DOM APIs or a modern rendering framework.",
        ),
        (
            r"\binnerHTML\s*=",
            "security",
            "high",
            "Direct innerHTML assignment",
            "Writing untrusted content through innerHTML can introduce cross-site scripting vulnerabilities.",
            "Prefer textContent or sanitize trusted HTML before rendering.",
        ),
    ],
    "java": [
        (
            r"System\.out\.print",
            "observability",
            "low",
            "Direct console output",
            "Direct console output is difficult to manage in production environments.",
            "Use an application logging framework.",
        ),
        (
            r"\bVector\s*<",
            "legacy",
            "medium",
            "Legacy Vector collection",
            "Vector is a legacy synchronized collection and is rarely the preferred modern implementation.",
            "Use ArrayList or an appropriate concurrent collection.",
        ),
        (
            r"\bHashtable\s*<",
            "legacy",
            "medium",
            "Legacy Hashtable collection",
            "Hashtable is a legacy collection with coarse synchronization.",
            "Use HashMap or ConcurrentHashMap depending on concurrency requirements.",
        ),
        (
            r"Thread\.stop\s*\(",
            "security",
            "high",
            "Deprecated Thread.stop()",
            "Thread.stop() is unsafe because asynchronous termination can leave shared state inconsistent.",
            "Implement cooperative cancellation using interruption or application state.",
        ),
        (
            r"\bDate\s*\(\s*\)",
            "legacy",
            "low",
            "Legacy date API usage",
            "Older java.util.Date patterns are harder to reason about than the modern java.time API.",
            "Prefer java.time classes such as Instant, LocalDate or ZonedDateTime.",
        ),
    ],
}


SECRET_PATTERN = re.compile(
    r"""(?ix)
    \b(
        password|
        passwd|
        api[_-]?key|
        secret|
        access[_-]?token|
        auth[_-]?token
    )\b
    \s*[:=]\s*
    ["'][^"']{6,}["']
    """
)


SQL_PATTERN = re.compile(
    r"""(?ix)
    (select|insert|update|delete)
    .*
    (
        \+\s*[a-zA-Z_]|
        \{[a-zA-Z_][^}]*\}|
        %s
    )
    """
)


def normalize_language(language: str) -> str:
    normalized = language.lower().strip()
    return LANGUAGE_ALIASES.get(normalized, normalized)


def add_finding(
    findings: list[Finding],
    category: str,
    severity: str,
    title: str,
    description: str,
    recommendation: str,
    line: int | None,
) -> None:
    findings.append(
        Finding(
            id=f"F-{len(findings) + 1:03}",
            category=category,
            severity=severity,
            title=title,
            description=description,
            line=line,
            recommendation=recommendation,
        )
    )


def detect_rule_findings(
    code: str,
    language: str,
    findings: list[Finding],
) -> None:
    rules = RULES.get(language, [])

    for line_number, line in enumerate(code.splitlines(), start=1):
        for (
            pattern,
            category,
            severity,
            title,
            description,
            recommendation,
        ) in rules:
            if re.search(pattern, line, re.IGNORECASE):
                add_finding(
                    findings,
                    category,
                    severity,
                    title,
                    description,
                    recommendation,
                    line_number,
                )


def detect_cross_language_findings(
    code: str,
    findings: list[Finding],
) -> None:
    lines = code.splitlines()

    for line_number, line in enumerate(lines, start=1):
        stripped = line.strip()

        if SECRET_PATTERN.search(line):
            add_finding(
                findings,
                "security",
                "critical",
                "Possible hardcoded secret",
                "A credential-like value appears to be embedded directly in source code.",
                "Move secrets to environment variables or a dedicated secrets-management system and rotate exposed credentials.",
                line_number,
            )

        if re.search(r"""["']http://[^"']+["']""", line, re.IGNORECASE):
            add_finding(
                findings,
                "security",
                "medium",
                "Insecure HTTP endpoint",
                "The source contains a plaintext HTTP endpoint.",
                "Use HTTPS where supported and validate transport-security requirements.",
                line_number,
            )

        if SQL_PATTERN.search(line):
            add_finding(
                findings,
                "security",
                "high",
                "Potential dynamic SQL construction",
                "SQL appears to be assembled using dynamic application values.",
                "Use parameterized queries or a safe database abstraction instead of string-built SQL.",
                line_number,
            )

        if re.search(r"\b(TODO|FIXME|HACK)\b", stripped, re.IGNORECASE):
            add_finding(
                findings,
                "maintainability",
                "low",
                "Unresolved technical-debt marker",
                "The source contains an explicit TODO, FIXME or HACK marker.",
                "Convert the marker into tracked work or resolve it during modernization.",
                line_number,
            )

        if len(line) > 120:
            add_finding(
                findings,
                "maintainability",
                "low",
                "Long source line",
                "This line exceeds 120 characters and may reduce readability.",
                "Break the expression into smaller and clearer statements.",
                line_number,
            )

    if len(lines) > 300:
        add_finding(
            findings,
            "maintainability",
            "medium",
            "Large source file",
            "The file contains more than 300 lines and may combine multiple responsibilities.",
            "Consider splitting the file into cohesive modules or classes.",
            None,
        )


def detect_duplicate_findings(
    findings: list[Finding],
) -> list[Finding]:
    seen = set()
    unique = []

    for finding in findings:
        key = (
            finding.title,
            finding.line,
            finding.category,
        )

        if key not in seen:
            seen.add(key)
            unique.append(finding)

    for index, finding in enumerate(unique, start=1):
        finding.id = f"F-{index:03}"

    return unique


def calculate_scores(findings: list[Finding]) -> ScoreBreakdown:
    security_penalty = sum(
        WEIGHTS[f.severity]
        for f in findings
        if f.category == "security"
    )

    maintainability_penalty = sum(
        WEIGHTS[f.severity]
        for f in findings
        if f.category in {
            "maintainability",
            "quality",
            "observability",
        }
    )

    modernization_penalty = sum(
        WEIGHTS[f.severity]
        for f in findings
        if f.category in {
            "legacy",
            "quality",
            "maintainability",
            "observability",
        }
    )

    security = max(0, 100 - security_penalty)
    maintainability = max(0, 100 - maintainability_penalty)
    modernization = max(0, 100 - modernization_penalty)

    overall = round(
        security * 0.40
        + maintainability * 0.30
        + modernization * 0.30
    )

    return ScoreBreakdown(
        security=security,
        maintainability=maintainability,
        modernization=modernization,
        overall=overall,
    )


def analyze(
    code: str,
    language: str,
) -> tuple[list[Finding], ScoreBreakdown]:
    language = normalize_language(language)

    findings: list[Finding] = []

    detect_rule_findings(
        code,
        language,
        findings,
    )

    detect_cross_language_findings(
        code,
        findings,
    )

    findings = detect_duplicate_findings(findings)

    severity_order = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    findings.sort(
        key=lambda finding: (
            severity_order[finding.severity],
            finding.line or 999999,
        )
    )

    for index, finding in enumerate(findings, start=1):
        finding.id = f"F-{index:03}"

    return findings, calculate_scores(findings)


def create_plan(findings: list[Finding]) -> list[str]:
    if not findings:
        return [
            "No high-confidence issues were detected by the current deterministic rule set.",
            "Establish regression tests before performing architectural modernization.",
            "Review dependencies, runtime versions and deployment configuration for upgrade opportunities.",
        ]

    plan: list[str] = []

    categories = Counter(f.category for f in findings)

    if any(f.severity == "critical" for f in findings):
        plan.append(
            "Resolve critical vulnerabilities and exposed credentials before broader modernization."
        )

    if categories["security"]:
        plan.append(
            "Remove unsafe execution, transport, deserialization and data-access patterns."
        )

    if categories["legacy"]:
        plan.append(
            "Replace deprecated or legacy APIs with supported language and framework alternatives."
        )

    if categories["maintainability"] or categories["quality"]:
        plan.append(
            "Reduce technical-debt hotspots and simplify difficult-to-maintain source structures."
        )

    if categories["observability"]:
        plan.append(
            "Replace ad-hoc console output with structured application logging."
        )

    plan.append(
        "Add regression tests around current behavior before applying potentially behavior-changing refactors."
    )

    plan.append(
        "Apply deterministic safe transformations first, then review remaining recommendations manually."
    )

    return plan


def create_summary(
    findings: list[Finding],
    overall_score: int,
) -> str:
    if not findings:
        return (
            "RecodeAI found no high-confidence modernization issues "
            "using the current deterministic analysis rules."
        )

    counts = Counter(f.severity for f in findings)

    return (
        f"RecodeAI detected {len(findings)} modernization finding(s): "
        f"{counts['critical']} critical, {counts['high']} high, "
        f"{counts['medium']} medium and {counts['low']} low. "
        f"The modernization health score is {overall_score}/100."
    )
