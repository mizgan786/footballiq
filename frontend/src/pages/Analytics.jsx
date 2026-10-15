import { useCallback } from "react";
import {
  BarChart, Bar, ScatterChart, Scatter, XAxis, YAxis, ZAxis, Tooltip, ResponsiveContainer,
  CartesianGrid, ReferenceLine,
} from "recharts";

import { useApi } from "../hooks/useApi";
import { getAnalyticsCharts, getModelMetrics } from "../services/api";
import { formatEur, formatPercent } from "../utils/format";
import StatCard from "../components/StatCard";
import { LoadingState, ErrorState } from "../components/StatusStates";

const gridProps = { strokeDasharray: "3 3", stroke: "var(--color-border)" };
const axisProps = { stroke: "var(--color-text-muted)", fontSize: 12 };
const tooltipStyle = {
  background: "var(--color-panel-raised)",
  border: "1px solid var(--color-border-strong)",
  borderRadius: 4,
  fontSize: 13,
};

function ChartCard({ title, note, children }) {
  return (
    <div className="border border-[var(--color-border)] rounded p-5 bg-[var(--color-panel)]">
      <h2 className="text-sm text-[var(--color-text-muted)] mb-1">{title}</h2>
      {note && <p className="text-xs text-[var(--color-text-faint)] mb-3">{note}</p>}
      {children}
    </div>
  );
}

export default function Analytics() {
  const { data: charts, loading: chartsLoading, error: chartsError, refetch: refetchCharts } = useApi(
    useCallback(() => getAnalyticsCharts(), []),
    []
  );
  const { data: metrics, loading: metricsLoading } = useApi(useCallback(() => getModelMetrics(), []), []);

  const maxValue =
    charts && charts.actual_vs_predicted.length > 0
      ? Math.max(...charts.actual_vs_predicted.flatMap((p) => [p.actual_eur, p.predicted_eur])) / 1_000_000
      : 0;

  return (
    <div className="px-6 md:px-10 py-10">
      <h1 className="font-display text-3xl mb-6">Analytics</h1>

      {/* Model Performance */}
      <h2 className="text-sm text-[var(--color-text-muted)] mb-3">Model performance (held-out test set)</h2>
      {metricsLoading && <LoadingState label="Loading model metrics..." />}
      {metrics && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-10">
          <StatCard label="MAE" value={formatEur(metrics.test.MAE_eur)} accent="amber" />
          <StatCard label="RMSE" value={formatEur(metrics.test.RMSE_eur)} />
          <StatCard label="R²" value={metrics.test.R2.toFixed(3)} accent="blue" />
          <StatCard label="MAPE" value={formatPercent(metrics.test.MAPE, 1)} />
        </div>
      )}

      {chartsLoading && <LoadingState label="Loading analytics..." />}
      {chartsError && <ErrorState message={chartsError.message} onRetry={refetchCharts} />}

      {charts && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <ChartCard title={`Market value distribution (${charts.market_value_distribution.reduce((s, b) => s + b.count, 0).toLocaleString()} player-seasons)`}>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={charts.market_value_distribution}>
                <CartesianGrid {...gridProps} vertical={false} />
                <XAxis dataKey="bucket" {...axisProps} />
                <YAxis {...axisProps} width={50} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="count" fill="var(--color-amber)" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Average market value by position">
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={charts.value_by_position}>
                <CartesianGrid {...gridProps} vertical={false} />
                <XAxis dataKey="position" {...axisProps} />
                <YAxis {...axisProps} width={50} tickFormatter={(v) => `€${(v / 1_000_000).toFixed(0)}M`} />
                <Tooltip contentStyle={tooltipStyle} formatter={(v) => formatEur(v)} />
                <Bar dataKey="avg_market_value_eur" fill="var(--color-blue)" radius={[3, 3, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Age vs market value" note={`${charts.age_vs_value.length} player-seasons sampled`}>
            <ResponsiveContainer width="100%" height={260}>
              <ScatterChart>
                <CartesianGrid {...gridProps} />
                <XAxis type="number" dataKey="age" name="Age" {...axisProps} />
                <YAxis
                  type="number"
                  dataKey="market_value_eur"
                  name="Market value"
                  {...axisProps}
                  width={50}
                  tickFormatter={(v) => `€${(v / 1_000_000).toFixed(0)}M`}
                />
                <ZAxis range={[20, 20]} />
                <Tooltip contentStyle={tooltipStyle} formatter={(v, n) => (n === "Market value" ? formatEur(v) : v)} />
                <Scatter data={charts.age_vs_value} fill="var(--color-amber)" fillOpacity={0.5} />
              </ScatterChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Goals vs market value" note={`${charts.goals_vs_value.length} player-seasons sampled`}>
            <ResponsiveContainer width="100%" height={260}>
              <ScatterChart>
                <CartesianGrid {...gridProps} />
                <XAxis type="number" dataKey="goals" name="Goals" {...axisProps} />
                <YAxis
                  type="number"
                  dataKey="market_value_eur"
                  name="Market value"
                  {...axisProps}
                  width={50}
                  tickFormatter={(v) => `€${(v / 1_000_000).toFixed(0)}M`}
                />
                <ZAxis range={[20, 20]} />
                <Tooltip contentStyle={tooltipStyle} formatter={(v, n) => (n === "Market value" ? formatEur(v) : v)} />
                <Scatter data={charts.goals_vs_value} fill="var(--color-blue)" fillOpacity={0.5} />
              </ScatterChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard
            title="Actual vs predicted (test set)"
            note="Points on the dashed line are perfect predictions; points below it are underestimated by the model."
          >
            <ResponsiveContainer width="100%" height={280}>
              <ScatterChart margin={{ top: 4, right: 8, left: 0, bottom: 4 }}>
                <CartesianGrid {...gridProps} />
                <XAxis
                  type="number"
                  dataKey="actual_eur"
                  name="Actual"
                  domain={[0, maxValue * 1_000_000]}
                  {...axisProps}
                  tickFormatter={(v) => `€${(v / 1_000_000).toFixed(0)}M`}
                />
                <YAxis
                  type="number"
                  dataKey="predicted_eur"
                  name="Predicted"
                  domain={[0, maxValue * 1_000_000]}
                  {...axisProps}
                  width={50}
                  tickFormatter={(v) => `€${(v / 1_000_000).toFixed(0)}M`}
                />
                <Tooltip contentStyle={tooltipStyle} formatter={(v) => formatEur(v)} />
                <ReferenceLine
                  segment={[
                    { x: 0, y: 0 },
                    { x: maxValue * 1_000_000, y: maxValue * 1_000_000 },
                  ]}
                  stroke="var(--color-text-faint)"
                  strokeDasharray="4 4"
                />
                <Scatter data={charts.actual_vs_predicted} fill="var(--color-positive)" fillOpacity={0.5} />
              </ScatterChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Top feature importances">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={[...charts.feature_importance].reverse()} layout="vertical" margin={{ left: 20 }}>
                <CartesianGrid {...gridProps} horizontal={false} />
                <XAxis type="number" {...axisProps} />
                <YAxis type="category" dataKey="feature" {...axisProps} width={110} />
                <Tooltip contentStyle={tooltipStyle} />
                <Bar dataKey="importance" fill="var(--color-amber)" radius={[0, 3, 3, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>
      )}
    </div>
  );
}
