export function LoadingState({ label = "Loading..." }) {
  return (
    <div className="flex items-center gap-3 text-[var(--color-text-muted)] py-12 justify-center">
      <span className="w-4 h-4 rounded-full border-2 border-[var(--color-border-strong)] border-t-[var(--color-amber)] animate-spin" />
      <span className="text-sm">{label}</span>
    </div>
  );
}

export function ErrorState({ message = "Something went wrong.", onRetry }) {
  return (
    <div className="border border-[var(--color-negative)]/30 bg-[var(--color-negative)]/10 rounded p-5 text-sm">
      <div className="text-[var(--color-negative)] font-medium mb-1">Couldn't load this</div>
      <div className="text-[var(--color-text-muted)]">{message}</div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="mt-3 text-xs px-3 py-1.5 rounded border border-[var(--color-border-strong)] hover:bg-[var(--color-panel-raised)]"
        >
          Try again
        </button>
      )}
    </div>
  );
}

export function EmptyState({ title = "Nothing here yet", hint }) {
  return (
    <div className="border border-dashed border-[var(--color-border-strong)] rounded p-8 text-center">
      <div className="text-[var(--color-text)] font-medium">{title}</div>
      {hint && <div className="text-sm text-[var(--color-text-muted)] mt-1">{hint}</div>}
    </div>
  );
}
