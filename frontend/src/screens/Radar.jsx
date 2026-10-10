import ReplayPicker from '../components/ReplayPicker.jsx'
import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getSmokeRadar } from '../lib/api.js'
import { useApi } from '../lib/useApi.js'
import { useLang } from '../i18n/useLang.jsx'
import RadarSvg from '../components/RadarSvg.jsx'
import { Banners, ErrorCard, ScreenSkeleton } from '../components/StateViews.jsx'

const card8 = deg => ['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'][Math.round(deg / 45) % 8]
// Shown only in the first part of burning season. Delete this line's usage when the season is underway.
const isEarlySeason = () => { const d = new Date(); return d.getMonth() === 9 && d.getDate() <= 20 }

const PinIcon = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s7-6 7-11a7 7 0 0 0-14 0c0 5 7 11 7 11z" /><circle cx="12" cy="10" r="2.5" /></svg>
)

export default function Radar() {
  const { t, tryT, city, region } = useLang()
  const { status, data, reload } = useApi(getSmokeRadar)

  const risk = ['none', 'low', 'medium', 'high'].includes(data?.risk) ? data.risk : 'low'
  useEffect(() => {
    if (!data) return
    document.body.dataset.risk = risk
    return () => { delete document.body.dataset.risk }
  }, [data, risk])

  if (status === 'loading') return <ScreenSkeleton />
  if (!data) return <ErrorCard onRetry={reload} />

  const none = risk === 'none'
  const range = data.arrival_range_hours
  const top = [...(data.sources || [])].sort((a, b) => b.fire_count - a.fire_count)[0]
  const reasons = (data.reason_codes || []).map(r => tryT(r.code, r.params)).filter(Boolean)
  const confReasons = (data.confidence_reasons || []).map(c => tryT('cr_' + c)).filter(Boolean)
  const wind = data.wind
  const showSeason = (risk === 'low' || none) && data.mode !== 'replay' && isEarlySeason()

  return (
    <>
      <Banners data={data} />

      <section className="hero-sec stack" style={{ gap: 6 }}>
        <div className="row between">
          <span className="eyebrow row" style={{ gap: 6 }}><PinIcon />{city(data.location?.label)}</span>
          <span className={`pill risk-${risk}`}>{t('risk_' + risk)}</span>
        </div>
        <h1 className="hero-title">{none ? t('no_smoke') : t(risk === 'low' ? 'arrives_low' : 'arrives_in', { h: data.arrival_hours })}</h1>
        {!none && range && <p className="text-soft text-sm">{t('arrival_window', { a: range[0], b: range[1] })}</p>}
        {showSeason && <p className="text-soft text-sm">{t('low_season_note')}</p>}
      </section>

      <section className="glass-card radar-card">
        <RadarSvg data={data} risk={risk} />
        {wind && (
          <p className="radar-cap">
            {t('wind_from', { dir: t('dir_' + card8(wind.from_deg)), speed: wind.speed_kmh })}
          </p>
        )}
        <p className="radar-cap text-soft">{t('radar_legend')}</p>
      </section>

      {top && !none && (
        <section className="glass-card">
          <span className="eyebrow">{t('where_from')}</span>
          <div className="srcrow" style={{ marginTop: 6 }}>
            <strong>{region(top.region_code)}</strong>
            <span className="text-soft text-sm">{t('fires_n', { n: top.fire_count })} · {top.distance_km} km</span>
          </div>
        </section>
      )}

      <section className="glass-card">
        <h3 className="card-title">{t('conf_factors', { level: t('conf_' + data.confidence) })}</h3>
        {(reasons.length > 0 || confReasons.length > 0) && (
          <ul className="dots">
            {[...reasons, ...confReasons].map((r, i) => <li key={i}>{r}</li>)}
          </ul>
        )}
        <details className="explain">
          <summary>{t('conf_what')}</summary>
          <p style={{ marginTop: 6 }}>{t('conf_explain')}</p>
        </details>
      </section>

      {data.festival?.active && (
        <section className="glass-card" style={{ borderLeft: '4px solid #8b5cf6' }}>
          <h3 className="card-title">🎆 {t('festival_title')}</h3>
          <p className="text-soft text-sm" style={{ marginTop: 4 }}>{t('festival_note', { name: data.festival.name || '' })}</p>
        </section>
      )}

      <ReplayPicker />

      <Link className="btn" to="/day">{t('plan_my_day')} →</Link>
      <p className="text-soft text-sm" style={{ textAlign: 'center' }}>{t('disclaimer')}</p>
    </>
  )
}