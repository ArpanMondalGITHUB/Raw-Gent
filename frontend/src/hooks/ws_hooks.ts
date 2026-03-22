import {
  AgentMessage,
  AgentMessageSchema,
  JobStatusResponse,
  JobStatusResponseSchema,
  WebScoketMessageResponse,
  WebScoketMessageResponseSchema,
} from "../schemas/run_agent.schemas";
import { useCallback, useEffect, useRef, useState } from "react";

export function useWebsocket(job_id: string | null) {
  const wsRef = useRef<WebSocket | null>(null);
  const [isConnected, setisConnected] = useState(false);
  const [messages, setMessages] = useState<AgentMessage[]>([]);
  const [jobStatus, setJobStatus] = useState<JobStatusResponse | null>(null);
  const connect = useCallback(() => {
    if (!job_id) return;

    const wsURL = import.meta.env.VITE_WS_URL;

    const ws = new WebSocket(`${wsURL}/ws/status/${job_id}`);

    wsRef.current = ws;

    ws.onopen = () => {
      console.log("websocket is connected");
      setisConnected(true);
    };

    ws.onmessage = (event) => {
      const raw = JSON.parse(event.data);
      console.log(`"message recieved:"${raw}`);
      if (raw?.type === "ping") {
        ws.send(
          JSON.stringify({
            type: "pong",
            timestamp: new Date().toISOString(),
          }),
        );
        console.log("💚 Sent pong");
        return;
      }

      // ✅ Zod validates + narrows the type in one shot
      const result = WebScoketMessageResponseSchema.safeParse(raw);
      if (!result.success) {
        console.warn("⚠️ Invalid message:", result.error.message);
        return;
      }

      // After safeParse — message is fully typed as WebScoketMessageResponse
      const message: WebScoketMessageResponse = result.data;

      switch (message.type) {
        case "status_update": {
          // content is a JSON string containing JobStatusResponse
          const statusResult = JobStatusResponseSchema.safeParse(
            JSON.parse(message.content),
          );
          if (statusResult.success) {
            setJobStatus(statusResult.data);
            setMessages(statusResult.data.messages);
          }
          break;
        }

        case "agent_message": {
          const result = AgentMessageSchema.safeParse({
            role: "agent",
            content: message.content,
            timestamp: message.timestamp,
          });
          if (result.success) setMessages((prev) => [...prev, result.data]);
          break;
        }

        case "user_message": {
          const result = AgentMessageSchema.safeParse({
            role: "user",
            content: message.content,
            timestamp: message.timestamp,
          });
          if (result.success) setMessages((prev) => [...prev, result.data]);
          break;
        }

        case "error": {
          console.error("❌ Server error:", message.content);
          break;
        }
      }
    };

    ws.onerror = () => setisConnected(false);

    // ✅ ws.onclose not ws.close (bug in your version)
    ws.onclose = () => {
      setisConnected(false);
      wsRef.current = null;
    };
  }, [job_id]);

  useEffect(() => {
    connect();
    return () => wsRef.current?.close();
  }, [connect]);

  const onSendMessage = useCallback(
    (content: string) => {
      if (!job_id || wsRef.current?.readyState !== WebSocket.OPEN) return;

      const message: WebScoketMessageResponse = {
        type: "user_message",
        content: content,
        job_id: job_id,
        timestamp: new Date().toISOString(),
      };

      wsRef.current.send(JSON.stringify(message));
    },
    [job_id],
  );

  const disconnect = useCallback(() => {
    wsRef.current?.close();
    wsRef.current = null;
  }, []);

  return { isConnected, jobStatus, messages, onSendMessage, disconnect };
}
