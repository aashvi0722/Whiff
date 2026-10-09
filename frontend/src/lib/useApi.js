import { useCallback, useEffect, useState } from 'react'

export function useApi(fetcher) {
  const [state, setState] = useState({ status: 'loading', data: null })
  const [n, setN] = useState(0)
  useEffect(() => {
    let alive = true
    setState(s => ({ status: s.data ? 'refreshing' : 'loading', data: s.data }))
    fetcher()
      .then(data => alive && setState({ status: 'ok', data }))
      .catch(() => alive && setState(s => ({ status: 'error', data: s.data })))
    return () => { alive = false }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [n])
  const reload = useCallback(() => setN(x => x + 1), [])
  return { ...state, reload }
}