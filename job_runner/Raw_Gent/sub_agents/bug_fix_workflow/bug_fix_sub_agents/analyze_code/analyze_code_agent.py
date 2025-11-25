from google.adk.agents import LlmAgent
from . import analyze_code_prompt

Analyze_Code_Agent = LlmAgent(
    name="analyze_code",
    model="gemini-2.0-flash",
    description="",
    instruction=analyze_code_prompt.Analyze_Code_Prompt
)