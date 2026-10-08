import { useEffect, useState } from 'react';
import { getSmokeRadar } from '../api.js';
import { t } from '../i18n/index.js';

const MAX_RADAR_KM = 500;
const RADAR_SVG_RADIUS = 90;

function getSvgCoords(distanceKm, bearingDeg) {
  const radius = (Math.min(distanceKm, MAX_RADAR_KM) / MAX_RADAR_KM) * RADAR_SVG_RADIUS;
  const angleRad = (bearingDeg - 90) * (Math.PI / 180);
  return {
    x: 100 + radius * Math.cos(angleRad),
    y: 100 + radius * Math.sin(angleRad)
  };
}

export default function Radar() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getSmokeRadar('smoke_high').then(res => {
      setData(res);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="screen">Loading radar...</div>;
  if (!data) return null;

  return (
    <div className="screen">
      {/* Massive Typography Header */}
      <div style={{ marginTop: '12px' }}>
        <p className="text-soft" style={{ fontSize: '1rem', fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '4px' }}>
          {data.location.label} Current
        </p>
        <h1 style={{ fontSize: '4rem', lineHeight: '1', color: `var(--risk-${data.risk})`, textTransform: 'capitalize', textShadow: `0 0 32px var(--risk-${data.risk})` }}>
          {data.risk}
        </h1>
      </div>

      {/* Glowing Neon Radar */}
      <div style={{ position: 'relative', width: '100%', maxWidth: '340px', margin: '24px auto' }}>
        <svg viewBox="0 0 200 200" style={{ filter: 'drop-shadow(0 0 24px rgba(0,0,0,0.5))' }}>
          <circle cx="100" cy="100" r="98" fill="rgba(0,0,0,0.2)" stroke="var(--glass-border)" strokeWidth="1" />
          
          <circle cx="100" cy="100" r="30" fill="none" stroke="rgba(255,255,255,0.4)" strokeWidth="1">
            <animate attributeName="r" values="30;98" dur="3s" repeatCount="indefinite" />
            <animate attributeName="opacity" values="1;0" dur="3s" repeatCount="indefinite" />
          </circle>

          <circle cx="100" cy="100" r="90" fill="none" stroke="var(--text-soft)" strokeWidth="0.5" strokeDasharray="2 4" opacity="0.4" />
          <circle cx="100" cy="100" r="60" fill="none" stroke="var(--text-soft)" strokeWidth="0.5" strokeDasharray="2 4" opacity="0.4" />
          <circle cx="100" cy="100" r="30" fill="none" stroke="var(--text-soft)" strokeWidth="0.5" opacity="0.4" />
          
          <circle cx="100" cy="100" r="3" fill="#fff" />

          {data.wind && (
            <g transform={`rotate(${data.wind.from_deg + 180} 100 100)`}>
              <line x1="100" y1="100" x2="100" y2="15" stroke="var(--text-soft)" strokeWidth="2" strokeDasharray="3 3" opacity="0.8"/>
              <polygon points="96,22 100,15 104,22" fill="var(--text-soft)" />
            </g>
          )}

          {data.sources?.map((source, i) => {
            const { x, y } = getSvgCoords(source.distance_km, source.bearing_deg);
            const dotSize = Math.max(4, Math.min(12, source.fire_count / 30)); 
            return (
              <g key={i}>
                <circle cx={x} cy={y} r={dotSize} fill={`var(--risk-${data.risk})`} opacity="0.2">
                  <animate attributeName="r" values={`${dotSize};${dotSize * 3};${dotSize}`} dur="2s" repeatCount="indefinite" />
                  <animate attributeName="opacity" values="0.4;0;0.4" dur="2s" repeatCount="indefinite" />
                </circle>
                <circle cx={x} cy={y} r={dotSize * 0.6} fill={`var(--risk-${data.risk})`} stroke="#000" strokeWidth="2" />
              </g>
            );
          })}
        </svg>
      </div>

      {/* Data-Dense Forecast Card */}
      <div className="glass-card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h3 className="text-soft text-sm" style={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>Forecast</h3>
          {data.risk === 'none' ? (
            <p style={{ margin: '4px 0 0 0', fontSize: '1.2rem', fontWeight: 600 }}>Clear Skies</p>
          ) : (
            <p style={{ margin: '4px 0 0 0', fontSize: '1.2rem', fontWeight: 600 }}>
              Arrival in <span style={{ color: `var(--risk-${data.risk})` }}>~{data.arrival_hours}h</span>
            </p>
          )}
        </div>
        {data.risk !== 'none' && (
          <div style={{ textAlign: 'right' }}>
            <span className="text-soft text-sm">Window</span>
            <div style={{ fontWeight: 600 }}>{data.arrival_range_hours?.[0]}h - {data.arrival_range_hours?.[1]}h</div>
          </div>
        )}
      </div>

      <div className="glass-card">
        <h3 className="text-soft text-sm" style={{ textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>
          {data.confidence} Confidence Factors
        </h3>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {data.reason_codes?.map((rc, i) => (
            <div key={i} style={{ display: 'flex', alignItems: 'flex-start', gap: '12px' }}>
              <div style={{ width: '6px', height: '6px', borderRadius: '50%', background: 'var(--text-soft)', marginTop: '8px' }} />
              <p style={{ margin: 0, lineHeight: 1.5 }}>{t(rc.code, 'en', rc.params)}</p>
            </div>
          ))}
        </div>
      </div>

      {data.festival?.active && (
        <div className="glass-card" style={{ background: 'rgba(168, 85, 247, 0.1)', borderColor: 'rgba(168, 85, 247, 0.3)', borderTopColor: 'rgba(168, 85, 247, 0.6)' }}>
          <h3 style={{ color: '#d8b4fe', marginBottom: '8px' }}>🎇 Festival Alert: {data.festival.name}</h3>
          <p className="text-soft" style={{ margin: 0 }}>Local emissions will compound incoming smoke tonight.</p>
        </div>
      )}
    </div>
  );
}