import React from 'react'

export default function HistoryTable({ history }) {
  return (
    <div>
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
    </div>
  )
}
