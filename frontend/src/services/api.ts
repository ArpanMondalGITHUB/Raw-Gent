import axios from "axios"

const baseURL = process.env.URL

console.log("baseURL:",{baseURL})

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