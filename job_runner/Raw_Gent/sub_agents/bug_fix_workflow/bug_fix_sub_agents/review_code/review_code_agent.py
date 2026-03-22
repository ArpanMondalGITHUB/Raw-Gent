from google.adk.agents import LlmAgent
from .review_code_prompt import Review_Code_Prompt

Review_Code_Agent = LlmAgent(
    name="review_code",
    model="gemini-3.1-flash-lite-preview",
    description="",
    instruction=Review_Code_Prompt
    )