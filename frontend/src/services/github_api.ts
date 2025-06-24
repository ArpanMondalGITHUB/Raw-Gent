import apiClient from "./api"

export const fetchInstallRepos = async() => {
    const response = await apiClient.get("/installation-repos")
    return response.data
}