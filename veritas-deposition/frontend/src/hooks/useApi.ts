import { useState, useEffect } from 'react'
import { api } from '../api/client'

export function useApi<T>(fetcher: () => Promise<T>, deps: any[] = []) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    setLoading(true)
    setError(null)
    fetcher()
      .then(d => { if (!cancelled) setData(d) })
      .catch(e => { if (!cancelled) setError(e.message) })
      .finally(() => { if (!cancelled) setLoading(false) })
    return () => { cancelled = true }
  }, deps)

  return { data, loading, error }
}

export function useMatters() {
  return useApi(() => api.getMatters(), [])
}

export function useMatter(id: string) {
  return useApi(() => api.getMatter(id), [id])
}

export function useDepositions(matterId: string) {
  return useApi(() => api.getDepositions(matterId), [matterId])
}

export function useContradictions(matterId?: string) {
  return useApi(() => api.getContradictions(matterId), [matterId])
}

export function useWitnesses(matterId: string) {
  return useApi(() => api.getWitnesses(matterId), [matterId])
}

export function useEvidence(matterId: string) {
  return useApi(() => api.getEvidence(matterId), [matterId])
}