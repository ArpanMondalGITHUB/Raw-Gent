from google.adk.agents import LlmAgent
from .test_code_prompt import Test_Code_Prompt

Test_Code_Agent = LlmAgent(
    name="test_code",
    model="gemini-2.0-flash",
    description="",
    instruction=Test_Code_Prompt
)