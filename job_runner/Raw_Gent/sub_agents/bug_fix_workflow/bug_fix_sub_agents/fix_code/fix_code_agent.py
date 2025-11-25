from google.adk.agents import LlmAgent
from . import fix_code_prompt

Fix_Code_Agent = LlmAgent(
    name="fix_code",
    model="gemini-2.0-flash",
    description="",
    description=fix_code_prompt.Fix_Bug_Agent
)