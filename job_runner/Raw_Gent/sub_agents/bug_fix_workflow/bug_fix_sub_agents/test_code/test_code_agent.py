from google.adk.agents import LlmAgent
from . import test_code_prompt

Test_Code_Agent = LlmAgent(
    name="test_code",
    model="gemini-2.0-flash",
    description="",
    instruction=test_code_prompt.Test_Fix_Agent
)