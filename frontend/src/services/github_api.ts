import apiClient from "./api"

export const fetchInstallRepos = async() => {
    const response = await apiClient.get("/installation-repos")
    return response.data
}

export const fetchbranch = async (repo_name:string) => {
    const response = await apiClient.get(`/branches/${repo_name}`);
    return response.data;
}