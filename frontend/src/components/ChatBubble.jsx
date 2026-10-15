import ReactMarkdown from "react-markdown";

export function ChatBubble({ role, content, sources }) {
  const isUser = role === "user";
  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={`max-w-[85%] rounded px-4 py-2.5 text-sm ${
          isUser
            ? "bg-[var(--color-amber)] text-[var(--color-bg)]"
            : "bg-[var(--color-panel)] border border-[var(--color-border)]"
        }`}
      >
        {isUser ? (
          <span>{content}</span>
        ) : (
          <div className="prose-chat">
            <ReactMarkdown>{content}</ReactMarkdown>
          </div>
        )}
        {sources && sources.length > 0 && (
          <div className="mt-2 pt-2 border-t border-[var(--color-border)] text-xs text-[var(--color-text-faint)]">
            From the knowledge base: {sources.map((s) => s.title).join(", ")}
          </div>
        )}
      </div>
    </div>
  );
}

export function TypingIndicator() {
  return (
    <div className="flex justify-start">
      <div className="bg-[var(--color-panel)] border border-[var(--color-border)] rounded px-4 py-3 flex gap-1">
        {[0, 1, 2].map((i) => (
          <span
            key={i}
            className="w-1.5 h-1.5 rounded-full bg-[var(--color-text-faint)] animate-bounce"
            style={{ animationDelay: `${i * 0.15}s` }}
          />
        ))}
      </div>
    </div>
  );
}

export function SuggestionChips({ prompts, onPick, disabled }) {
  return (
    <div className="flex flex-wrap gap-2">
      {prompts.map((p) => (
        <button
          key={p}
          type="button"
          disabled={disabled}
          onClick={() => onPick(p)}
          className="text-xs px-3 py-1.5 rounded-full border border-[var(--color-border-strong)] text-[var(--color-text-muted)] hover:text-[var(--color-text)] hover:bg-[var(--color-panel-raised)] disabled:opacity-50"
        >
          {p}
        </button>
      ))}
    </div>
  );
}
