export const BANDS = [
  { k: 'good', from: 0, to: 50, c: '#22c55e' }, { k: 'satisfactory', from: 51, to: 100, c: '#a3e635' },
  { k: 'moderate', from: 101, to: 200, c: '#facc15' }, { k: 'poor', from: 201, to: 300, c: '#fb923c' },
  { k: 'very_poor', from: 301, to: 400, c: '#ef4444' }, { k: 'severe', from: 401, to: 500, c: '#9f1239' },
]
export const bandOf = aqi => (BANDS.find(b => aqi <= b.to) || BANDS[5]).k