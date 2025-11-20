import React, { useState } from 'react'

export default function HistoryTable({ history }) {
  const [modalMessage, setModalMessage] = useState(null)

  const showError = (msg) => {
    setModalMessage(msg)
  }

  const hideModal = () => setModalMessage(null)

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
          {history.map((h, idx) => {
            // Detect error objects returned by the server (FastAPI /error handlers)
            const isError = h && (h.detail || h.error)
            const key = h && h.id ? h.id : `row-${idx}`
            return (
              <tr key={key}>
                <td>{isError ? (
                  <button type="button" onClick={() => showError(h.detail || h.error)} style={{ color: '#b00', background: 'transparent', border: 'none', cursor: 'pointer' }}>
                    Error
                  </button>
                ) : (
                  h.city_name
                )}</td>
                <td style={{ textAlign: 'center' }}>{isError ? '-' : h.temperature}</td>
                <td style={{ textAlign: 'center' }}>{isError ? '-' : h.humidity}</td>
                <td style={{ textAlign: 'center' }}>{isError ? '' : (h.fetched_at ? new Date(h.fetched_at).toLocaleString() : '')}</td>
              </tr>
            )
          })}
        </tbody>
      </table>

      {modalMessage && (
        <div style={{ position: 'fixed', left: 0, top: 0, right: 0, bottom: 0, background: 'rgba(0,0,0,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 9999 }} onClick={hideModal}>
          <div style={{ background: '#fff', padding: 20, borderRadius: 8, minWidth: 280 }} onClick={(e) => e.stopPropagation()}>
            <h4 style={{ marginTop: 0 }}>Error</h4>
            <p>{modalMessage}</p>
            <div style={{ textAlign: 'right' }}>
              <button onClick={hideModal}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
