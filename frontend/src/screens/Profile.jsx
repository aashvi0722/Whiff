import { useState } from 'react'
import { useLang } from '../i18n/useLang.jsx'
import { getAudience, getCity } from '../lib/api.js'

const AUD = [
  { id: 'general', icon: <><circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 4-6 8-6s8 2 8 6" /></> },
  { id: 'sensitive', icon: <path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.5A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z" /> },
  { id: 'child', icon: <><circle cx="9" cy="8" r="3.5" /><circle cx="17" cy="10" r="2.5" /><path d="M2 20c0-4 3-6 7-6s7 2 7 6" /></> },
  { id: 'outdoor', icon: <><path d="M4 16a8 8 0 0 1 16 0z" /><path d="M2 19h20M12 8v4" /></> },
]
const CITIES = [
  { label: 'Delhi', lat: 28.61, lon: 77.21 }, { label: 'Lucknow', lat: 26.85, lon: 80.95 },
  { label: 'Bengaluru', lat: 12.97, lon: 77.59 }, { label: 'Chennai', lat: 13.08, lon: 80.27 },
  { label: 'Chandigarh', lat: 30.73, lon: 76.78 },
]
const save = (k, v) => { try { localStorage.setItem(k, v) } catch { /* storage blocked */ } }

export default function Profile() {
  const { t, city: cityName } = useLang()
  const [audience, setAudience] = useState(getAudience)
  const [place, setPlace] = useState(() => {
    const c = getCity()
    return CITIES.find(x => x.lat === c.lat && x.lon === c.lon)?.label || (c.custom ? 'custom' : 'Delhi')
  })
  const [geo, setGeo] = useState('idle') // idle | busy | denied | unsupported

  const pickAudience = id => { setAudience(id); save('whiff_audience', id) }
  const pickCity = c => {
    setPlace(c.label)
    save('whiff_city', JSON.stringify({ lat: c.lat, lon: c.lon }))
  }
  const useMyLocation = () => {
    if (!navigator.geolocation) return setGeo('unsupported')
    setGeo('busy')
    navigator.geolocation.getCurrentPosition(
      pos => {
        const lat = +pos.coords.latitude.toFixed(2), lon = +pos.coords.longitude.toFixed(2)
        save('whiff_city', JSON.stringify({ lat, lon, custom: true }))
        setPlace('custom'); setGeo('idle')
      },
      () => setGeo('denied'),
      { timeout: 10000, maximumAge: 600000 },
    )
  }

  return (
    <>
      <section className="hero-sec stack" style={{ gap: 4 }}>
        <span className="eyebrow">{t('personalize')}</span>
        <h1 className="hero-title">{t('profile_title')}</h1>
        <p className="text-soft text-sm">{t('profile_hint')}</p>
      </section>

      <section className="stack" role="radiogroup" aria-label={t('who_for')}>
        <span className="eyebrow">{t('who_for')}</span>
        {AUD.map(o => {
          const on = audience === o.id
          return (
            <button key={o.id} role="radio" aria-checked={on} className={'opt glass-card' + (on ? ' on' : '')} onClick={() => pickAudience(o.id)}>
              <span className="opt-ic"><svg className="ni" viewBox="0 0 24 24" aria-hidden="true">{o.icon}</svg></span>
              <span className="opt-tx">
                <strong>{t('aud_' + o.id)}</strong>
                <span className="text-soft text-sm">{t('aud_' + o.id + '_d')}</span>
              </span>
              <span className="opt-tick" aria-hidden="true">
                <svg className="ni" viewBox="0 0 24 24"><path d="M5 12l5 5 9-10" /></svg>
              </span>
            </button>
          )
        })}
      </section>

      <section className="glass-card stack" style={{ gap: 10 }}>
        <span className="eyebrow">{t('location_title')}</span>
        <div className="chips">
          {CITIES.map(c => (
            <button key={c.label} className={'chip' + (place === c.label ? ' on' : '')} aria-pressed={place === c.label} onClick={() => pickCity(c)}>
              {cityName(c.label)}
            </button>
          ))}
          {place === 'custom' && <span className="chip on">{t('my_location')}</span>}
        </div>
        <button className="btn ghost" onClick={useMyLocation} disabled={geo === 'busy'}>
          {geo === 'busy' ? t('loading') : t('use_location')}
        </button>
        {geo === 'denied' && <p className="text-soft text-sm" role="alert">{t('geo_denied')}</p>}
        {geo === 'unsupported' && <p className="text-soft text-sm" role="alert">{t('geo_unsupported')}</p>}
        <p className="text-soft text-sm">{t('location_note')}</p>
      </section>

      <p className="text-soft text-sm" style={{ textAlign: 'center' }}>{t('disclaimer')}</p>
    </>
  )
}