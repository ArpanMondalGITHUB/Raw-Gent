from google.adk.agents import LlmAgent
from core.config import GEMINI_API_KEY
from review_code import review_code_prompt
Review_Code_Agent = LlmAgent(
    name="review_code",
    model="gemini-2.0-flash",
    model_param = GEMINI_API_KEY,
    description="",
    instruction=review_code_prompt.Review_Fix_Agent
    )