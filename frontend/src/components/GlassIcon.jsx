// Glass-style icons, drawn from scratch. Same props as before: type + size.
export default function GlassIcon({ type, size = 64 }) {
  const defs = (
    <defs>
      <linearGradient id="wfSun" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#fef08a" /><stop offset="1" stopColor="#fb923c" /></linearGradient>
      <linearGradient id="wfFire" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#fdba74" /><stop offset="1" stopColor="#ef4444" /></linearGradient>
      <linearGradient id="wfMoon" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#ddd6fe" /><stop offset="1" stopColor="#8b5cf6" /></linearGradient>
      <linearGradient id="wfCloud" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#ffffff" stopOpacity=".95" /><stop offset="1" stopColor="#a5a3c9" stopOpacity=".85" /></linearGradient>
      <linearGradient id="wfWind" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stopColor="#7dd3fc" /><stop offset="1" stopColor="#a78bfa" /></linearGradient>
      <linearGradient id="wfViolet" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#a78bfa" /><stop offset="1" stopColor="#7c3aed" /></linearGradient>
      <linearGradient id="wfGlass" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stopColor="#ffffff" stopOpacity=".9" /><stop offset="1" stopColor="#ffffff" stopOpacity=".35" /></linearGradient>
      <linearGradient id="wfShine" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#ffffff" stopOpacity=".75" /><stop offset="1" stopColor="#ffffff" stopOpacity="0" /></linearGradient>
    </defs>
  )
  const base = { filter: 'drop-shadow(0 6px 10px rgba(80,60,160,0.28))' }
  const rim = 'rgba(255,255,255,0.85)'

  switch (type) {
    case 'sun':
    case 'clear_air':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" style={base} aria-hidden="true">
          {defs}
          <g stroke="#fbbf24" strokeWidth="5" strokeLinecap="round">
            <line x1="86" y1="50" x2="94" y2="50" /><line x1="75.5" y1="75.5" x2="81.1" y2="81.1" />
            <line x1="50" y1="86" x2="50" y2="94" /><line x1="24.5" y1="75.5" x2="18.9" y2="81.1" />
            <line x1="14" y1="50" x2="6" y2="50" /><line x1="24.5" y1="24.5" x2="18.9" y2="18.9" />
            <line x1="50" y1="14" x2="50" y2="6" /><line x1="75.5" y1="24.5" x2="81.1" y2="18.9" />
          </g>
          <circle cx="50" cy="50" r="27" fill="url(#wfSun)" stroke={rim} strokeWidth="1.5" />
          <ellipse cx="42" cy="38" rx="14" ry="9" fill="url(#wfShine)" />
        </svg>
      )
    case 'moon':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" style={base} aria-hidden="true">
          {defs}
          <path d="M 60 20 A 30 30 0 1 0 80 80 A 35 35 0 1 1 60 20 Z" fill="url(#wfMoon)" stroke={rim} strokeWidth="1.5" />
          <path d="M 60 20 A 30 30 0 1 0 80 80 A 35 35 0 1 1 60 20 Z" fill="url(#wfShine)" opacity=".5" />
        </svg>
      )
    case 'smoke':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" style={base} aria-hidden="true">
          {defs}
          <circle cx="52" cy="72" r="16" fill="url(#wfFire)" opacity=".55" filter="blur(7px)" />
          <path d="M 30 65 A 15 15 0 0 1 45 45 A 20 20 0 0 1 75 55 A 15 15 0 0 1 70 80 L 35 80 A 15 15 0 0 1 30 65 Z" fill="url(#wfCloud)" stroke={rim} strokeWidth="1.5" />
          <path d="M 40 52 Q 52 42 66 52" stroke="#ffffff" strokeOpacity=".8" strokeWidth="4" strokeLinecap="round" />
        </svg>
      )
    case 'fire':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" style={base} aria-hidden="true">
          {defs}
          <path d="M 50 20 Q 30 50 35 70 A 15 15 0 0 0 65 70 Q 70 50 50 20 Z" fill="url(#wfFire)" stroke={rim} strokeWidth="1.5" />
          <ellipse cx="46" cy="52" rx="6" ry="12" fill="url(#wfShine)" opacity=".7" />
        </svg>
      )
    case 'wind':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" style={base} aria-hidden="true">
          {defs}
          <path d="M 20 40 L 70 40 A 10 10 0 0 0 70 20 M 10 60 L 60 60 A 10 10 0 0 1 60 80 M 30 80 L 80 80 A 10 10 0 0 0 80 60" stroke="url(#wfWind)" strokeWidth="7" strokeLinecap="round" />
        </svg>
      )
    case 'clock':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" style={base} aria-hidden="true">
          {defs}
          <circle cx="50" cy="50" r="35" fill="url(#wfGlass)" stroke="rgba(124,58,237,0.35)" strokeWidth="2" />
          <polyline points="50,27 50,50 65,63" stroke="#7c3aed" strokeWidth="5" strokeLinecap="round" strokeLinejoin="round" />
          <circle cx="50" cy="50" r="4" fill="#7c3aed" />
        </svg>
      )
    case 'share':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" style={base} aria-hidden="true">
          {defs}
          <line x1="35" y1="45" x2="65" y2="30" stroke="#a78bfa" strokeWidth="3" strokeLinecap="round" />
          <line x1="35" y1="55" x2="65" y2="70" stroke="#a78bfa" strokeWidth="3" strokeLinecap="round" />
          <circle cx="75" cy="25" r="12" fill="url(#wfViolet)" stroke={rim} strokeWidth="1.5" />
          <circle cx="25" cy="50" r="12" fill="url(#wfViolet)" stroke={rim} strokeWidth="1.5" />
          <circle cx="75" cy="75" r="12" fill="url(#wfViolet)" stroke={rim} strokeWidth="1.5" />
        </svg>
      )
    default:
      return null
  }
}