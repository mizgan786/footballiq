import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";

import { useChat } from "../hooks/useChat";
import { SUGGESTED_PROMPTS } from "../context/chatContext";
import { ChatBubble, TypingIndicator, SuggestionChips } from "./ChatBubble";

export default function ChatWidget() {
  const location = useLocation();
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const { messages, sending, error, send, clearConversation } = useChat();
  const scrollRef = useRef(null);

  useEffect(() => {
    if (open) scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, sending, open]);

  // the full Assistant page already offers this - don't stack a duplicate on top of it
  if (location.pathname === "/assistant") return null;

  const handleSubmit = (e) => {
    e.preventDefault();
    const text = input;
    setInput("");
    send(text);
  };

  const lastMessage = messages.at(-1);
  const showSuggestions = !sending && (messages.length === 0 || lastMessage?.role === "assistant");

  return (
    <>
      {open && (
        <div className="fixed bottom-20 right-4 md:right-6 z-30 w-[calc(100vw-2rem)] max-w-[360px] h-[70vh] max-h-[520px] flex flex-col bg-[var(--color-panel)] border border-[var(--color-border-strong)] rounded shadow-2xl overflow-hidden">
          <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--color-border)] shrink-0">
            <span className="font-display text-sm">FootballIQ Assistant</span>
            <div className="flex items-center gap-1">
              {messages.length > 0 && (
                <button
                  onClick={clearConversation}
                  className="text-xs px-2 py-1 rounded text-[var(--color-text-muted)] hover:bg-[var(--color-panel-raised)]"
                >
                  Clear
                </button>
              )}
              <button
                onClick={() => setOpen(false)}
                aria-label="Close chat"
                className="text-xs px-2 py-1 rounded text-[var(--color-text-muted)] hover:bg-[var(--color-panel-raised)]"
              >
                ✕
              </button>
            </div>
          </div>

          <div ref={scrollRef} className="flex-1 overflow-y-auto p-3 space-y-2.5">
            {messages.length === 0 && (
              <p className="text-xs text-[var(--color-text-faint)]">
                Ask about players, stats, or football knowledge in general.
              </p>
            )}
            {messages.map((m, i) => (
              <ChatBubble key={i} role={m.role} content={m.content} sources={m.sources} />
            ))}
            {sending && <TypingIndicator />}
            {error && (
              <div className="border border-[var(--color-negative)]/30 bg-[var(--color-negative)]/10 rounded p-2 text-xs text-[var(--color-negative)]">
                {error}
              </div>
            )}
            {showSuggestions && (
              <SuggestionChips prompts={SUGGESTED_PROMPTS.slice(0, 3)} onPick={send} disabled={sending} />
            )}
          </div>

          <form onSubmit={handleSubmit} className="flex gap-2 p-3 border-t border-[var(--color-border)] shrink-0">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask something..."
              className="flex-1 bg-[var(--color-bg)] border border-[var(--color-border-strong)] rounded px-3 py-2 text-sm min-w-0"
            />
            <button
              type="submit"
              disabled={sending || !input.trim()}
              className="px-3 py-2 rounded bg-[var(--color-amber)] text-[var(--color-bg)] text-sm font-medium hover:opacity-90 disabled:opacity-50 shrink-0"
            >
              Send
            </button>
          </form>
        </div>
      )}

      <button
        onClick={() => setOpen((v) => !v)}
        aria-label={open ? "Close assistant" : "Open assistant"}
        className="fixed bottom-4 right-4 md:right-6 z-30 w-14 h-14 rounded-full bg-[var(--color-amber)] text-[var(--color-bg)] shadow-2xl flex items-center justify-center hover:opacity-90 transition-opacity"
      >
        {open ? (
          <svg width="22" height="22" viewBox="0 0 20 20" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M5 5l10 10M15 5L5 15" strokeLinecap="round" />
          </svg>
        ) : (
          <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.03 2 11c0 2.4 1.05 4.57 2.77 6.16L4 22l5.2-1.73c.9.23 1.84.36 2.8.36 5.52 0 10-4.03 10-9S17.52 2 12 2z" />
          </svg>
        )}
      </button>
    </>
  );
}
