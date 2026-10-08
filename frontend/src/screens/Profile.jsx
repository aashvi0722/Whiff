import { useState, useEffect } from 'react';

export default function Profile() {
  const [audience, setAudience] = useState('general');

  useEffect(() => {
    const saved = localStorage.getItem('whiff_audience');
    if (saved) setAudience(saved);
  }, []);

  const handleSelect = (id) => {
    setAudience(id);
    localStorage.setItem('whiff_audience', id);
  };

  const options = [
    { id: 'general', label: 'Just Me', desc: 'Standard AQI guidance' },
    { id: 'sensitive', label: 'Sensitive', desc: 'Asthma, allergies, or respiratory conditions' },
    { id: 'child', label: 'With a Child', desc: 'Stricter thresholds for developing lungs' },
    { id: 'outdoor', label: 'Outdoor Worker', desc: 'Guidance for prolonged exposure' }
  ];

  return (
    <div className="screen">
      
      <div style={{ marginTop: '12px', marginBottom: '24px' }}>
        <p className="text-soft" style={{ fontSize: '1rem', fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: '4px' }}>
          Personalize
        </p>
        <h1 style={{ fontSize: '3rem', lineHeight: '1' }}>My Profile</h1>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
        {options.map(opt => {
          const isActive = audience === opt.id;
          return (
            <button
              key={opt.id}
              className="glass-card"
              onClick={() => handleSelect(opt.id)}
              style={{
                textAlign: 'left',
                padding: '24px',
                background: isActive ? 'rgba(168, 85, 247, 0.15)' : 'var(--glass-bg)',
                borderColor: isActive ? '#a855f7' : 'var(--glass-border)',
                borderTopColor: isActive ? '#d8b4fe' : 'var(--glass-highlight)',
                boxShadow: isActive ? '0 0 32px rgba(168, 85, 247, 0.2)' : '0 24px 48px rgba(0,0,0,0.4)',
                cursor: 'pointer',
                outline: 'none',
                width: '100%',
                transition: 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)'
              }}
            >
              <div style={{ 
                fontWeight: 600, 
                fontSize: '1.25rem', 
                color: isActive ? '#e9d5ff' : 'var(--text)',
                marginBottom: '8px'
              }}>
                {opt.label}
              </div>
              <div className="text-soft" style={{ fontSize: '0.9rem', lineHeight: 1.4 }}>
                {opt.desc}
              </div>
            </button>
          );
        })}
      </div>

    </div>
  );
}