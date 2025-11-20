from google.adk.agents import LlmAgent
from test_code import test_code_prompt
from core.config import GEMINI_API_KEY

Test_Code_Agent = LlmAgent(
    name="test_code",
    model="gemini-2.0-flash",
    model_param = GEMINI_API_KEY,
    description="",
    instruction=test_code_prompt.Test_Fix_Agent
)