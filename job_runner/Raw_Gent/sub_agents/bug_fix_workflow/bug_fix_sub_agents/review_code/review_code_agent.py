from google.adk.agents import LlmAgent
from . import review_code_prompt

Review_Code_Agent = LlmAgent(
    name="review_code",
    model="gemini-2.0-flash",
    description="",
    instruction=review_code_prompt.Review_Fix_Agent
    )