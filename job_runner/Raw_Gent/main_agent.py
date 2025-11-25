from google.adk.agents import LlmAgent
from Raw_Gent import prompt
from Raw_Gent.tools import read_file_from_repo, write_file_to_repo, list_files_in_repo
from .sub_agents.bug_fix_workflow import bug_fix_workflow_agent
from .sub_agents.code_improver_workflow import code_improver_workflow_agent
from .sub_agents.feature_workflow import feature_workflow_agent
from .sub_agents.test_workflow import test_workflow_agent

root_agent = LlmAgent(
    name="Raw_Gent",
    model="gemini-2.5-pro",
    description=" you are the primary agent . Route user requests to appropriate specialist agents ",
    instruction=prompt.ROOT_AGENT,
    sub_agents=[
        bug_fix_workflow_agent.Bug_Fix_Workflow_Agent,     # Sequential steps for bug fixing
        code_improver_workflow_agent.Code_Improver_Workflow_Agent,     # Parallel work for features
        feature_workflow_agent.Feature_Workflow_Agent,
        test_workflow_agent.Test_Workflow_Agent
    ],
    tools=[
        read_file_from_repo,
        write_file_to_repo,
        list_files_in_repo
    ],
)



