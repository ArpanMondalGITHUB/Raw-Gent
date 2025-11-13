import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
import { Button } from "./ui/button";
import { ArrowRight, ChevronRight, ChevronRightIcon } from "lucide-react";
import Editor, { DiffEditor } from "@monaco-editor/react";

export function Chatui() {
  return (
    <div
      className="bg-[#28252b] p-0 absolute top-[48px] left-64 right-0 bottom-0 flex flex-col
         text-white font-normal text-[13px] overflow-hidden"
    >
      <PanelGroup direction="horizontal" className="flex-1">
        <Panel
          defaultSize={30}
          minSize={20}
          className="border-r border-gray-700 flex flex-col"
        >
          {/* Panel Header*/}
          <div className="h-10 px-4 border-b border-gray-700 flex items-center justify-between bg-[#28252b] flex-shrink-0">
            <span className="text-white font-sans font-medium">Chat Panel</span>
          </div>

          {/* Chat Messages Area */}
          <div className="flex-1 overflow-y-auto overflow-x-hidden ">
            <div className="p-4 space-y-2 min-h-full">
              <div className="bg-zinc-900 p-2 rounded-md w-fit">Hey!</div>
              <div className="bg-zinc-700 p-2 rounded-md w-fit ml-auto">
                Hello world
              </div>
              <div className="bg-zinc-900 p-2 rounded-md w-fit">
                How are you?
              </div>
              <div className="bg-zinc-700 p-2 rounded-md w-fit ml-auto">
                I'm doing great, thanks!
              </div>
              <div className="bg-zinc-900 p-2 rounded-md w-fit">
                That's awesome! What are you working on today?
              </div>
              <div className="bg-zinc-700 p-2 rounded-md w-fit ml-auto">
                Building some cool layouts with React and Tailwind
              </div>
              <div className="bg-zinc-900 p-2 rounded-md w-fit">Nice!</div>
              <div className="bg-zinc-700 p-2 rounded-md w-fit ml-auto">
                Yeah, it's pretty fun
              </div>
            </div>
          </div>

          {/* Input Area - Sticky Bottom */}
          <div className="p-4 border-gray-700 bg-[#28252b] flex-shrink-0">
            <div className="bg-zinc-700 rounded-3xl flex px-3 items-center">
              <input
                type="text"
                placeholder="Type your message..."
                className="w-full p-3 bg-transparent rounded-3xl focus:outline-none font-semibold font-sans placeholder-gray-400"
              />
              <Button className="hover:bg-zinc-600" size="sm" variant="ghost">
                <ArrowRight className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </Panel>

        <PanelResizeHandle />

        <Panel
          defaultSize={30}
          minSize={20}
          className="border-l border-gray-700 flex flex-col"
        >
          {/* Right Panel Header */}
          <div className="h-10 px-4 border-b border-gray-700 flex items-center justify-between bg-[#28252b] flex-shrink-0">
            <span className="text-white font-sans font-medium">
              Main Content
            </span>
          </div>

          {/* Right Panel Content */}
          <div className="flex-1">
            <div className="text-gray-400 text-center mt-8">
              <DiffEditor
                height="90vh"
                theme="vs-dark"
                original=""
                modified=""
                language=""
                modifiedLanguage=""
                originalLanguage=""                                
              />
            </div>
          </div>
        </Panel>
      </PanelGroup>
    </div>
  );
}
