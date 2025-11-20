from google.adk.agents import LlmAgent
from analyze_code import analyze_code_prompt
from core.config import GEMINI_API_KEY

Analyze_Code_Agent = LlmAgent(
    name="analyze_code",
    model="gemini-2.0-flash",
    model_param = GEMINI_API_KEY,
    description="",
    instruction=analyze_code_prompt.Analyze_Code_Prompt
)