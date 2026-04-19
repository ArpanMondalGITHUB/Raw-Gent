from google.adk.agents import LlmAgent
from .test_code_prompt import Test_Code_Prompt
from Raw_Gent.tools import list_files_in_repo, read_file_from_repo, write_file_to_repo

Test_Code_Agent = LlmAgent(
    name="test_code",
    model="gemini-3.1-flash-lite-preview",
    description="Validate the bug fix and add targeted repository tests when appropriate.",
    instruction=Test_Code_Prompt,
    output_key="bug_test_result",
    tools=[list_files_in_repo, read_file_from_repo, write_file_to_repo],
)
