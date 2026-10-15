import { useCallback } from "react";
import { Link } from "react-router-dom";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from "recharts";

import { useApi } from "../hooks/useApi";
import { getAnalyticsSummary, getTopPlayers } from "../services/api";
import { formatEur } from "../utils/format";
import StatCard from "../components/StatCard";
import { LoadingState, ErrorState } from "../components/StatusStates";

export default function Dashboard() {
  const summaryFetch = useCallback(() => getAnalyticsSummary(), []);
  const topFetch = useCallback(() => getTopPlayers(8), []);

  const { data: summary, loading: summaryLoading, error: summaryError, refetch: refetchSummary } =
    useApi(summaryFetch, []);
  const { data: topPlayers, loading: topLoading, error: topError, refetch: refetchTop } = useApi(topFetch, []);

  const chartData = (topPlayers || []).map((p) => ({
    name: p.name.split(" ").slice(-1)[0], // last name keeps bars readable
    value: p.market_value_in_eur / 1_000_000,
  }));

  return (
    <div>
      {/* Hero */}
      <section className="border-b border-[var(--color-border)] px-6 md:px-10 py-14 md:py-20">
        <div className="max-w-2xl">
          <h1 className="font-display text-4xl md:text-5xl leading-tight">FootballIQ</h1>
          <p className="text-[var(--color-text-muted)] mt-3 text-lg">
            AI-powered football player analytics and market valuation, trained on real
            performance data from Europe's top five leagues.
          </p>
          <div className="flex flex-wrap gap-3 mt-7">
            <Link
              to="/search"
              className="px-4 py-2 rounded bg-[var(--color-amber)] text-[var(--color-bg)] text-sm font-medium hover:opacity-90"
            >
              Search a player
            </Link>
            <Link
              to="/predict"
              className="px-4 py-2 rounded border border-[var(--color-border-strong)] text-sm hover:bg-[var(--color-panel-raised)]"
            >
              Predict a value
            </Link>
            <Link
              to="/analytics"
              className="px-4 py-2 rounded border border-[var(--color-border-strong)] text-sm hover:bg-[var(--color-panel-raised)]"
            >
              Explore analytics
            </Link>
            <Link
              to="/assistant"
              className="px-4 py-2 rounded border border-[var(--color-border-strong)] text-sm hover:bg-[var(--color-panel-raised)]"
            >
              Ask the assistant
            </Link>
          </div>
        </div>
      </section>

      <section className="px-6 md:px-10 py-8">
        {summaryLoading && <LoadingState label="Loading dashboard..." />}
        {summaryError && <ErrorState message={summaryError.message} onRetry={refetchSummary} />}

        {summary && (
          <>
            <div className="grid grid-cols-2 lg:grid-cols-5 gap-4">
              <StatCard label="Players analyzed" value={summary.players_analyzed.toLocaleString()} />
              <StatCard
                label="Avg. market value"
                value={formatEur(summary.average_market_value_eur)}
              />
              <StatCard
                label="Highest valued"
                value={summary.highest_valued_player.name}
                sublabel={formatEur(summary.highest_valued_player.market_value_in_eur)}
                accent="amber"
              />
              <StatCard label="Model R²" value={summary.model_r2.toFixed(2)} accent="blue" />
              <StatCard
                label="Seasons covered"
                value={summary.seasons_covered.length}
                sublabel={`${summary.seasons_covered[0]}\u2013${summary.seasons_covered.at(-1)}`}
              />
            </div>

            <div className="mt-8 border border-[var(--color-border)] rounded p-5 bg-[var(--color-panel)]">
              <h2 className="text-sm text-[var(--color-text-muted)] mb-4">
                Highest valued players, most recent season on record
              </h2>
              {topLoading && <LoadingState label="Loading chart..." />}
              {topError && <ErrorState message={topError.message} onRetry={refetchTop} />}
              {chartData.length > 0 && (
                <ResponsiveContainer width="100%" height={280}>
                  <BarChart data={chartData} margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" vertical={false} />
                    <XAxis dataKey="name" stroke="var(--color-text-muted)" fontSize={12} />
                    <YAxis
                      stroke="var(--color-text-muted)"
                      fontSize={12}
                      tickFormatter={(v) => `€${v}M`}
                      width={50}
                    />
                    <Tooltip
                      contentStyle={{
                        background: "var(--color-panel-raised)",
                        border: "1px solid var(--color-border-strong)",
                        borderRadius: 4,
                        fontSize: 13,
                      }}
                      formatter={(v) => [`€${v.toFixed(1)}M`, "Market value"]}
                    />
                    <Bar dataKey="value" fill="var(--color-amber)" radius={[3, 3, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              )}
            </div>
          </>
        )}
      </section>
    </div>
  );
}
