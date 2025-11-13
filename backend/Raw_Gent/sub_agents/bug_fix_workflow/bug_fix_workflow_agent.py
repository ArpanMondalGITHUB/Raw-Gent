from google.adk.agents import SequentialAgent
from .bug_fix_sub_agents.analyze_code import analyze_code_agent
from .bug_fix_sub_agents.fix_code import fix_code_agent
from .bug_fix_sub_agents.review_code import review_code_agent
from .bug_fix_sub_agents.test_code import test_code_agent


Bug_Fix_Workflow_Agent = SequentialAgent(
    name="bug_fix_workflow",
    description= "Executes a sequence of code analyzing, fix, test and  review code.",
    sub_agents = [
        analyze_code_agent.Analyze_Code_Agent,    # Step 1: Find the bug
        fix_code_agent.Fix_Code_Agent,        # Step 2: Fix it  
        test_code_agent.Test_Code_Agent,       # Step 3: Test the fix
        review_code_agent.Review_Code_Agent      # Step 4: Review the fix
    ]
)