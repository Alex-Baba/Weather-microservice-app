import React from 'react'
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

export default function TempChart({ chartData, metricLabel = 'Value' }) {
  if (!chartData) return null
  return (
    <div style={{ marginTop: 16 }}>
      <h4>{metricLabel} Trend</h4>
      <Line data={chartData} />
    </div>
  )
}
