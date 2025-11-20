import React, { useState } from 'react'
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
                const labels = sorted.map(d => new Date(d.fetched_at).toLocaleString())
                const temps = sorted.map(d => d.temperature)
                setChartData({
                  labels,
                  datasets: [
                    {
                      label: 'Temperature (°C)',
                      data: temps,
                      fill: false,
                      borderColor: 'rgba(75,192,192,1)',
                      tension: 0.1,
                    }
                  ]
                })
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
        </div>
      )}
    </div>
  )
}
