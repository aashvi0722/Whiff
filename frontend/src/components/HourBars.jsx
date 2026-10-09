import { useLang } from '../i18n/useLang.jsx'
import { fmtHour } from '../lib/time.js'

const BAND = { good: 'none', satisfactory: 'low', moderate: 'medium', poor: 'high', very_poor: 'high', severe: 'severe' }
export const bandVar = b => `var(--risk-${BAND[b] || 'medium'})`

export default function HourBars({ hours = [], windows = [], from = 5, to = 22 }) {
  const { t, lang } = useLang()
  const byH = new Map(hours.map(x => [x.h, x]))
  const max = Math.max(60, ...hours.map(x => x.pm25 || 0))
  const inWin = h => windows.some(w => h >= w.start_h && h <= w.end_h)
  const slots = Array.from({ length: to - from + 1 }, (_, i) => from + i)
  return (
    <div className="hb" role="img" aria-label={t('hourly_pm25')}>
      {slots.map(h => {
        const x = byH.get(h)
        const h12 = h % 12 === 0 ? 12 : h % 12
        const tip = x ? `${fmtHour(h, lang)}: PM2.5 ${x.pm25}` : `${fmtHour(h, lang)}: ${t('no_data')}`
        return (
          <div key={h} className="hb-col" title={tip}>
            <div className="hb-wrap">
              {x
                ? <div className={'hb-bar' + (inWin(h) ? ' win' : '')}
                       style={{ height: `${Math.max(8, (x.pm25 / max) * 100)}%`, background: bandVar(x.band) }} />
                : <div className="hb-gap" />}
            </div>
            <span className="hb-t">{h % 3 === 0 ? (lang === 'hi' ? h : `${h12}${h < 12 ? 'a' : 'p'}`) : ''}</span>
          </div>
        )
      })}
    </div>
  )
}