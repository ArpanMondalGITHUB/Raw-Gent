import apiClient from "./api"

export const fetchInstallRepos = async() => {
    const response = await apiClient.get("/installation-repos")
    return response.data
}

export const fetchbranch = async (repoName:string) => {
    const response = await apiClient.get(`/branches/${repoName}`);
    return response.data;
}