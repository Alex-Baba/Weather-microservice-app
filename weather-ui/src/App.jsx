import React, { useState, useEffect, useRef } from 'react'
import TempChart from './components/TempChart'
import CitySelector from './components/CitySelector'
import HistoryTable from './components/HistoryTable'

export default function App() {
  const [city, setCity] = useState('')
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)
  const [error, setError] = useState(null)
  const [modalMessage, setModalMessage] = useState(null)
  const [history, setHistory] = useState([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [chartData, setChartData] = useState(null)
  const modalTimerRef = useRef(null)
  const [selectedMetric, setSelectedMetric] = useState('temperature')
  const [availableCities, setAvailableCities] = useState([])
  const [selectedCities, setSelectedCities] = useState([])

  useEffect(() => {
    if (!history || history.length === 0 || selectedCities.length === 0) {
      setChartData(null)
      return
    }
    
    const datasets = selectedCities.map((city, idx) => {
      const cityRecords = history
        .filter(d => d.city_name === city && d.fetched_at)
        .filter(d => {
          if (selectedMetric === 'temperature') return typeof d.temperature === 'number'
          if (selectedMetric === 'humidity') return typeof d.humidity === 'number'
          if (selectedMetric === 'wind') return typeof d.wind_speed === 'number'
          return false
        })
        .slice()
        .sort((a, b) => new Date(a.fetched_at) - new Date(b.fetched_at))
      const valueAccessor = (d) => {
        if (selectedMetric === 'temperature') return d.temperature
        if (selectedMetric === 'humidity') return d.humidity
        if (selectedMetric === 'wind') return d.wind_speed
        return null
      }

      return {
        label: city,
        data: cityRecords.map(d => ({ x: new Date(d.fetched_at).toLocaleString(), y: valueAccessor(d) })),
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
  }, [history, selectedCities, selectedMetric])

  const metricLabel = selectedMetric === 'temperature' ? 'Temperature (°C)'
    : selectedMetric === 'humidity' ? 'Humidity (%)'
    : selectedMetric === 'wind' ? 'Wind Speed (m/s)'
    : 'Value'

  async function fetchWeather(e) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await fetch(`/weather?city=${encodeURIComponent(city)}`)
      if (!res.ok) {
        const txt = await res.text()
        const msg = txt || `HTTP ${res.status}`
        if (/city not found/i.test(msg)) setModalMessage('City not found')
        else setModalMessage(msg)
        return
      }
      const ctype = res.headers.get('content-type') || ''
      if (!ctype.includes('application/json')) {
        const txt = await res.text()
        setModalMessage('Unexpected response (not JSON): ' + (txt || ctype))
        return
      }
      const data = await res.json()
      // If server returned an error structure, show modal
      if (data && (data.error || data.detail)) {
        const m = (data.error || data.detail).toString()
        if (/city not found/i.test(m)) setModalMessage('City not found')
        else setModalMessage(m)
        return
      }
      setResult(data)
    } catch (err) {
      setError(err.message)
      const m = err.message || String(err)
      if (/city not found/i.test(m)) setModalMessage('City not found')
      else setModalMessage(m)
    } finally {
      setLoading(false)
    }
  }

  // Auto-close modal after 5 seconds
  useEffect(() => {
    if (modalTimerRef.current) {
      clearTimeout(modalTimerRef.current)
      modalTimerRef.current = null
    }
    if (modalMessage) {
      modalTimerRef.current = setTimeout(() => setModalMessage(null), 5000)
    }
    return () => {
      if (modalTimerRef.current) clearTimeout(modalTimerRef.current)
    }
  }, [modalMessage])

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

      {modalMessage && (
        <div style={{ position: 'fixed', left: 0, top: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }} onClick={() => setModalMessage(null)}>
          <div style={{ background: '#fff', padding: 20, borderRadius: 8, minWidth: 280 }} onClick={(e) => e.stopPropagation()}>
            <h4 style={{ marginTop: 0 }}>Notice</h4>
            <p>{modalMessage}</p>
            <div style={{ textAlign: 'right' }}>
              <button onClick={() => setModalMessage(null)}>Close</button>
            </div>
          </div>
        </div>
      )}

      {historyLoading && <p>Loading history...</p>}

      {history && history.length > 0 && (
        <div className="card">
          <h3>History</h3>
          {/* city selector moved below the chart */}
          <HistoryTable history={history} />

          {/* metric selector above the chart */}
          <div style={{ display: 'flex', gap: 8, alignItems: 'center', margin: '12px 0' }}>
            <div style={{ fontWeight: 600 }}>Metric:</div>
            <select value={selectedMetric} onChange={(e) => setSelectedMetric(e.target.value)}>
              <option value="temperature">Temperature</option>
              <option value="humidity">Humidity</option>
              <option value="wind">Wind Speed</option>
            </select>
          </div>

          <TempChart chartData={chartData} metricLabel={metricLabel} />
          <CitySelector availableCities={availableCities} selectedCities={selectedCities} setSelectedCities={setSelectedCities} />
        </div>
      )}
    </div>
  )
}
