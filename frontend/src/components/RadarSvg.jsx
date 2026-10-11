// Radar: same data in, livelier picture out. Only the drawing changed.
const C = 160, R = 136, MAX = 600

function polar(km, deg) {
  const r = (Math.min(km, MAX) / MAX) * R
  const a = (deg * Math.PI) / 180
  return [C + r * Math.sin(a), C - r * Math.cos(a)]
}

const CARDINALS = [['N', 0], ['E', 90], ['S', 180], ['W', 270]]
const TICKS = Array.from({ length: 12 }, (_, i) => i * 30)
const STREAKS = [-100, -68, -34, 0, 34, 68, 100]

export default function RadarSvg({ data, risk }) {
  const color = `var(--risk-${risk})`
  const sources = data.sources || []
  const windDir = data.wind ? (data.wind.from_deg + 180) % 360 : null
  const speed = data.wind?.speed_kmh ?? 12
  const flowSec = Math.max(2.4, Math.min(7, 60 / Math.max(speed, 8)))
  const tip = R * 0.62
  const at = (deg, r) => {
    const a = (deg * Math.PI) / 180
    return [C + r * Math.sin(a), C - r * Math.cos(a)]
  }

  return (
    <svg className="radar-svg" viewBox="0 0 320 320" role="img"
         aria-label={`Smoke radar: ${sources.length} fire clusters, risk ${risk}`}>
      <defs>
        <radialGradient id="rdGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0" style={{ stopColor: 'var(--accent1)', stopOpacity: 0.2 }} />
          <stop offset="1" style={{ stopColor: 'var(--accent1)', stopOpacity: 0.02 }} />
        </radialGradient>
        <linearGradient id="rdSweepG" x1="1" y1="0" x2="0" y2="0">
          <stop offset="0" style={{ stopColor: 'var(--accent1)', stopOpacity: 0.4 }} />
          <stop offset="1" style={{ stopColor: 'var(--accent1)', stopOpacity: 0 }} />
        </linearGradient>
        <clipPath id="rdClip"><circle cx={C} cy={C} r={R} /></clipPath>
      </defs>

      <circle className="rd-base" cx={C} cy={C} r={R + 2} />
      <circle cx={C} cy={C} r={R} fill="url(#rdGlow)" />

      {TICKS.map((d) => {
        const major = d % 90 === 0
        const [x1, y1] = at(d, R - (major ? 10 : 6))
        const [x2, y2] = at(d, R)
        return <line key={d} className={'rd-tick' + (major ? ' major' : '')} x1={x1} y1={y1} x2={x2} y2={y2} />
      })}
      {CARDINALS.map(([l, d]) => {
        const [x, y] = at(d, R + 14)
        return (
          <text key={l} className="rd-label" x={x} y={y + 3} textAnchor="middle" style={{ fontSize: 10 }}>{l}</text>
        )
      })}

      {[200, 400, 600].map((km, i) => {
        const r = (km / MAX) * R
        return (
          <g key={km}>
            <circle className={'rd-ring' + (i === 2 ? ' solid' : '')} cx={C} cy={C} r={r} />
            {i < 2 && <text className="rd-label" x={C + 5} y={C - r - 3}>{km} km</text>}
          </g>
        )
      })}

      <g clipPath="url(#rdClip)">
        <g className="rd-sweep">
          <path d={`M${C} ${C} L${C} ${C - R} A${R} ${R} 0 0 0 ${C - 111.4} ${C - 78} Z`} fill="url(#rdSweepG)" />
          <line className="rd-sweep-line" x1={C} y1={C} x2={C} y2={C - R} />
        </g>
        {windDir !== null && (
          <g transform={`rotate(${windDir} ${C} ${C})`}>
            {STREAKS.map((dx, i) => (
              <line key={dx} className="rd-flow" x1={C + dx} y1={C + R} x2={C + dx} y2={C - R}
                    style={{ animationDuration: `${flowSec}s`, animationDelay: `${-i * 0.55}s` }} />
            ))}
          </g>
        )}
      </g>

      <circle className="rd-sonar" cx={C} cy={C} r="20" />

      {windDir !== null && (
        <g transform={`rotate(${windDir} ${C} ${C})`}>
          <line className="rd-arrow" x1={C} y1={C - 14} x2={C} y2={C - tip + 8} />
          <polygon className="rd-head" points={`${C - 8},${C - tip + 13} ${C},${C - tip - 3} ${C + 8},${C - tip + 13}`} />
        </g>
      )}

      {sources.map((s, i) => {
        const [x, y] = polar(s.distance_km, s.bearing_deg)
        const rad = Math.max(5, Math.min(15, 3 + Math.sqrt(s.fire_count) * 0.55))
        return (
          <g key={i}>
            <line x1={x} y1={y} x2={C} y2={C} stroke={color} strokeOpacity=".35" strokeWidth="1.2" strokeDasharray="3 4" />
            {[0, 2].map((off) => (
              <circle key={off} className="rd-puff" r="3.5" fill={color} opacity="0">
                <animate attributeName="cx" values={`${x};${C}`} dur="4s" begin={`${-(i * 1.1 + off)}s`} repeatCount="indefinite" />
                <animate attributeName="cy" values={`${y};${C}`} dur="4s" begin={`${-(i * 1.1 + off)}s`} repeatCount="indefinite" />
                <animate attributeName="opacity" values="0;.8;0" keyTimes="0;.35;1" dur="4s" begin={`${-(i * 1.1 + off)}s`} repeatCount="indefinite" />
              </circle>
            ))}
            <circle cx={x} cy={y} r={rad * 2.3} fill={color} fillOpacity=".16" />
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