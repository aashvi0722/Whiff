import { useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { toPng } from 'html-to-image'
import { useLang } from '../i18n/useLang.jsx'
import { getLog, counts, streakInfo } from '../lib/streak.js'
import { fmtHour } from '../lib/time.js'
import { useProfile } from '../lib/profile.js'

export default function Wrapped() {
  const { t, lang } = useLang()
  const { name } = useProfile()
  const ref = useRef(null)
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState(false)
  const log = getLog()
  const since = new Date(); since.setDate(since.getDate() - 6); since.setHours(0, 0, 0, 0)
  const week = Object.values(log).filter(e => new Date(e.date + 'T00:00:00') >= since && counts(e))
  const avoided = week.reduce((s, e) => s + (e.exposure_avoided_hours || 0), 0)
  const outs = week.filter(e => e.action === 'went_out').length
  const stays = week.filter(e => e.action === 'stayed_in').length
  const freq = {}
  week.forEach(e => { if (e.best_start_h != null) freq[e.best_start_h] = (freq[e.best_start_h] || 0) + 1 })
  const top = Object.keys(freq).sort((a, b) => freq[b] - freq[a])[0]
  const { current } = streakInfo(log)

  const share = async () => {
  setBusy(true); setErr(false)
  try {
    const url = await toPng(ref.current, { pixelRatio: 2, cacheBust: true })
    const a = document.createElement('a')
    a.href = url; a.download = 'weekly-whiff.png'
    document.body.appendChild(a); a.click(); a.remove()
  } catch { setErr(true) } finally { setBusy(false) }
}

  if (week.length === 0) return (
    <section className="glass-card stack">
      <h3>{t('wrap_title')}</h3>
      <p className="text-soft">{t('wrap_empty')}</p>
      <Link className="btn" to="/day">{t('plan_my_day')} →</Link>
    </section>
  )
  return (
    <>
      <div ref={ref} className="wrap-card">
        <div className="wc-k">{t('wrap_title')}</div>
{name && <div className="wc-name">{t('wrap_for', { name })}</div>}
        <div className="wc-big">{avoided} <small>{t('wrap_unit')}</small></div>
        <div className="wc-sub">{t('wrap_sub')}</div>
        <div className="wc-grid">
          <div><span>{t('wrap_best')}</span><b>{top != null ? fmtHour(+top, lang) : '–'}</b></div>
          <div><span>{t('wrap_streak')}</span><b>🔥 {current}</b></div>
          <div><span>{t('wrap_stays')}</span><b>{stays}</b></div>
          <div><span>{t('wrap_outs')}</span><b>{outs}</b></div>
        </div>
        <p className="wc-fact">{t('wrap_fact', { n: avoided })}</p>
        <div className="wc-foot">Whiff · {t('tagline')}</div>
      </div>
      <button className="btn" onClick={share} disabled={busy}>{busy ? t('loading') : t('wrap_share')}</button>
      {err && <p className="text-soft text-sm" role="alert">{t('wrap_err')}</p>}
      <p className="text-soft text-sm" style={{ textAlign: 'center' }}>{t('wrap_note')}</p>
    </>
  )
}