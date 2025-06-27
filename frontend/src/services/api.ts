import axios from "axios"

const baseURL = "https://amazed-infinitely-marten.ngrok-free.app"

console.log("baseURL:",baseURL)

const apiClient  = axios.create(
    {
        baseURL,
        headers:{
            'Content-Type': 'application/json',
            'ngrok-skip-browser-warning': 'true'
        },
        withCredentials: true
    }
)
export default apiClient;