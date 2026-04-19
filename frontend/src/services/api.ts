import axios from "axios"
import { API_BASE_URL } from "../config/runtime";

const apiClient  = axios.create(
    {
        baseURL: API_BASE_URL,
        headers:{
            'Content-Type': 'application/json',
        },
        withCredentials: true
    }
)
export default apiClient;
