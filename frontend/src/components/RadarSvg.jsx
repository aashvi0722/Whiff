const C = 160, R = 136, MAX = 600

function polar(km, deg) {
  const r = (Math.min(km, MAX) / MAX) * R
  const a = (deg * Math.PI) / 180
  return [C + r * Math.sin(a), C - r * Math.cos(a)]
}

export default function RadarSvg({ data, risk }) {
  const color = `var(--risk-${risk})`
  const sources = data.sources || []
  const windDir = data.wind ? (data.wind.from_deg + 180) % 360 : null
  const tip = R * 0.62
  return (
    <svg className="radar-svg" viewBox="0 0 320 320" role="img"
         aria-label={`Smoke radar: ${sources.length} fire clusters, risk ${risk}`}>
      <circle className="rd-base" cx={C} cy={C} r={R + 2} />
      {[200, 400, 600].map((km, i) => {
        const r = (km / MAX) * R
        return (
          <g key={km}>
            <circle className={'rd-ring' + (i === 2 ? ' solid' : '')} cx={C} cy={C} r={r} />
            <text className="rd-label" x={C + 4} y={C - r - 3}>{km} km</text>
          </g>
        )
      })}
      <text className="rd-label" x={C} y="12" textAnchor="middle" style={{ fontSize: 10 }}>N</text>

      <circle className="rd-sonar" cx={C} cy={C} r="20" />

      {windDir !== null && (
        <g transform={`rotate(${windDir} ${C} ${C})`}>
          <line className="rd-arrow" x1={C} y1={C - 14} x2={C} y2={C - tip + 8} />
          <polygon className="rd-head" points={`${C - 7},${C - tip + 12} ${C},${C - tip - 2} ${C + 7},${C - tip + 12}`} />
        </g>
      )}

      {sources.map((s, i) => {
        const [x, y] = polar(s.distance_km, s.bearing_deg)
        const rad = Math.max(5, Math.min(15, 3 + Math.sqrt(s.fire_count) * 0.55))
        return (
          <g key={i}>
            <line x1={x} y1={y} x2={C} y2={C} stroke={color} strokeOpacity=".4" strokeWidth="1.2" strokeDasharray="3 4" />
            <circle className="rd-pulse" cx={x} cy={y} r={rad} fill={color} />
            <circle cx={x} cy={y} r={rad} fill={color} fillOpacity=".92" stroke="#fff" strokeWidth="2" />
          </g>
        )
      })}

      <circle className="rd-you" cx={C} cy={C} r="5" />
      <circle cx={C} cy={C} r="9" fill="none" stroke="var(--text)" strokeOpacity=".35" />
    </svg>
  )
}