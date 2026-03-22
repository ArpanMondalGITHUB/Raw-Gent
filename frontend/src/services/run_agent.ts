import { JobStatusResponse, RunAgentRequest, RunAgentResponse } from "@/schemas/run_agent.schemas";
import apiClient from "./api"
const agentApi = {
  runAgent:async (data:RunAgentRequest): Promise<RunAgentResponse> => {
    const response = await apiClient.post("/agent/run",data);
    return response.data;
  },

  getJobStatus:async (job_id: string): Promise<JobStatusResponse> => {
    const response = await apiClient.get(`/agent/status/${job_id}`)
    return response.data
  }
}
export default agentApi;