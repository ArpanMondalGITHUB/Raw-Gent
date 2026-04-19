from google.adk.agents import LlmAgent
from .fix_code_prompt import Fix_Code_Prompt
from Raw_Gent.tools import list_files_in_repo, read_file_from_repo, write_file_to_repo

Fix_Code_Agent = LlmAgent(
    name="fix_code",
    model="gemini-3.1-flash-lite-preview",
    description="Implement a focused bug fix directly in the repository.",
    instruction=Fix_Code_Prompt,
    output_key="bug_fix_result",
    tools=[list_files_in_repo, read_file_from_repo, write_file_to_repo],
)
