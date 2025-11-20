import React from 'react'

export default function CitySelector({ availableCities, selectedCities, setSelectedCities }) {
  return (
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
  )
}
