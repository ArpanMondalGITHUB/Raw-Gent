from google.adk.agents import LlmAgent
from .test_code_prompt import Test_Code_Prompt

Test_Code_Agent = LlmAgent(
    name="test_code",
    model="gemini-3.1-flash-lite-preview",
    description="",
    instruction=Test_Code_Prompt
)