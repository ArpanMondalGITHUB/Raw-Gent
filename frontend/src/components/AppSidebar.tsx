import { ChevronDown, Search, GitBranch, CheckCircle } from "lucide-react";
import { Button } from "../components/ui/button";
import { Input } from "../components/ui/input";
import { useState } from "react";

export function AppSidebar() {
  const [isTasksExpanded, setIsTasksExpanded] = useState(true);
  const [isCodebasesExpanded, setIsCodebasesExpanded] = useState(true);

  return (
    <div className="left-0 top-0 absolute w-64 h-screen bg-[#141316] border-gray-800 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-800">
        <div className="flex items-center gap-2 mb-4">
          <div className="w-6 h-6 bg-gradient-to-br from-purple-500 to-blue-500 rounded-sm flex items-center justify-center">
            <span className="text-white text-xs font-bold">R</span>
          </div>
          <span className="text-white font-semibold">Raw-Gent</span>
          <span className="text-xs bg-gray-700 text-gray-300 px-2 py-0.5 rounded">beta</span>
        </div>
        
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-500 w-4 h-4" />
          <Input 
            placeholder="Search for repos or tasks"
            className="pl-10 bg-gray-900 border-gray-700 text-gray-300 placeholder-gray-500"
          />
        </div>
      </div>

      {/* Recent tasks */}
      <div className="flex-1 overflow-y-auto">
        <div className="p-4">
          <button 
            onClick={() => setIsTasksExpanded(!isTasksExpanded)}
            className="flex items-center gap-2 text-gray-400 hover:text-gray-300 mb-3 w-full"
          >
            <ChevronDown className={`w-4 h-4 transition-transform ${!isTasksExpanded ? '-rotate-90' : ''}`} />
            <span className="text-sm">Recent tasks</span>
          </button>
          
          {isTasksExpanded && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 p-2 hover:bg-gray-800 rounded cursor-pointer">
                
                <span className="text-sm text-gray-300 truncate"></span>
              </div>
            </div>
          )}
        </div>

        {/* Codebases */}
        <div className="p-4">
          <button 
            onClick={() => setIsCodebasesExpanded(!isCodebasesExpanded)}
            className="flex items-center gap-2 text-gray-400 hover:text-gray-300 mb-3 w-full"
          >
            <ChevronDown className={`w-4 h-4 transition-transform ${!isCodebasesExpanded ? '-rotate-90' : ''}`} />
            <span className="text-sm">Codebases</span>
          </button>
          
          {isCodebasesExpanded && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 p-2 hover:bg-gray-800 rounded cursor-pointer">
                <div className="flex-1 min-w-0">
                  <div className="text-sm text-gray-300"></div>
                  <div className="text-xs text-gray-500 truncate"></div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Footer */}
      <div className="p-4 border-t border-gray-800">
        <div className="text-xs text-gray-500 mb-2">
          Daily task limit (0/60)
        </div>
        <div className="flex gap-2">
          <Button variant="ghost" size="sm" className="text-gray-400 hover:text-gray-300">
            <span className="w-4 h-4">📄</span>
          </Button>
          <Button variant="ghost" size="sm" className="text-gray-400 hover:text-gray-300">
            <span className="w-4 h-4">💬</span>
          </Button>
          <Button variant="ghost" size="sm" className="text-gray-400 hover:text-gray-300">
            <span className="w-4 h-4">✖️</span>
          </Button>
        </div>
      </div>
    </div>
  );
}
