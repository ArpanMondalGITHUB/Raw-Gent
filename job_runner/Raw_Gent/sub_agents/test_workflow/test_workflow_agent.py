from google.adk.agents import LlmAgent
from .test_workflow_prompt import Test_Workflow_Prompt
from Raw_Gent.tools import list_files_in_repo, read_file_from_repo, write_file_to_repo

Test_Workflow_Agent = LlmAgent(
    name="test_workflow",
    model="gemini-3.1-flash-lite-preview",
    description="Inspect the repository and create or improve tests.",
    instruction=Test_Workflow_Prompt,
    tools=[list_files_in_repo, read_file_from_repo, write_file_to_repo],
)
