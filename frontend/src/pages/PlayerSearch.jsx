import { useCallback, useEffect, useState } from "react";

import { useApi } from "../hooks/useApi";
import { listPlayers, getClubs } from "../services/api";
import PlayerCard from "../components/PlayerCard";
import { LoadingState, ErrorState, EmptyState } from "../components/StatusStates";

const POSITIONS = ["Attack", "Midfield", "Defender", "Goalkeeper"];
const SORT_OPTIONS = [
  { value: "market_value_in_eur", label: "Market value" },
  { value: "age", label: "Age" },
  { value: "goals", label: "Goals" },
  { value: "assists", label: "Assists" },
  { value: "appearances", label: "Appearances" },
];

function useDebouncedValue(value, delayMs) {
  const [debounced, setDebounced] = useState(value);
  useEffect(() => {
    const t = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(t);
  }, [value, delayMs]);
  return debounced;
}

export default function PlayerSearch() {
  const [nameInput, setNameInput] = useState("");
  const debouncedName = useDebouncedValue(nameInput, 350);

  const [position, setPosition] = useState("");
  const [clubId, setClubId] = useState("");
  const [minAge, setMinAge] = useState("");
  const [maxAge, setMaxAge] = useState("");
  const [sortBy, setSortBy] = useState("market_value_in_eur");
  const [order, setOrder] = useState("desc");

  const { data: clubs } = useApi(useCallback(() => getClubs(), []), []);

  const fetchPlayers = useCallback(() => {
    const params = {
      sort_by: sortBy,
      order,
      limit: 60,
    };
    if (debouncedName.trim()) params.name = debouncedName.trim();
    if (position) params.position = position;
    if (clubId) params.club_id = clubId;
    if (minAge) params.min_age = minAge;
    if (maxAge) params.max_age = maxAge;
    return listPlayers(params);
  }, [debouncedName, position, clubId, minAge, maxAge, sortBy, order]);

  const { data: players, loading, error, refetch } = useApi(fetchPlayers, [fetchPlayers]);

  return (
    <div className="px-6 md:px-10 py-10">
      <h1 className="font-display text-3xl mb-6">Player Search</h1>

      <div className="grid grid-cols-2 md:grid-cols-6 gap-3 mb-8">
        <input
          type="text"
          placeholder="Search by name..."
          value={nameInput}
          onChange={(e) => setNameInput(e.target.value)}
          className="col-span-2 md:col-span-2 bg-[var(--color-panel)] border border-[var(--color-border-strong)] rounded px-3 py-2 text-sm placeholder:text-[var(--color-text-faint)]"
        />
        <select
          value={position}
          onChange={(e) => setPosition(e.target.value)}
          className="bg-[var(--color-panel)] border border-[var(--color-border-strong)] rounded px-3 py-2 text-sm"
        >
          <option value="">All positions</option>
          {POSITIONS.map((p) => (
            <option key={p} value={p}>
              {p}
            </option>
          ))}
        </select>
        <select
          value={clubId}
          onChange={(e) => setClubId(e.target.value)}
          className="bg-[var(--color-panel)] border border-[var(--color-border-strong)] rounded px-3 py-2 text-sm"
        >
          <option value="">All clubs</option>
          {(clubs || []).map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
        <div className="flex gap-1">
          <input
            type="number"
            placeholder="Min age"
            value={minAge}
            onChange={(e) => setMinAge(e.target.value)}
            className="w-full bg-[var(--color-panel)] border border-[var(--color-border-strong)] rounded px-2 py-2 text-sm"
          />
          <input
            type="number"
            placeholder="Max age"
            value={maxAge}
            onChange={(e) => setMaxAge(e.target.value)}
            className="w-full bg-[var(--color-panel)] border border-[var(--color-border-strong)] rounded px-2 py-2 text-sm"
          />
        </div>
        <div className="flex gap-1">
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="w-full bg-[var(--color-panel)] border border-[var(--color-border-strong)] rounded px-2 py-2 text-sm"
          >
            {SORT_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>
                {o.label}
              </option>
            ))}
          </select>
          <button
            onClick={() => setOrder(order === "desc" ? "asc" : "desc")}
            title={order === "desc" ? "Descending" : "Ascending"}
            className="shrink-0 px-3 border border-[var(--color-border-strong)] rounded text-sm hover:bg-[var(--color-panel-raised)]"
          >
            {order === "desc" ? "\u2193" : "\u2191"}
          </button>
        </div>
      </div>

      {loading && <LoadingState label="Searching players..." />}
      {error && <ErrorState message={error.message} onRetry={refetch} />}
      {!loading && !error && players && players.length === 0 && (
        <EmptyState title="No players match these filters" hint="Try widening the age range or clearing a filter." />
      )}
      {!loading && !error && players && players.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {players.map((p) => (
            <PlayerCard key={p.id} player={p} />
          ))}
        </div>
      )}
    </div>
  );
}
