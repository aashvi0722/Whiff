export default function GlassIcon({ type, size = 64 }) {
  const defs = (
    <defs>
      {/* Dark mode glass gradient */}
      <linearGradient id="darkGlass" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="rgba(255, 255, 255, 0.15)" />
        <stop offset="100%" stopColor="rgba(255, 255, 255, 0.02)" />
      </linearGradient>
      {/* Neon glowing gradients */}
      <linearGradient id="neonSun" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#fde047" />
        <stop offset="100%" stopColor="#f59e0b" />
      </linearGradient>
      <linearGradient id="neonFire" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#f87171" />
        <stop offset="100%" stopColor="#dc2626" />
      </linearGradient>
      <linearGradient id="neonWind" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stopColor="#7dd3fc" />
        <stop offset="100%" stopColor="#0ea5e9" />
      </linearGradient>
    </defs>
  );

  const baseStyle = { filter: 'drop-shadow(0 8px 16px rgba(0,0,0,0.4))' };

  switch (type) {
    case 'sun':
    case 'clear_air':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" style={baseStyle}>
          {defs}
          <circle cx="50" cy="50" r="30" fill="url(#neonSun)" opacity="0.9" />
          <circle cx="50" cy="50" r="30" fill="url(#darkGlass)" stroke="rgba(255,255,255,0.4)" strokeWidth="1.5" />
        </svg>
      );
    
    case 'moon':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" style={baseStyle}>
          {defs}
          <path d="M 60 20 A 30 30 0 1 0 80 80 A 35 35 0 1 1 60 20 Z" fill="#c084fc" opacity="0.9" />
          <path d="M 60 20 A 30 30 0 1 0 80 80 A 35 35 0 1 1 60 20 Z" fill="url(#darkGlass)" stroke="rgba(255,255,255,0.4)" strokeWidth="1.5" />
        </svg>
      );

    case 'smoke':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" style={baseStyle}>
          {defs}
          {/* Neon warning base */}
          <circle cx="50" cy="50" r="25" fill="url(#neonFire)" opacity="0.5" filter="blur(8px)" />
          {/* Frosted cloud */}
          <path d="M 30 65 A 15 15 0 0 1 45 45 A 20 20 0 0 1 75 55 A 15 15 0 0 1 70 80 L 35 80 A 15 15 0 0 1 30 65 Z" fill="url(#darkGlass)" stroke="rgba(255,255,255,0.4)" strokeWidth="1.5" />
          <path d="M 40 40 Q 55 25 70 40" stroke="rgba(255,255,255,0.3)" strokeWidth="4" strokeLinecap="round" />
        </svg>
      );

    case 'fire':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" style={baseStyle}>
          {defs}
          <path d="M 50 20 Q 30 50 35 70 A 15 15 0 0 0 65 70 Q 70 50 50 20 Z" fill="url(#neonFire)" opacity="0.9" />
          <path d="M 50 20 Q 30 50 35 70 A 15 15 0 0 0 65 70 Q 70 50 50 20 Z" fill="url(#darkGlass)" stroke="rgba(255,255,255,0.4)" strokeWidth="1.5" />
        </svg>
      );

    case 'wind':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" style={baseStyle}>
          {defs}
          <path d="M 20 40 L 70 40 A 10 10 0 0 0 70 20 M 10 60 L 60 60 A 10 10 0 0 1 60 80 M 30 80 L 80 80 A 10 10 0 0 0 80 60" stroke="url(#neonWind)" strokeWidth="6" strokeLinecap="round" />
          <rect x="0" y="0" width="100" height="100" fill="url(#darkGlass)" opacity="0.5" />
        </svg>
      );

    case 'clock':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" style={baseStyle}>
          {defs}
          <circle cx="50" cy="50" r="35" fill="url(#darkGlass)" stroke="rgba(255,255,255,0.4)" strokeWidth="2" />
          <polyline points="50,25 50,50 65,65" stroke="#a855f7" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      );

    case 'share':
      return (
        <svg width={size} height={size} viewBox="0 0 100 100" fill="none" style={baseStyle}>
          {defs}
          <circle cx="75" cy="25" r="12" fill="url(#darkGlass)" stroke="rgba(255,255,255,0.4)" strokeWidth="1.5" />
          <circle cx="25" cy="50" r="12" fill="url(#darkGlass)" stroke="rgba(255,255,255,0.4)" strokeWidth="1.5" />
          <circle cx="75" cy="75" r="12" fill="url(#darkGlass)" stroke="rgba(255,255,255,0.4)" strokeWidth="1.5" />
          <line x1="35" y1="45" x2="65" y2="30" stroke="rgba(255,255,255,0.6)" strokeWidth="2" />
          <line x1="35" y1="55" x2="65" y2="70" stroke="rgba(255,255,255,0.6)" strokeWidth="2" />
        </svg>
      );

    default:
      return null;
  }
}