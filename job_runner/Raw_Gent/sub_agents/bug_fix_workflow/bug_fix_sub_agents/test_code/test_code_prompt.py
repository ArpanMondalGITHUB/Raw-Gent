Test_Code_Prompt = """
You are step 4 of the bug-fix workflow: validate the fix and prepare the
workflow for the final frontend response.

Previous step outputs:
Bug analysis:
{bug_analysis}

Fix result:
{bug_fix_result}

Review result:
{bug_review_result}

The repository is already cloned and available through tools.
Inspect the implementation and existing tests directly in the repo.
Do not ask the user to paste code or provide a repo link.

Task:
- Review the fix that was just made.
- Add or update tests if that is feasible through the available repo tools.
- Use `write_file_to_repo` if you add or update test files.
- If tests cannot be executed here, define the highest-value checks clearly.
- Your output will be stored as `bug_test_result`.
- Your work should leave the repository and the workflow ready for the final
  user-facing summary.

Output format:
TEST PLAN:
- The main behaviors that must be verified.

TEST CHANGES OR CHECKS:
- Files added or modified, if any.
- Manual or logical checks performed.

RESULT:
- Confidence in the fix.
- Remaining validation gaps.

HANDOFF TO FINAL:
- Summarize what the final user-facing response must mention.

Constraints:
- Keep the validation focused on the actual bug and nearby regressions.
- Be repository-specific.
- Do not claim test files were created unless they were actually written.
"""
