from google.adk.agents import LlmAgent, SequentialAgent
from .bug_fix_sub_agents.analyze_code import analyze_code_agent
from .bug_fix_sub_agents.fix_code import fix_code_agent
from .bug_fix_sub_agents.review_code import review_code_agent
from .bug_fix_sub_agents.test_code import test_code_agent
from .bug_fix_prompt import Bug_Fix_Prompt
from Raw_Gent.tools import list_files_in_repo, read_file_from_repo

Bug_Fix_Result_Agent = LlmAgent(
    name="bug_fix_result",
    model="gemini-3.1-flash-lite-preview",
    description="Turn the completed bug-fix workflow into the final frontend response.",
    instruction=Bug_Fix_Prompt,
    tools=[list_files_in_repo, read_file_from_repo],
)

Bug_Fix_Workflow_Agent = SequentialAgent(
    name="bug_fix_workflow",
    description="Executes a sequence of analyze, fix, review, test, and final result delivery.",
    sub_agents = [
        analyze_code_agent.Analyze_Code_Agent,    # Step 1: Find the bug
        fix_code_agent.Fix_Code_Agent,        # Step 2: Fix it  
        review_code_agent.Review_Code_Agent,  # Step 3: Review the fix
        test_code_agent.Test_Code_Agent,      # Step 4: Validate and add tests
        Bug_Fix_Result_Agent,                 # Step 5: Produce the final frontend response
    ]
)
