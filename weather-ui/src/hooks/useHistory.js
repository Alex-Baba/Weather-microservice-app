import { useState } from 'react'

export default function useHistory() {
  const [history, setHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [availableCities, setAvailableCities] = useState([])

  const loadHistory = async (setError) => {
    setHistoryLoading(true)
    try {
      const res = await fetch('/history')
      if (!res.ok) {
        const txt = await res.text()
        throw new Error(txt)
      }
      const ctype = res.headers.get('content-type') || ''
      if (!ctype.includes('application/json')) {
        const txt = await res.text()
        throw new Error('Unexpected response (not JSON): ' + (txt || ctype))
      }
      const data = await res.json()
      setHistory(data)

      const sorted = data
        .filter(d => d.fetched_at && typeof d.temperature === 'number')
        .slice()
        .sort((a, b) => new Date(a.fetched_at) - new Date(b.fetched_at))

      const cities = Array.from(new Set(sorted.map(d => d.city_name))).sort()
      setAvailableCities(cities)
    } catch (e) {
      if (setError) setError(e.message)
    } finally {
      setHistoryLoading(false)
    }
  }

  return { history, historyLoading, availableCities, loadHistory, setHistory }
}
