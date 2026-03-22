import axios from "axios"

const AXIOS_BASE_URL = import.meta.env.VITE_API_URL;
const apiClient  = axios.create(
    {
        baseURL: AXIOS_BASE_URL,
        headers:{
            'Content-Type': 'application/json',
        },
        withCredentials: true
    }
)
export default apiClient;