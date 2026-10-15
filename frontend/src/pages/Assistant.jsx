import { useEffect, useRef, useState } from "react";

import { useChat } from "../hooks/useChat";
import { SUGGESTED_PROMPTS } from "../context/chatContext";
import { ChatBubble, TypingIndicator, SuggestionChips } from "../components/ChatBubble";

export default function Assistant() {
  const { messages, sending, error, send, clearConversation } = useChat();
  const [input, setInput] = useState("");
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, sending]);

  const handleSubmit = (e) => {
    e.preventDefault();
    const text = input;
    setInput("");
    send(text);
  };

  const lastMessage = messages.at(-1);
  const showSuggestions = !sending && (messages.length === 0 || lastMessage?.role === "assistant");

  return (
    <div className="px-6 md:px-10 py-8 flex flex-col h-[calc(100vh-64px)]">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h1 className="font-display text-2xl">FootballIQ Assistant</h1>
          <p className="text-xs text-[var(--color-text-muted)]">
            Ask about players, stats, or football knowledge in general.
          </p>
        </div>
        {messages.length > 0 && (
          <button
            onClick={clearConversation}
            className="text-xs px-3 py-1.5 rounded border border-[var(--color-border-strong)] hover:bg-[var(--color-panel-raised)]"
          >
            Clear conversation
          </button>
        )}
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto space-y-3 pr-1">
        {messages.map((m, i) => (
          <ChatBubble key={i} role={m.role} content={m.content} sources={m.sources} />
        ))}
        {sending && <TypingIndicator />}
        {error && (
          <div className="border border-[var(--color-negative)]/30 bg-[var(--color-negative)]/10 rounded p-3 text-xs text-[var(--color-negative)]">
            {error}
          </div>
        )}
        {showSuggestions && (
          <div className="pt-1">
            <SuggestionChips prompts={SUGGESTED_PROMPTS} onPick={send} disabled={sending} />
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="flex gap-2 mt-4 pt-4 border-t border-[var(--color-border)]">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask the assistant..."
          className="flex-1 bg-[var(--color-panel)] border border-[var(--color-border-strong)] rounded px-3 py-2.5 text-sm"
        />
        <button
          type="submit"
          disabled={sending || !input.trim()}
          className="px-5 py-2.5 rounded bg-[var(--color-amber)] text-[var(--color-bg)] text-sm font-medium hover:opacity-90 disabled:opacity-50"
        >
          Send
        </button>
      </form>
    </div>
  );
}
