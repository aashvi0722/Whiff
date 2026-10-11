import { useState } from 'react'
import { useLang } from '../i18n/useLang.jsx'
import { getCity } from '../lib/api.js'
const CITIES = [
  { label: 'Delhi', lat: 28.61, lon: 77.21 }, { label: 'Lucknow', lat: 26.85, lon: 80.95 },
  { label: 'Bengaluru', lat: 12.97, lon: 77.59 }, { label: 'Chennai', lat: 13.08, lon: 80.27 },
  { label: 'Chandigarh', lat: 30.73, lon: 76.78 },
]
const save = v => { try { localStorage.setItem('whiff_city', JSON.stringify(v)) } catch { /* blocked */ } }
export default function LocationCard() {
  const { t, city: cityName } = useLang()
  const [place, setPlace] = useState(() => {
    const c = getCity()
    return CITIES.find(x => x.lat === c.lat && x.lon === c.lon)?.label || (c.custom ? 'custom' : 'Delhi')
  })
  const [geo, setGeo] = useState('idle')
  const pick = c => { setPlace(c.label); save({ lat: c.lat, lon: c.lon }) }
  const locate = () => {
    if (!navigator.geolocation) return setGeo('unsupported')
    setGeo('busy')
    navigator.geolocation.getCurrentPosition(
      p => { save({ lat: +p.coords.latitude.toFixed(2), lon: +p.coords.longitude.toFixed(2), custom: true }); setPlace('custom'); setGeo('idle') },
      () => setGeo('denied'), { timeout: 10000, maximumAge: 600000 })
  }
  return (
    <section className="glass-card stack" style={{ gap: 10 }}>
      <span className="eyebrow">{t('location_title')}</span>
      <div className="chips">
        {CITIES.map(c => (
          <button key={c.label} className={'chip' + (place === c.label ? ' on' : '')} aria-pressed={place === c.label} onClick={() => pick(c)}>{cityName(c.label)}</button>
        ))}
        {place === 'custom' && <span className="chip on">{t('my_location')}</span>}
      </div>
      <button className="btn ghost" onClick={locate} disabled={geo === 'busy'}>{geo === 'busy' ? t('loading') : t('use_location')}</button>
      {geo === 'denied' && <p className="text-soft text-sm" role="alert">{t('geo_denied')}</p>}
      {geo === 'unsupported' && <p className="text-soft text-sm" role="alert">{t('geo_unsupported')}</p>}
      <p className="text-soft text-sm">{t('location_note')}</p>
    </section>
  )
}