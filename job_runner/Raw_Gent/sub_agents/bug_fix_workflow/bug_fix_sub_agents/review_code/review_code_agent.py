from google.adk.agents import LlmAgent
from .review_code_prompt import Review_Code_Prompt

Review_Code_Agent = LlmAgent(
    name="review_code",
    model="gemini-2.0-flash",
    description="",
    instruction=Review_Code_Prompt
    )