import { Chatui } from "../components/Chatui";
import { AppSidebar } from "../components/AppSidebar";
import { Navbar } from "../components/Navbar";

const Task = () => {
    return ( 
        <div className="min-h-screen flex bg-[#0a0a0a] relative">
            <AppSidebar/>
            <Chatui/>
            <Navbar/>
            
        </div>
     );
}
 
export default Task;