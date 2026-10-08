import { useEffect, useState } from 'react';
import { getDayPlan } from '../api.js';
import { t } from '../i18n/index.js';

function getBandColor(band) {
  const map = { good: 'none', satisfactory: 'low', moderate: 'medium', poor: 'high', very_poor: 'high', severe: 'severe' };
  return `var(--risk-${map[band] || 'medium'})`;
}

export default function Day() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getDayPlan('day_windows').then(res => {
      setData(res);
      setLoading(false);
    });
  }, []);

  if (loading) return <div className="screen">Loading day plan...</div>;
  if (!data) return null;

  return (
    <div className="screen">
      
      <div style={{ marginTop: '12px' }}>
        <p className="text-soft" style={{ fontSize: '1rem', fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '4px' }}>
          {data.audience || 'General'} Profile
        </p>
        <h1 style={{ fontSize: '2.5rem' }}>Plan My Day</h1>
      </div>

      {/* Analytics Timeline */}
      <div className="glass-card" style={{ padding: '24px 16px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: '20px', padding: '0 8px' }}>
          <h3 className="text-soft text-sm" style={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>Hourly PM2.5</h3>
          <span className="text-soft" style={{ fontSize: '0.75rem' }}>*Estimated</span>
        </div>
        
        <div style={{ display: 'flex', gap: '8px', overflowX: 'auto', paddingBottom: '12px', paddingHorizontal: '8px', scrollbarWidth: 'none' }}>
          {data.hours?.map((hour) => (
            <div key={hour.h} style={{ flex: '0 0 44px', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'flex-end', height: '120px' }}>
              <span style={{ fontSize: '0.75rem', fontWeight: 600, color: getBandColor(hour.band), marginBottom: '8px', opacity: hour.status === 'stay' ? 0.3 : 1 }}>
                {hour.pm25}
              </span>
              <div 
                style={{ 
                  width: '100%',
                  height: `${Math.max(10, (hour.pm25 / 300) * 80)}px`,
                  background: getBandColor(hour.band),
                  borderRadius: '6px',
                  opacity: hour.status === 'stay' ? 0.3 : 1,
                  boxShadow: `0 0 12px ${getBandColor(hour.band)}40`
                }} 
              />
              <div className="text-soft" style={{ fontSize: '0.75rem', marginTop: '12px', fontWeight: 600 }}>
                {hour.h}:00
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Strategic Advice Cards */}
      <div className="glass-card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
          <h3 className="text-soft text-sm" style={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>
            Action Plan
          </h3>
          <span style={{ background: 'rgba(255,255,255,0.1)', padding: '4px 12px', borderRadius: '100px', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text)' }}>
            {data.day_state.replace('_', ' ').toUpperCase()}
          </span>
        </div>
        
        {data.day_state === 'windows' ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {data.windows?.map((win, i) => (
              <div key={i} style={{ background: 'rgba(0,0,0,0.2)', padding: '16px', borderRadius: '16px', borderLeft: `4px solid ${getBandColor(win.band)}` }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                  <strong style={{ fontSize: '1.2rem' }}>{win.start_h}:00 - {win.end_h + 1}:00</strong>
                  <span className="text-soft text-sm">Rank #{win.rank}</span>
                </div>
                <p className="text-soft" style={{ margin: 0, fontSize: '0.9rem', lineHeight: 1.5 }}>
                  {win.reason_codes?.map(rc => t(rc.code, 'en', rc.params)).join(', ')}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <div style={{ display: 'flex', justifyContent: 'space-between', background: 'rgba(0,0,0,0.2)', padding: '16px', borderRadius: '16px' }}>
            <div><span className="text-soft text-sm">Best Hour</span><br/><strong style={{fontSize: '1.2rem'}}>{data.best_hour}:00</strong></div>
            <div style={{textAlign: 'right'}}><span className="text-soft text-sm">Worst Hour</span><br/><strong style={{fontSize: '1.2rem'}}>{data.worst_hour}:00</strong></div>
          </div>
        )}
      </div>

      {/* Impact Chips */}
      <div style={{ display: 'flex', gap: '12px' }}>
        <div className="glass-card" style={{ flex: 1, padding: '16px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <span className="text-soft text-sm" style={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>Avoided</span>
          <strong style={{ fontSize: '1.5rem', color: 'var(--risk-none)' }}>{data.exposure_avoided_hours}h</strong>
        </div>
        <div className="glass-card" style={{ flex: 1, padding: '16px', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <span className="text-soft text-sm" style={{ textTransform: 'uppercase', letterSpacing: '0.05em' }}>Equivalent</span>
          <strong style={{ fontSize: '1.5rem', color: 'var(--risk-medium)' }}>🚬 ~{data.cigarette_equiv?.value}</strong>
        </div>
      </div>

    </div>
  );
}