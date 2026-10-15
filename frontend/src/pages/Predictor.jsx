import { useCallback, useState } from "react";

import { useApi } from "../hooks/useApi";
import { predictValue, getClubs, getModelMetrics } from "../services/api";
import { formatEur, formatEurFull, LEAGUE_NAMES } from "../utils/format";
import { LoadingState, ErrorState } from "../components/StatusStates";

const SUB_POSITIONS = [
  "Goalkeeper", "Centre-Back", "Left-Back", "Right-Back",
  "Defensive Midfield", "Central Midfield", "Attacking Midfield", "Left Midfield", "Right Midfield",
  "Left Winger", "Right Winger", "Second Striker", "Centre-Forward",
];

const DEFAULT_FORM = {
  age: 24,
  sub_position: "Centre-Forward",
  foot: "right",
  league: "GB1",
  appearances: 30,
  minutes_played: 2400,
  goals: 10,
  assists: 5,
  yellow_cards: 3,
  red_cards: 0,
  height_in_cm: "",
  club_id: "",
};

function Field({ label, children }) {
  return (
    <label className="block">
      <span className="text-xs text-[var(--color-text-muted)]">{label}</span>
      <div className="mt-1">{children}</div>
    </label>
  );
}

const inputClass =
  "w-full bg-[var(--color-panel)] border border-[var(--color-border-strong)] rounded px-3 py-2 text-sm";

export default function Predictor() {
  const [form, setForm] = useState(DEFAULT_FORM);
  const [result, setResult] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState(null);

  const { data: clubs } = useApi(useCallback(() => getClubs(), []), []);
  const { data: metrics } = useApi(useCallback(() => getModelMetrics(), []), []);

  const update = (field) => (e) => {
    const value = e.target.value;
    setForm((f) => ({ ...f, [field]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setSubmitError(null);
    setResult(null);
    try {
      const payload = {
        age: Number(form.age),
        sub_position: form.sub_position,
        foot: form.foot,
        league: form.league,
        appearances: Number(form.appearances),
        minutes_played: Number(form.minutes_played),
        goals: Number(form.goals),
        assists: Number(form.assists),
        yellow_cards: Number(form.yellow_cards),
        red_cards: Number(form.red_cards),
      };
      if (form.height_in_cm) payload.height_in_cm = Number(form.height_in_cm);
      if (form.club_id) payload.club_id = Number(form.club_id);

      const data = await predictValue(payload);
      setResult(data);
    } catch (err) {
      setSubmitError(err);
    } finally {
      setSubmitting(false);
    }
  };

  const goalsPer90 =
    form.minutes_played > 0 ? ((form.goals / form.minutes_played) * 90).toFixed(2) : "0.00";
  const assistsPer90 =
    form.minutes_played > 0 ? ((form.assists / form.minutes_played) * 90).toFixed(2) : "0.00";

  const testMae = metrics?.test?.MAE_eur;

  return (
    <div className="px-6 md:px-10 py-10 max-w-4xl">
      <h1 className="font-display text-3xl mb-2">Value Predictor</h1>
      <p className="text-[var(--color-text-muted)] mb-8 max-w-xl">
        Enter a hypothetical season profile and the model will estimate a market value from it — useful for
        exploring "what would a player with these numbers be worth?"
      </p>

      <form onSubmit={handleSubmit} className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Field label="Age">
          <input type="number" min={14} max={45} step={0.1} value={form.age} onChange={update("age")} className={inputClass} required />
        </Field>
        <Field label="Position">
          <select value={form.sub_position} onChange={update("sub_position")} className={inputClass}>
            {SUB_POSITIONS.map((p) => (
              <option key={p} value={p}>{p}</option>
            ))}
          </select>
        </Field>
        <Field label="Preferred foot">
          <select value={form.foot} onChange={update("foot")} className={inputClass}>
            <option value="right">Right</option>
            <option value="left">Left</option>
            <option value="both">Both</option>
          </select>
        </Field>
        <Field label="League">
          <select value={form.league} onChange={update("league")} className={inputClass}>
            {Object.entries(LEAGUE_NAMES).map(([code, name]) => (
              <option key={code} value={code}>{name}</option>
            ))}
          </select>
        </Field>

        <Field label="Appearances (season)">
          <input type="number" min={0} max={70} value={form.appearances} onChange={update("appearances")} className={inputClass} required />
        </Field>
        <Field label="Minutes played">
          <input type="number" min={0} max={6300} value={form.minutes_played} onChange={update("minutes_played")} className={inputClass} required />
        </Field>
        <Field label="Goals">
          <input type="number" min={0} value={form.goals} onChange={update("goals")} className={inputClass} required />
        </Field>
        <Field label="Assists">
          <input type="number" min={0} value={form.assists} onChange={update("assists")} className={inputClass} required />
        </Field>

        <Field label="Yellow cards">
          <input type="number" min={0} value={form.yellow_cards} onChange={update("yellow_cards")} className={inputClass} />
        </Field>
        <Field label="Red cards">
          <input type="number" min={0} value={form.red_cards} onChange={update("red_cards")} className={inputClass} />
        </Field>
        <Field label="Height (cm, optional)">
          <input type="number" min={150} max={210} value={form.height_in_cm} onChange={update("height_in_cm")} className={inputClass} placeholder="auto by position" />
        </Field>
        <Field label="Club (optional)">
          <select value={form.club_id} onChange={update("club_id")} className={inputClass}>
            <option value="">League average</option>
            {(clubs || []).map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </Field>

        <div className="col-span-2 md:col-span-4 text-xs text-[var(--color-text-faint)] -mt-2">
          Goals/90: {goalsPer90} &middot; Assists/90: {assistsPer90} (computed automatically from minutes)
        </div>

        <div className="col-span-2 md:col-span-4">
          <button
            type="submit"
            disabled={submitting}
            className="px-5 py-2.5 rounded bg-[var(--color-amber)] text-[var(--color-bg)] text-sm font-medium hover:opacity-90 disabled:opacity-50"
          >
            {submitting ? "Predicting..." : "Predict Market Value"}
          </button>
        </div>
      </form>

      {submitting && <div className="mt-8"><LoadingState label="Running the model..." /></div>}
      {submitError && (
        <div className="mt-8">
          <ErrorState message={submitError.response?.data?.detail?.[0]?.msg || submitError.message} />
        </div>
      )}

      {result && !submitting && (
        <div className="mt-8 border border-[var(--color-border)] rounded p-6 bg-[var(--color-panel)]">
          <div className="text-sm text-[var(--color-text-muted)]">Estimated Market Value</div>
          <div className="font-display text-5xl text-[var(--color-amber)] mt-1">
            {formatEur(result.predicted_value_eur)}
          </div>
          <div className="text-xs text-[var(--color-text-faint)] mt-1">{formatEurFull(result.predicted_value_eur)}</div>

          {testMae != null && (
            <div className="text-sm text-[var(--color-text-muted)] mt-4">
              Typical prediction error on held-out data: ±{formatEur(testMae)} (MAE)
            </div>
          )}

          <div className="text-sm text-[var(--color-text-muted)] mt-3">
            Model used: <span className="text-[var(--color-text)]">{result.model_used}</span>
          </div>
          <div className="text-sm text-[var(--color-text-muted)] mt-1">
            Most influential factors:{" "}
            <span className="text-[var(--color-text)]">{result.important_factors.join(", ")}</span>
          </div>

          <p className="text-xs text-[var(--color-text-faint)] mt-4 max-w-xl">{result.disclaimer}</p>
        </div>
      )}
    </div>
  );
}
