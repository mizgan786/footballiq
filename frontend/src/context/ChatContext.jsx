import { useState, useCallback } from "react";
import { sendChatMessage } from "../services/api";
import { ChatContext } from "./chatContext";

export function ChatProvider({ children }) {
  const [messages, setMessages] = useState([]); // {role, content, sources?}
  const [sending, setSending] = useState(false);
  const [error, setError] = useState(null);

  const send = useCallback(
    async (text) => {
      const trimmed = text.trim();
      if (!trimmed || sending) return;

      const history = messages.map((m) => ({ role: m.role, content: m.content }));
      setMessages((prev) => [...prev, { role: "user", content: trimmed }]);
      setSending(true);
      setError(null);

      try {
        const data = await sendChatMessage(trimmed, history);
        setMessages((prev) => [...prev, { role: "assistant", content: data.reply, sources: data.sources }]);
      } catch (err) {
        const detail = err.response?.data?.detail;
        setError(typeof detail === "string" ? detail : err.message);
      } finally {
        setSending(false);
      }
    },
    [sending, messages]
  );

  const clearConversation = useCallback(() => {
    setMessages([]);
    setError(null);
  }, []);

  return (
    <ChatContext.Provider value={{ messages, sending, error, send, clearConversation }}>
      {children}
    </ChatContext.Provider>
  );
}
