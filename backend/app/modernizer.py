import difflib
import re


def modernize(code: str, language: str):
    language = language.lower().strip()
    modernized = code
    changes: list[str] = []

    if language in {"javascript", "js"}:
        updated = re.sub(r"\bvar\s+", "let ", modernized)

        if updated != modernized:
            changes.append(
                "Replaced legacy JavaScript var declarations with let."
            )
            modernized = updated

    elif language == "java":
        updated = re.sub(
            r"\bVector\s*<([^>]+)>",
            r"ArrayList<\1>",
            modernized,
        )

        if updated != modernized:
            changes.append(
                "Replaced legacy Vector declarations with ArrayList."
            )
            modernized = updated

        updated = re.sub(
            r"\bHashtable\s*<([^>]+)>",
            r"HashMap<\1>",
            modernized,
        )

        if updated != modernized:
            changes.append(
                "Replaced legacy Hashtable declarations with HashMap."
            )
            modernized = updated

    elif language in {"python", "py", "python3"}:
        # Intentionally conservative.
        # Dangerous constructs such as eval/exec are reported but not
        # automatically rewritten because doing so could change behavior.
        pass

    if not changes:
        changes.append(
            "No deterministic safe rewrite was available. "
            "Review the modernization recommendations before changing behavior."
        )

    diff = "\n".join(
        difflib.unified_diff(
            code.splitlines(),
            modernized.splitlines(),
            fromfile="legacy",
            tofile="modernized",
            lineterm="",
        )
    )

    return modernized, changes, diff
