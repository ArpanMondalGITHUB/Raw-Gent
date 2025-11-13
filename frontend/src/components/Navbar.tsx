import { GiftIcon, GithubIcon, MessageSquare, PlusIcon, Settings } from "lucide-react";
import { Button } from "./ui/button";

export function Navbar() {
    return(
        <div className=" absolute top-0 left-64 right-0 flex h-[48px] pr-10 bg-[#1d1b1f] text-white justify-between items-center">
            {/* right section */}
            <div className="flex ml-4 text-white text-[13px] gap-2 font-sans">
                <GithubIcon className="w-5 h-5"/>
                <span className="text-white text-[13px]"> heloo world </span>
            </div>

            {/* left section */}
            <div className="flex items-center gap-4">

                <Button size="sm" className="bg-purple-600 hover:bg-purple-700">
                    <PlusIcon className=""/>
                </Button>

                <Button size="sm" className="text-purple-600 hover:bg-slate-800">
                    <GiftIcon className=""/>
                    
                </Button>

                <Button size="sm" className="hover:bg-slate-800 gap-1">
                    <MessageSquare className=""/>
                    <span className="text-white">Feedback</span>
                </Button>

                <Button size="sm" className="hover:bg-slate-800">
                    <Settings className=""/>
                </Button>
            </div>
        </div>
    );
}