import { useContext } from "react";
import { ChatContext } from "../context/chatContext";

export function useChat() {
  const ctx = useContext(ChatContext);
  if (!ctx) throw new Error("useChat must be used within a ChatProvider");
  return ctx;
}
