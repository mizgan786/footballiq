import { useCallback, useMemo } from "react";
import { useParams, Link } from "react-router-dom";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend,
} from "recharts";

import { useApi } from "../hooks/useApi";
import { getPlayer, predictValue } from "../services/api";
import { formatEur, formatPercent, LEAGUE_NAMES, POSITION_NAMES } from "../utils/format";
import { LoadingState, ErrorState, EmptyState } from "../components/StatusStates";
import StatCard from "../components/StatCard";

export default function PlayerProfile() {
  const { id } = useParams();

  const playerFetch = useCallback(() => getPlayer(id), [id]);
  const { data: player, loading: playerLoading, error: playerError, refetch: refetchPlayer } = useApi(
    playerFetch,
    [id]
  );

  const latestSeason = player?.seasons?.at(-1) ?? null;

  const predictFetch = useCallback(() => {
    if (!player || !latestSeason) return Promise.resolve(null);
    return predictValue({
      age: latestSeason.age,
      sub_position: player.sub_position,
      foot: player.foot,
      league: latestSeason.league,
      appearances: latestSeason.appearances,
      minutes_played: latestSeason.minutes_played,
      goals: latestSeason.goals,
      assists: latestSeason.assists,
      yellow_cards: latestSeason.yellow_cards,
      red_cards: latestSeason.red_cards,
      height_in_cm: player.height_in_cm,
      club_id: latestSeason.club_id,
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [player, latestSeason]);
  const { data: prediction, loading: predictLoading } = useApi(predictFetch, [player]);

  const valueHistory = useMemo(
    () =>
      (player?.seasons || []).map((s) => ({
        season: s.season,
        value: s.market_value_in_eur / 1_000_000,
      })),
    [player]
  );

  const productionHistory = useMemo(
    () =>
      (player?.seasons || []).map((s) => ({
        season: s.season,
        goals: s.goals,
        assists: s.assists,
      })),
    [player]
  );

  const diffInfo = useMemo(() => {
    if (!prediction || !latestSeason) return null;
    const diff = prediction.predicted_value_eur - latestSeason.market_value_in_eur;
    const pct = latestSeason.market_value_in_eur ? diff / latestSeason.market_value_in_eur : 0;
    return { diff, pct, direction: diff >= 0 ? "above" : "below" };
  }, [prediction, latestSeason]);

  if (playerLoading) return <LoadingState label="Loading player..." />;
  if (playerError) return <div className="px-6 md:px-10 py-10"><ErrorState message={playerError.message} onRetry={refetchPlayer} /></div>;
  if (!player) return null;
  if (!latestSeason) {
    return (
      <div className="px-6 md:px-10 py-10">
        <EmptyState title={`No top-5-league season data for ${player.name}`} />
      </div>
    );
  }

  return (
    <div className="px-6 md:px-10 py-10 max-w-5xl">
      <Link to="/search" className="text-xs text-[var(--color-text-muted)] hover:text-[var(--color-text)]">
        &larr; Back to search
      </Link>

      {/* Header */}
      <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1 mt-3">
        <h1 className="font-display text-4xl">{player.name}</h1>
        <span className="text-[var(--color-text-muted)]">
          {player.sub_position || POSITION_NAMES[player.position] || player.position}
        </span>
      </div>
      <div className="text-sm text-[var(--color-text-muted)] mt-1">
        {latestSeason.club_name || "Unknown club"} &middot; {LEAGUE_NAMES[latestSeason.league] || latestSeason.league}{" "}
        &middot; Age {latestSeason.age?.toFixed(1)} &middot; {player.foot}-footed
        {player.height_in_cm ? ` \u00b7 ${Math.round(player.height_in_cm)}cm` : ""}
      </div>

      {/* Market Value */}
      <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-8">
        <StatCard label="Actual market value" value={formatEur(latestSeason.market_value_in_eur)} accent="blue" />
        <StatCard
          label="Model prediction"
          value={predictLoading ? "..." : prediction ? formatEur(prediction.predicted_value_eur) : "—"}
          accent="amber"
        />
        <StatCard
          label="Difference"
          value={diffInfo ? `${diffInfo.direction === "above" ? "+" : ""}${formatPercent(diffInfo.pct, 1)}` : "—"}
          sublabel={diffInfo ? `Model estimate ${diffInfo.direction} market value` : undefined}
        />
      </div>
      <p className="text-xs text-[var(--color-text-faint)] mt-3 max-w-xl">
        This is a statistical estimate produced by a trained model, not an official or objectively correct player
        valuation.
      </p>

      {/* Performance */}
      <h2 className="font-display text-xl mt-10 mb-4">Performance, {latestSeason.season}</h2>
      <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
        <StatCard label="Appearances" value={latestSeason.appearances} />
        <StatCard label="Minutes" value={latestSeason.minutes_played?.toLocaleString()} />
        <StatCard label="Goals" value={latestSeason.goals} />
        <StatCard label="Assists" value={latestSeason.assists} />
        <StatCard label="Goals / 90" value={latestSeason.goals_per_90?.toFixed(2)} />
        <StatCard label="Assists / 90" value={latestSeason.assists_per_90?.toFixed(2)} />
      </div>

      {/* Charts */}
      {valueHistory.length > 1 && (
        <div className="mt-10 border border-[var(--color-border)] rounded p-5 bg-[var(--color-panel)]">
          <h2 className="text-sm text-[var(--color-text-muted)] mb-4">Market value over time</h2>
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={valueHistory} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="season" stroke="var(--color-text-muted)" fontSize={12} />
              <YAxis stroke="var(--color-text-muted)" fontSize={12} tickFormatter={(v) => `€${v}M`} width={50} />
              <Tooltip
                contentStyle={{
                  background: "var(--color-panel-raised)",
                  border: "1px solid var(--color-border-strong)",
                  borderRadius: 4,
                  fontSize: 13,
                }}
                formatter={(v) => [`€${v.toFixed(1)}M`, "Market value"]}
              />
              <Line type="monotone" dataKey="value" stroke="var(--color-amber)" strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {productionHistory.length > 1 && (
        <div className="mt-6 border border-[var(--color-border)] rounded p-5 bg-[var(--color-panel)]">
          <h2 className="text-sm text-[var(--color-text-muted)] mb-4">Goals &amp; assists by season</h2>
          <ResponsiveContainer width="100%" height={240}>
            <BarChart data={productionHistory} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
              <XAxis dataKey="season" stroke="var(--color-text-muted)" fontSize={12} />
              <YAxis stroke="var(--color-text-muted)" fontSize={12} width={30} />
              <Tooltip
                contentStyle={{
                  background: "var(--color-panel-raised)",
                  border: "1px solid var(--color-border-strong)",
                  borderRadius: 4,
                  fontSize: 13,
                }}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Bar dataKey="goals" fill="var(--color-blue)" radius={[3, 3, 0, 0]} />
              <Bar dataKey="assists" fill="var(--color-positive)" radius={[3, 3, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}
    </div>
  );
}
