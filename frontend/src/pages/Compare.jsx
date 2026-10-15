import { useCallback, useMemo, useState } from "react";
import {
  RadarChart, Radar, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Legend, Tooltip,
} from "recharts";

import { useApi } from "../hooks/useApi";
import { comparePlayers } from "../services/api";
import { formatEur, formatPercent } from "../utils/format";
import { buildRadarData } from "../utils/radar";
import PlayerPicker from "../components/PlayerPicker";
import { LoadingState, ErrorState, EmptyState } from "../components/StatusStates";

function Row({ label, a, b, formatter = (v) => v }) {
  return (
    <div className="grid grid-cols-3 py-2 border-b border-[var(--color-border)] text-sm">
      <div className="text-right pr-4">{formatter(a)}</div>
      <div className="text-center text-[var(--color-text-muted)] text-xs self-center">{label}</div>
      <div className="pl-4">{formatter(b)}</div>
    </div>
  );
}

export default function Compare() {
  const [playerA, setPlayerA] = useState(null);
  const [playerB, setPlayerB] = useState(null);

  const fetcher = useCallback(() => {
    if (!playerA || !playerB) return Promise.resolve(null);
    return comparePlayers(playerA.id, playerB.id);
  }, [playerA, playerB]);

  const { data, loading, error, refetch } = useApi(fetcher, [playerA, playerB]);

  const radarData = useMemo(() => (data ? buildRadarData(data.player_a, data.player_b) : []), [data]);

  return (
    <div className="px-6 md:px-10 py-10 max-w-4xl">
      <h1 className="font-display text-3xl mb-6">Player Comparison</h1>

      <div className="grid grid-cols-2 gap-4 mb-8">
        <PlayerPicker label="Player A" onSelect={setPlayerA} selectedName={playerA?.name} />
        <PlayerPicker label="Player B" onSelect={setPlayerB} selectedName={playerB?.name} />
      </div>

      {(!playerA || !playerB) && (
        <EmptyState title="Pick two players to compare" hint="Search and select a player in each box above." />
      )}

      {playerA && playerB && loading && <LoadingState label="Comparing..." />}
      {playerA && playerB && error && <ErrorState message={error.message} onRetry={refetch} />}

      {data && !loading && !error && (
        <>
          {/* Player Information */}
          <div className="grid grid-cols-3 items-center mb-2">
            <div className="text-right pr-4 font-display text-xl truncate">{data.player_a.name}</div>
            <div className="text-center text-xs text-[var(--color-text-faint)]">vs</div>
            <div className="pl-4 font-display text-xl truncate">{data.player_b.name}</div>
          </div>
          <div className="border border-[var(--color-border)] rounded bg-[var(--color-panel)] px-4">
            <Row label="Position" a={data.player_a.sub_position} b={data.player_b.sub_position} />
            <Row
              label="Club / League"
              a={`${data.player_a.latest_season.club_name || "—"}`}
              b={`${data.player_b.latest_season.club_name || "—"}`}
            />
            <Row
              label="Age"
              a={data.player_a.latest_season.age}
              b={data.player_b.latest_season.age}
              formatter={(v) => v?.toFixed(1)}
            />

            {/* Performance */}
            <Row label="Appearances" a={data.player_a.latest_season.appearances} b={data.player_b.latest_season.appearances} />
            <Row label="Minutes" a={data.player_a.latest_season.minutes_played} b={data.player_b.latest_season.minutes_played} formatter={(v) => v?.toLocaleString()} />
            <Row label="Goals" a={data.player_a.latest_season.goals} b={data.player_b.latest_season.goals} />
            <Row label="Assists" a={data.player_a.latest_season.assists} b={data.player_b.latest_season.assists} />
            <Row
              label="Goals / 90"
              a={data.player_a.latest_season.goals_per_90}
              b={data.player_b.latest_season.goals_per_90}
              formatter={(v) => v?.toFixed(2)}
            />

            {/* Market Value */}
            <Row
              label="Actual market value"
              a={data.player_a.latest_season.market_value_in_eur}
              b={data.player_b.latest_season.market_value_in_eur}
              formatter={formatEur}
            />
            <Row
              label="Model prediction"
              a={data.player_a.predicted_value_eur}
              b={data.player_b.predicted_value_eur}
              formatter={formatEur}
            />
            <Row
              label="Difference"
              a={data.player_a.difference_pct}
              b={data.player_b.difference_pct}
              formatter={(v) => `${v >= 0 ? "+" : ""}${formatPercent(v, 1)}`}
            />
          </div>
          <p className="text-xs text-[var(--color-text-faint)] mt-2">
            Model predictions are statistical estimates, not official valuations.
          </p>

          {/* Radar */}
          <div className="mt-8 border border-[var(--color-border)] rounded p-5 bg-[var(--color-panel)]">
            <h2 className="text-sm text-[var(--color-text-muted)] mb-1">Profile comparison</h2>
            <p className="text-xs text-[var(--color-text-faint)] mb-4">
              Normalized 0-100 against typical season ceilings in the dataset (goals, assists, playing time, and
              value - this dataset doesn't include passing or defensive-action data).
            </p>
            <ResponsiveContainer width="100%" height={320}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="var(--color-border)" />
                <PolarAngleAxis dataKey="metric" tick={{ fill: "var(--color-text-muted)", fontSize: 12 }} />
                <PolarRadiusAxis tick={{ fill: "var(--color-text-faint)", fontSize: 10 }} domain={[0, 100]} />
                <Radar name={data.player_a.name} dataKey="a" stroke="var(--color-amber)" fill="var(--color-amber)" fillOpacity={0.25} />
                <Radar name={data.player_b.name} dataKey="b" stroke="var(--color-blue)" fill="var(--color-blue)" fillOpacity={0.25} />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                <Tooltip
                  contentStyle={{
                    background: "var(--color-panel-raised)",
                    border: "1px solid var(--color-border-strong)",
                    borderRadius: 4,
                    fontSize: 13,
                  }}
                />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}
