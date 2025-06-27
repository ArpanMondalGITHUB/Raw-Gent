import axios from "axios"

const baseURL = "https://raw-gent.onrender.com"

console.log("baseURL:",baseURL)

const apiClient  = axios.create(
    {
        baseURL,
        headers:{
            'Content-Type': 'application/json',
        },
        withCredentials: true
    }
)
export default apiClient;