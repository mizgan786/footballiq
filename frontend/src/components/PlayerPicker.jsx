import { useEffect, useRef, useState } from "react";
import { listPlayers } from "../services/api";

export default function PlayerPicker({ label, onSelect, selectedName }) {
  const [query, setQuery] = useState("");
  const [suggestions, setSuggestions] = useState([]);
  const [open, setOpen] = useState(false);
  const boxRef = useRef(null);

  useEffect(() => {
    if (!query.trim()) return;
    const t = setTimeout(() => {
      listPlayers({ name: query.trim(), limit: 6 }).then(setSuggestions).catch(() => setSuggestions([]));
    }, 300);
    return () => clearTimeout(t);
  }, [query]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (boxRef.current && !boxRef.current.contains(e.target)) setOpen(false);
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  return (
    <div ref={boxRef} className="relative">
      <span className="text-xs text-[var(--color-text-muted)]">{label}</span>
      <input
        type="text"
        value={open ? query : selectedName || query}
        onChange={(e) => {
          const value = e.target.value;
          setQuery(value);
          setOpen(true);
          if (!value.trim()) setSuggestions([]);
        }}
        onFocus={() => setOpen(true)}
        placeholder="Search a player..."
        className="mt-1 w-full bg-[var(--color-panel)] border border-[var(--color-border-strong)] rounded px-3 py-2 text-sm"
      />
      {open && suggestions.length > 0 && (
        <div className="absolute z-10 mt-1 w-full bg-[var(--color-panel-raised)] border border-[var(--color-border-strong)] rounded overflow-hidden">
          {suggestions.map((p) => (
            <button
              key={p.id}
              type="button"
              onClick={() => {
                onSelect(p);
                setQuery("");
                setOpen(false);
              }}
              className="w-full text-left px-3 py-2 text-sm hover:bg-[var(--color-panel)] flex justify-between gap-2"
            >
              <span className="truncate">{p.name}</span>
              <span className="text-[var(--color-text-faint)] text-xs shrink-0">{p.club_name}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
