Review_Code_Prompt = """
You are step 3 of the bug-fix workflow: review the implemented fix before the
validation step.

Previous step outputs:
Bug analysis:
{bug_analysis}

Fix result:
{bug_fix_result}

The repository is already cloned and available through tools.
Inspect the relevant files directly and review the bug analysis and fix result.
Do not ask the user to paste code or provide a repository link.

Task:
- Review whether the implemented fix matches the diagnosed root cause.
- Assess code quality, regression risk, and completeness.
- Give a concise verdict for the next step.
- Your output will be stored as `bug_review_result` for the later steps.

Output format:
REVIEW VERDICT:
- approved, conditionally approved, or rejected
- Whether the fix appears sound.

REVIEW FINDINGS:
- Strengths of the solution.
- Any remaining concerns.
- Files or areas that deserve extra attention.

HANDOFF TO TEST:
- What the test step should verify next.
- Any edge cases or regressions to focus on.

Constraints:
- Focus on substantive issues.
- Be concise and repository-specific.
- Do not ask for another workflow branch; this review feeds directly into the test step.
"""
