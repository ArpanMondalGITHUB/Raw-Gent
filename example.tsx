// import { useEffect, useMemo, useRef, useState } from "react";
// import { Panel, PanelGroup, PanelResizeHandle } from "react-resizable-panels";
// import { Button } from "./ui/button";
// import { ArrowRight, CheckCircle2, Circle, CircleDot, XCircle } from "lucide-react";
// import { DiffEditor } from "@monaco-editor/react";
// import { AgentMessage, JobStatusResponse } from "../schemas/run_agent.schemas";

// export interface ChatuiProps {
//   jobStatus: JobStatusResponse | null;
//   messages: AgentMessage[];
//   onSendMessage: (content: string) => void;
//   isConnected: boolean;
// }

// function statusBadge(status?: string) {
//   switch (status) {
//     case "queued":
//       return (
//         <span className="inline-flex items-center gap-2 rounded-full bg-yellow-600/20 px-3 py-1 text-xs font-medium text-yellow-100">
//           <Circle className="h-3 w-3" />
//           Queued
//         </span>
//       );
//     case "running":
//       return (
//         <span className="inline-flex items-center gap-2 rounded-full bg-sky-600/20 px-3 py-1 text-xs font-medium text-sky-100">
//           <CircleDot className="h-3 w-3" />
//           Running
//         </span>
//       );
//     case "completed":
//       return (
//         <span className="inline-flex items-center gap-2 rounded-full bg-emerald-600/20 px-3 py-1 text-xs font-medium text-emerald-100">
//           <CheckCircle2 className="h-3 w-3" />
//           Completed
//         </span>
//       );
//     case "failed":
//       return (
//         <span className="inline-flex items-center gap-2 rounded-full bg-rose-600/20 px-3 py-1 text-xs font-medium text-rose-100">
//           <XCircle className="h-3 w-3" />
//           Failed
//         </span>
//       );
//     default:
//       return (
//         <span className="inline-flex items-center gap-2 rounded-full bg-neutral-600/20 px-3 py-1 text-xs font-medium text-neutral-100">
//           <Circle className="h-3 w-3" />
//           Unknown
//         </span>
//       );
//   }
// }

// export function Chatui({ jobStatus, messages, onSendMessage, isConnected }: ChatuiProps) {
//   const [draft, setDraft] = useState("");
//   const [selectedFilePath, setSelectedFilePath] = useState<string | null>(null);

//   const fileChanges = useMemo(() => jobStatus?.file_changes ?? [], [jobStatus?.file_changes]);

//   const sortedFileChanges = useMemo(() => {
//     const priority: Record<string, number> = {
//       modified: 0,
//       created: 1,
//       deleted: 2,
//     };

//     return [...fileChanges].sort((a, b) => {
//       const pa = priority[a.change_type] ?? 99;
//       const pb = priority[b.change_type] ?? 99;
//       if (pa !== pb) return pa - pb;
//       return a.file_path.localeCompare(b.file_path);
//     });
//   }, [fileChanges]);

//   const selectedFile = useMemo(() => {
//     if (!sortedFileChanges.length) return undefined;
//     if (selectedFilePath) {
//       return sortedFileChanges.find((f) => f.file_path === selectedFilePath) ?? sortedFileChanges[0];
//     }
//     return sortedFileChanges[0];
//   }, [selectedFilePath, sortedFileChanges]);

//   // Keep selection valid when file list changes
//   useEffect(() => {
//     if (!sortedFileChanges.length) {
//       setSelectedFilePath(null);
//       return;
//     }

//     if (!selectedFilePath) {
//       setSelectedFilePath(sortedFileChanges[0].file_path);
//       return;
//     }

//     const exists = sortedFileChanges.some((f) => f.file_path === selectedFilePath);
//     if (!exists) {
//       setSelectedFilePath(sortedFileChanges[0].file_path);
//     }
//   }, [sortedFileChanges, selectedFilePath]);

//   const lastMessage = useMemo(() => {
//     if (messages.length === 0) return "No messages yet.";
//     return messages[messages.length - 1].content;
//   }, [messages]);

//   const messagesEndRef = useRef<HTMLDivElement | null>(null);

//   useEffect(() => {
//     messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
//   }, [messages]);

//   const send = () => {
//     const trimmed = draft.trim();
//     if (!trimmed) return;
//     onSendMessage(trimmed);
//     setDraft("");
//   };

//   return (
//     <div
//       className="bg-[#28252b] p-0 absolute top-[48px] left-64 right-0 bottom-0 flex flex-col text-white font-normal text-[13px] overflow-hidden"
//       role="main"
//     >
//       <PanelGroup direction="horizontal" className="flex-1">
//         <Panel
//           defaultSize={30}
//           minSize={22}
//           className="border-r border-gray-700 flex flex-col"
//         >
//           {/* Panel Header */}
//           <div className="h-10 px-4 border-b border-gray-700 flex items-center justify-between bg-[#28252b] flex-shrink-0">
//             <div className="flex flex-col">
//               <span className="text-white font-sans font-semibold">Task updates</span>
//               <span className="text-xs text-gray-400">{jobStatus?.job_id ?? "No job selected"}</span>
//             </div>
//             <div className="flex items-center gap-2">
//               {statusBadge(jobStatus?.status)}
//               <span
//                 className={`text-xs font-medium ${
//                   isConnected ? "text-emerald-200" : "text-rose-200"
//                 }`}
//               >
//                 {isConnected ? "Connected" : "Disconnected"}
//               </span>
//             </div>
//           </div>

//           {/* Messages + Status Summary */}
//           <div className="flex-1 overflow-y-auto overflow-x-hidden">
//             <div className="p-4 space-y-4">
//               <div className="rounded-xl border border-gray-700 bg-[#1e1b22] p-4">
//                 <div className="flex items-center justify-between">
//                   <h3 className="text-sm font-semibold text-white">Latest Message</h3>
//                   <span className="text-xs text-gray-400">{new Date().toLocaleTimeString()}</span>
//                 </div>
//                 <p className="mt-2 text-sm text-gray-200">{lastMessage}</p>
//               </div>

//               <div className="rounded-xl border border-gray-700 bg-[#1e1b22] p-4">
//                 <h3 className="text-sm font-semibold text-white">File changes</h3>
//                 {sortedFileChanges.length === 0 ? (
//                   <p className="mt-2 text-sm text-gray-400">No changes detected yet.</p>
//                 ) : (
//                   <ul className="mt-2 space-y-2">
//                     {sortedFileChanges.map((file) => (
//                       <li key={file.file_path}>
//                         <button
//                           className={`w-full text-left rounded-lg px-3 py-2 text-sm transition-all hover:bg-zinc-700/50 ${
//                             selectedFilePath === file.file_path ? "bg-zinc-700/60" : ""
//                           }`}
//                           onClick={() => setSelectedFilePath(file.file_path)}
//                         >
//                           <span className="font-medium text-white">{file.file_path}</span>
//                           <span className="ml-2 text-xs text-gray-400">{file.change_type}</span>
//                         </button>
//                       </li>
//                     ))}
//                   </ul>
//                 )}
//               </div>

//               <div className="rounded-xl border border-gray-700 bg-[#1e1b22] p-4">
//                 <h3 className="text-sm font-semibold text-white">Conversation</h3>
//                 <div className="mt-3 space-y-2">
//                   {messages.length === 0 ? (
//                     <p className="text-sm text-gray-400">No messages yet, start the conversation below.</p>
//                   ) : (
//                     messages.map((message, index) => {
//                       const isAgent = message.role === "agent";
//                       return (
//                         <div
//                           key={`${message.timestamp}-${index}`}
//                           className={`flex items-start gap-2 rounded-xl px-3 py-2 text-sm ${
//                             isAgent
//                               ? "bg-zinc-900 text-gray-100"
//                               : "bg-zinc-700 text-gray-100 ml-auto"
//                           } w-fit max-w-full`}
//                         >
//                           <div
//                             className={`flex h-7 w-7 items-center justify-center rounded-full text-xs font-semibold text-white ${
//                               isAgent ? "bg-sky-600" : "bg-emerald-600"
//                             }`}
//                           >
//                             {isAgent ? "A" : "U"}
//                           </div>
//                           <div>
//                             <div className="font-medium text-xs text-gray-300">
//                               {isAgent ? "Agent" : "You"}
//                             </div>
//                             <div className="mt-1 whitespace-pre-wrap">{message.content}</div>
//                             <div className="mt-1 text-[11px] text-gray-500">
//                               {new Date(message.timestamp).toLocaleTimeString()}
//                             </div>
//                           </div>
//                         </div>
//                       );
//                     })
//                   )}
//                 </div>
//                 <div ref={messagesEndRef} />
//               </div>
//             </div>
//           </div>

//           {/* Input Area - Sticky Bottom */}
//           <div className="p-4 border-t border-gray-700 bg-[#28252b] flex-shrink-0">
//             <div className="bg-zinc-700 rounded-3xl flex items-center gap-2 px-3 py-2">
//               <input
//                 value={draft}
//                 onChange={(e) => setDraft(e.target.value)}
//                 onKeyDown={(e) => {
//                   if (e.key === "Enter" && !e.shiftKey) {
//                     e.preventDefault();
//                     send();
//                   }
//                 }}
//                 type="text"
//                 placeholder="Type a message and hit enter..."
//                 className="flex-1 bg-transparent text-sm font-semibold text-white outline-none placeholder:text-gray-400"
//               />
//               <Button
//                 disabled={!draft.trim() || !isConnected}
//                 onClick={send}
//                 className="h-9 w-9 rounded-full"
//                 size="sm"
//                 variant="ghost"
//               >
//                 <ArrowRight className="w-4 h-4" />
//               </Button>
//             </div>
//           </div>
//         </Panel>

//         <PanelResizeHandle />

//         <Panel
//           defaultSize={70}
//           minSize={20}
//           className="border-l border-gray-700 flex flex-col"
//         >
//           {/* Right Panel Header */}
//           <div className="h-10 px-4 border-b border-gray-700 flex items-center justify-between bg-[#28252b] flex-shrink-0">
//             <div>
//               <span className="text-white font-sans font-medium">Diff Viewer</span>
//               <span className="ml-2 text-xs text-gray-400">
//                 {selectedFile ? selectedFile.file_path : "Select a file to view diff"}
//               </span>
//             </div>
//             <div className="flex items-center gap-2">
//               <span className="text-xs text-gray-400">
//                 Updates: {jobStatus?.file_changes.length ?? 0}
//               </span>
//             </div>
//           </div>

//           {/* Right Panel Content */}
//           <div className="flex-1 relative">
//             {selectedFile ? (
//               <DiffEditor
//                 height="100%"
//                 theme="vs-dark"
//                 original={selectedFile.original_content ?? ""}
//                 modified={selectedFile.modified_content}
//                 language={selectedFile.language ?? ""}
//                 options={{ renderSideBySide: true, readOnly: true }}
//               />
//             ) : (
//               <div className="flex h-full flex-col items-center justify-center gap-3 text-center text-gray-400">
//                 <div className="text-lg font-semibold">No file selected</div>
//                 <div className="max-w-xs text-sm">
//                   Select a file on the left to view its diff. New changes will appear here as the job progresses.
//                 </div>
//               </div>
//             )}
//           </div>
//         </Panel>
//       </PanelGroup>
//     </div>
//   );
// }
