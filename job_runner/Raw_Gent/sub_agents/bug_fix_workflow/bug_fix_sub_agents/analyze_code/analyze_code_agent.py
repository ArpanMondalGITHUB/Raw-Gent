from google.adk.agents import LlmAgent
from .analyze_code_prompt import Analyze_Code_Prompt
from Raw_Gent.tools import list_files_in_repo, read_file_from_repo

Analyze_Code_Agent = LlmAgent(
    name="analyze_code",
    model="gemini-3.1-flash-lite-preview",
    description="Analyze the repository directly to identify a concrete bug and its root cause.",
    instruction=Analyze_Code_Prompt,
    output_key="bug_analysis",
    tools=[list_files_in_repo, read_file_from_repo],
)
