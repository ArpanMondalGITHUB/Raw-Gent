from google.adk.agents import LlmAgent
from .feature_prompt import Feature_Prompt
from Raw_Gent.tools import list_files_in_repo, read_file_from_repo, write_file_to_repo

Feature_Workflow_Agent = LlmAgent(
    name="feature_workflow",
    model="gemini-3.1-flash-lite-preview",
    description="Implement requested features directly in the repository.",
    instruction=Feature_Prompt,
    tools=[list_files_in_repo, read_file_from_repo, write_file_to_repo],
)
