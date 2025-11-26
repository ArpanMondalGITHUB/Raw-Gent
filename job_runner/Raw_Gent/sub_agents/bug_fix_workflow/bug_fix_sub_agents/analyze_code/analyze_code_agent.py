from google.adk.agents import LlmAgent
from .analyze_code_prompt import Analyze_Code_Prompt

Analyze_Code_Agent = LlmAgent(
    name="analyze_code",
    model="gemini-2.0-flash",
    description="",
    instruction=Analyze_Code_Prompt
)