import React, { useState, useEffect } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  TimeScale
)

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
    // for each selected city, create a dataset
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
    // build unified label set (all timestamps across selected cities)
    const allLabels = Array.from(new Set([
      ...datasets.flatMap(ds => ds.data.map(p => p.x))
    ])).sort((a, b) => new Date(a) - new Date(b))
    // align data to labels (Chart.js will handle missing points)
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
                // prepare chart data (temperature vs fetched_at)
                const sorted = data
                  .filter(d => d.fetched_at && typeof d.temperature === 'number')
                  .slice()
                  .sort((a, b) => new Date(a.fetched_at) - new Date(b.fetched_at))
                // set available cities
                const cities = Array.from(new Set(sorted.map(d => d.city_name))).sort()
                setAvailableCities(cities)
                // default to first city if none selected
                if (cities.length > 0 && selectedCities.length === 0) {
                  setSelectedCities([cities[0]])
                }
                // build chart for current selection (or first city)
                // chart will be built in useEffect when selectedCities is set
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
          <table style={{ width: '100%', borderCollapse: 'collapse' }}>
            <thead>
              <tr>
                <th style={{ textAlign: 'left' }}>City</th>
                <th>Temp</th>
                <th>Humidity</th>
                <th>When</th>
              </tr>
            </thead>
            <tbody>
              {history.map((h) => (
                <tr key={h.id}>
                  <td>{h.city_name}</td>
                  <td style={{ textAlign: 'center' }}>{h.temperature}</td>
                  <td style={{ textAlign: 'center' }}>{h.humidity}</td>
                  <td style={{ textAlign: 'center' }}>{h.fetched_at ? new Date(h.fetched_at).toLocaleString() : ''}</td>
                </tr>
              ))}
            </tbody>
          </table>
          {chartData && (
            <div style={{ marginTop: 16 }}>
              <h4>Temperature Trend</h4>
              <Line data={chartData} />
            </div>
          )}
          {/* nicer selector under the chart */}
          <div style={{ marginTop: 16 }}>
            <div style={{ fontSize: 18, marginBottom: 8, fontWeight: 600 }}>Select cities to plot</div>
            <div style={{ display: 'flex', gap: 12 }}>
              <div style={{ border: '1px solid #ddd', borderRadius: 8, padding: 12, maxHeight: 160, overflowY: 'auto', minWidth: 220 }}>
                {availableCities.map(c => (
                  <label key={c} style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6 }}>
                    <input type="checkbox" checked={selectedCities.includes(c)} onChange={(e) => {
                      if (e.target.checked) setSelectedCities(prev => [...prev, c])
                      else setSelectedCities(prev => prev.filter(x => x !== c))
                    }} />
                    <span style={{ fontSize: 15 }}>{c}</span>
                  </label>
                ))}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                <button type="button" onClick={() => setSelectedCities(Array.from(availableCities))}>Select all</button>
                <button type="button" onClick={() => setSelectedCities([])}>Clear</button>
              </div>
            </div>
            <div style={{ marginTop: 10, display: 'flex', gap: 8, flexWrap: 'wrap' }}>
              {selectedCities.map(c => (
                <button key={c} type="button" onClick={() => setSelectedCities(prev => prev.filter(x => x !== c))} style={{ padding: '6px 10px', borderRadius: 16, border: '1px solid #ccc', background: '#f0f7ff' }}>{c} ×</button>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
