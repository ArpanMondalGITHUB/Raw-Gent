from google.adk.agents import LlmAgent
from .review_code_prompt import Review_Code_Prompt
from Raw_Gent.tools import list_files_in_repo, read_file_from_repo

Review_Code_Agent = LlmAgent(
    name="review_code",
    model="gemini-3.1-flash-lite-preview",
    description="Review the implemented repository changes for correctness and risk.",
    instruction=Review_Code_Prompt,
    output_key="bug_review_result",
    tools=[list_files_in_repo, read_file_from_repo],
    )
