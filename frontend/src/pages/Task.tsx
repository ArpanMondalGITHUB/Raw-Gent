import { Chatui } from "../components/Chatui";
import { AppSidebar } from "../components/AppSidebar";
import { Navbar } from "../components/Navbar";
import { useWebsocket } from "../hooks/ws_hooks"
const Task = () => {
    // get job_id from session storage
    const taskDataStr = sessionStorage.getItem("currentTask");
    const taskData = taskDataStr ?  JSON.parse(taskDataStr) : null;

     // ✅ Use WebSocket hook
    const { isConnected, jobStatus, messages, onSendMessage } = useWebsocket(taskData?.job_id);

    // if (!taskData?.job_id) {
    //     return (
    //         <div className="min-h-screen flex items-center justify-center bg-[#0a0a0a]">
    //             <p className="text-red-500">No job ID found</p>
    //         </div>
    //     );
    // }

    return ( 
        <div className="min-h-screen flex bg-[#0a0a0a] relative">
            <AppSidebar/>
            <Chatui 
            jobStatus = {jobStatus}
            messages = {messages}
            onSendMessage =  {onSendMessage}
            isConnected = {isConnected}
            />
            <Navbar/>
            
        </div>
     );
}
 
export default Task;