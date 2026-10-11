import { useLang } from '../i18n/useLang.jsx'
import { BANDS, bandOf } from '../lib/aqi.js'
import { fmtHour } from '../lib/time.js'

export default function AqiCard({ day, replay }) {
  const { t, lang } = useLang()
  const hours = day?.hours || []
  if (!hours.length || (replay && day.mode !== 'replay')) return null
  const now = new Date().getHours()
  const pick = replay
    ? hours.find(x => x.h === day.worst_hour) || hours.reduce((a, b) => (b.aqi > a.aqi ? b : a))
    : hours.reduce((a, b) => (Math.abs(b.h - now) < Math.abs(a.h - now) ? b : a))
  if (pick?.aqi == null) return null
  const k = bandOf(pick.aqi)
  const pct = Math.min(500, pick.aqi) / 5
  return (
    <section className="glass-card stack" style={{ gap: 8 }}>
      <div className="row between">
        <span className="eyebrow">{replay ? t('aqi_peak') : t('aqi_now')}</span>
        <span className="text-soft text-sm">*{t('estimated')}</span>
      </div>
      <div className="row" style={{ alignItems: 'baseline', gap: 10 }}>
        <span className="aqi-num" style={{ color: BANDS.find(b => b.k === k).c }}>{pick.aqi}</span>
        <strong>{t('band_' + k)}</strong>
        <span className="text-soft text-sm">{fmtHour(pick.h, lang)}</span>
      </div>
      <div className="aqi-scale" role="img" aria-label={`AQI ${pick.aqi}, ${t('band_' + k)}`}>
        {BANDS.map(b => <span key={b.k} style={{ flex: b.to - b.from + 1, background: b.c }} />)}
        <i className="aqi-mark" style={{ left: `${pct}%` }} />
      </div>
      <div className="aqi-legend">
        {BANDS.map(b => (
          <span key={b.k}><i style={{ background: b.c }} />{t('band_' + b.k)} {b.from}–{b.to}</span>
        ))}
      </div>
      <p className="text-soft text-sm">{t('aqi_note')}</p>
        <a className="text-sm" href="https://airquality.cpcb.gov.in/ccr/#/" target="_blank" rel="noopener noreferrer" style={{ fontWeight: 600 }}>{t('ground_link')} ↗</a>
    </section>
  )
}