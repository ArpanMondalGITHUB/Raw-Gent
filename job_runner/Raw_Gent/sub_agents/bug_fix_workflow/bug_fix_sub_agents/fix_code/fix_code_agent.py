from google.adk.agents import LlmAgent
from .fix_code_prompt import Fix_Code_Prompt

Fix_Code_Agent = LlmAgent(
    name="fix_code",
    model="gemini-2.0-flash",
    description="",
    instruction=Fix_Code_Prompt
)