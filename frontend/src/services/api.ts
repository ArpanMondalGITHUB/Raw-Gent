import axios from "axios"

const baseURL = "https://raw-gent.onrender.com"


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