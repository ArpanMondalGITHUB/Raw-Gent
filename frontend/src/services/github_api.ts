import apiClient from "./api"

export const fetchInstallRepos = async() => {
    const response = await apiClient.get("/installation-repos")
    return response.data
}

export const fetchbranch = async (owner: string, repo_name: string) => {
  const response = await apiClient.get(`/branches/${repo_name}`, {
    params: { owner },
  });
  return response.data;
}