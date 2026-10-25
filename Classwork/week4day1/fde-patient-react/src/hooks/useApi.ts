import { useCallback, useEffect, useState } from 'react';

async function sendRequest(url: string, options?: RequestInit): Promise<Response> {
    const response = await fetch(url, options);
    if (!response.ok) {
        const detail = await response.text();
        throw new Error(`HTTP ${response.status}: ${detail || response.statusText}`);
    }
    return response;
}

export default function useApi<T>(url: string) {
    const [data, setData] = useState<T | null>(null);
    const [error, setError] = useState<Error | null>(null);
    const [pendingRequests, setPendingRequests] = useState(0);

    const run = useCallback(async <TResult,>(
        operation: () => Promise<TResult>,
        signal?: AbortSignal,
    ): Promise<TResult> => {
        setPendingRequests(count => count + 1);
        setError(null);
        try {
            return await operation();
        } catch (cause) {
            const requestError = cause instanceof Error ? cause : new Error(String(cause));
            if (!signal?.aborted) {
                setError(requestError);
            }
            throw requestError;
        } finally {
            setPendingRequests(count => count - 1);
        }
    }, []);

    const fetchData = useCallback((signal?: AbortSignal) => run(async () => {
        const response = await sendRequest(url, { signal });
        const result: T = await response.json();
        if (!signal?.aborted) {
            setData(result);
        }
        return result;
    }, signal), [url, run]);

    const createData = useCallback(<TBody, TResult = unknown>(body: TBody) => run(async () => {
        const response = await sendRequest(url, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(body),
        });
        const result: TResult = await response.json();
        return result;
    }), [url, run]);

    const deleteData = useCallback((id: string | number) => run(async () => {
        await sendRequest(`${url.replace(/\/$/, '')}/${encodeURIComponent(id)}`, {
            method: 'DELETE',
        });
    }), [url, run]);

    useEffect(() => {
        const controller = new AbortController();
        // oxlint-disable-next-line react/set-state-in-effect -- Synchronize with the API and track request status.
        void fetchData(controller.signal).catch(cause => {
            if (!controller.signal.aborted) {
                console.error('Error fetching data:', cause);
            }
        });
        return () => controller.abort();
    }, [fetchData]);

    return { data, error, isLoading: pendingRequests > 0, fetchData, createData, deleteData };
}
