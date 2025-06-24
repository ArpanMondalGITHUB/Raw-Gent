import { Settings, MessageSquare } from "lucide-react";
import { Button } from "../components/ui/button";
import { useState } from "react";

export function TopBar() {
  const[user , setUser] = useState(null)
  
  return (
    <div className="absolute top-0 right-0 p-4 flex items-center gap-2 z-10">
      <Button variant="ghost" size="sm" className="text-gray-400 hover:text-gray-300">
        <MessageSquare className="w-4 h-4" />
        Feedback
      </Button>
      <Button variant="ghost" size="sm" className="text-gray-400 hover:text-stone-800">
        <Settings className="w-4 h-4" />
      </Button>
      <div className="w-8 h-8 bg-purple-600 rounded-full flex items-center justify-center">
        <span className="text-white text-sm font-semibold">{user}</span>
      </div>
    </div>
  );
}
