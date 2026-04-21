from google.adk.agents import LlmAgent
from .code_improver_prompt import Code_Improver_Prompt
from Raw_Gent.tools import list_files_in_repo, read_file_from_repo, write_file_to_repo

Code_Improver_Workflow_Agent = LlmAgent(
    name="code_improver_workflow",
    model="gemini-3.1-flash-lite-preview",
    description="Inspect the repository and improve code quality or maintainability.",
    instruction=Code_Improver_Prompt,
    tools=[list_files_in_repo, read_file_from_repo, write_file_to_repo],
)
