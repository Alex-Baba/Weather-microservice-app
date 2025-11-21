import { useMemo } from 'react'

export default function useChartData(history, selectedCities, selectedMetric) {
  return useMemo(() => {
    if (!history || history.length === 0 || !selectedCities || selectedCities.length === 0) return null

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

    return { labels: allLabels, datasets: finalDatasets }
  }, [history, selectedCities, selectedMetric])
}
