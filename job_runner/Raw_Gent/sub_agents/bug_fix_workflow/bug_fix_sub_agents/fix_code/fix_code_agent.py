from google.adk.agents import LlmAgent
from core.config import GEMINI_API_KEY
from fix_code import fix_code_prompt
Fix_Code_Agent = LlmAgent(
    name="fix_code",
    model="gemini-2.0-flash",
    model_param = GEMINI_API_KEY,
    description="",
    description=fix_code_prompt.Fix_Bug_Agent
)