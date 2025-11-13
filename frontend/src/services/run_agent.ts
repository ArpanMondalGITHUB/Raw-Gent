import apiClient from "./api"

export const runagent = async(prompt:string , repo_name:string , installation_id: number , branches:string) => {
    const response = await apiClient.post("/agent/run", {
    prompt,
    repo_name,
    installation_id,
    branches,
  });
  return  response.data;
}