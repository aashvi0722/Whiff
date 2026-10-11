import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { useLang } from '../i18n/useLang.jsx'
import { fmtHour } from '../lib/time.js'
import { getLog, logAction, todayKey, counts, streakInfo } from '../lib/streak.js'

export default function CheckIn({ data }) {
  const { t, lang } = useLang()
  const [log, setLog] = useState(getLog)
  useEffect(() => {
    const f = () => setLog(getLog())
    window.addEventListener('whiff-log', f)
    return () => window.removeEventListener('whiff-log', f)
  }, [])
  const state = data.day_state
  const goDay = state === 'windows'
  const wins = data.windows || []
  const hour = new Date().getHours()
  const sorted = [...wins].sort((a, b) => a.start_h - b.start_h)
const first = sorted[0]
const next = sorted.find(w => w.start_h > hour)
const demo = new URLSearchParams(window.location.search).get('demo') === '1'
// honor system: once the first window has opened, you can log any time today
const canDo = !goDay || demo || (!!first && hour >= first.start_h)
  const done = counts(log[todayKey()])
  const { current } = streakInfo(log)
  const k = goDay ? 'go' : 'stay'
  const doIt = () => logAction({ day_state: state, action: goDay ? 'went_out' : 'stayed_in',
    exposure_avoided_hours: data.exposure_avoided_hours, best_start_h: first?.start_h })
  return (
    <section className="glass-card stack" style={{ gap: 10 }}>
      <div className="row between">
        <span className="eyebrow">{t('checkin_title')}</span>
        <span className="streak-pill">🔥 {current}</span>
      </div>
      {done ? <p>✓ {t('checkin_done_' + k)}</p> : (
        <>
          <p className="text-soft text-sm">{t('checkin_' + k + '_hint')}</p>
          <button className="btn" disabled={!canDo} onClick={doIt}>{t('checkin_btn_' + k)}</button>
          {!canDo && next && <p className="text-soft text-sm">{t('checkin_opens', { time: fmtHour(next.start_h, lang) })}</p>}
          {!canDo && !next && <p className="text-soft text-sm">{t('checkin_closed')}</p>}
        </>
      )}
      <div className="row between">
        <Link to="/streak" className="text-sm" style={{ fontWeight: 600 }}>{t('checkin_see')} →</Link>
        <span className="text-soft text-sm">{t('honor_note')}</span>
      </div>
    </section>
  )
}