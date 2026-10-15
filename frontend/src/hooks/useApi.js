import { useEffect, useState, useCallback } from "react";

/**
 * useApi(fetcherFn, deps) - runs fetcherFn() on mount / whenever deps change,
 * tracks data/loading/error. fetcherFn must be a stable callback (wrap with
 * useCallback at the call site if it closes over changing values).
 */
export function useApi(fetcherFn, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refetch = useCallback(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetcherFn()
      .then((result) => {
        if (!cancelled) setData(result);
      })
      .catch((err) => {
        if (!cancelled) setError(err);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => refetch(), [refetch]);

  return { data, loading, error, refetch };
}
