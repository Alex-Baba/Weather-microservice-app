import React, { useState, useEffect } from 'react'
import TempChart from './components/TempChart'
import CitySelector from './components/CitySelector'
import HistoryTable from './components/HistoryTable'

export default function App() {
  const [city, setCity] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [chartData, setChartData] = useState(null)
  const [availableCities, setAvailableCities] = useState([])
  const [selectedCities, setSelectedCities] = useState([])

  useEffect(() => {
    if (!history || history.length === 0 || selectedCities.length === 0) {
      setChartData(null)
      return
    }
    
    const datasets = selectedCities.map((city, idx) => {
      const cityRecords = history
        .filter(d => d.city_name === city && d.fetched_at && typeof d.temperature === 'number')
        .slice()
        .sort((a, b) => new Date(a.fetched_at) - new Date(b.fetched_at))
      return {
        label: city,
        data: cityRecords.map(d => ({ x: new Date(d.fetched_at).toLocaleString(), y: d.temperature })),
        fill: false,
        borderColor: `hsl(${(idx * 60) % 360} 70% 40%)`,
        tension: 0.1,
      }
    })
    
    const allLabels = Array.from(new Set([
      ...datasets.flatMap(ds => ds.data.map(p => p.x))
    ])).sort((a, b) => new Date(a) - new Date(b))
    
    const finalDatasets = datasets.map(ds => ({
      ...ds,
      data: allLabels.map(label => {
        const found = ds.data.find(p => p.x === label)
        return found ? found.y : null
      })
    }))
    setChartData({ labels: allLabels, datasets: finalDatasets })
  }, [history, selectedCities])

  async function fetchWeather(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await fetch(`/weather?city=${encodeURIComponent(city)}`)
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
      setResult(data)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container">
      <h1>Weather</h1>
      <form onSubmit={fetchWeather}>
        <input value={city} onChange={(e) => setCity(e.target.value)} placeholder="City name" />
        <button type="submit" disabled={!city || loading}>Get</button>
      </form>

      <div style={{ marginTop: 12 }}>
        <button onClick={async () => {
          setHistoryLoading(true)
          try {
            const res = await fetch(`/history`)
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
            setError(e.message)
          } finally {
            setHistoryLoading(false)
          }
        }} disabled={historyLoading}>Show History</button>
      </div>

      {loading && <p>Loading...</p>}
      {error && <pre className="error">{error}</pre>}

      {result && (
        <div className="card">
          <h2>{result.city_name}</h2>
          <p>Temperature: {result.temperature} °C</p>
          <p>Humidity: {result.humidity}%</p>
          <p>Conditions: {result.description}</p>
          <p>Wind speed: {result.wind_speed} m/s</p>
          {result.fetched_at && (
            <p>Fetched at: {new Date(result.fetched_at).toLocaleString()}</p>
          )}
        </div>
      )}

      {historyLoading && <p>Loading history...</p>}

      {history && history.length > 0 && (
        <div className="card">
          <h3>History</h3>
          {/* city selector moved below the chart */}
          <HistoryTable history={history} />
          <TempChart chartData={chartData} />
          <CitySelector availableCities={availableCities} selectedCities={selectedCities} setSelectedCities={setSelectedCities} />
        </div>
      )}
    </div>
  )
}
