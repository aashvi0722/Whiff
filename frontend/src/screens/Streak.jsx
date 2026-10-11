import { useEffect, useState } from 'react'
import { useLang } from '../i18n/useLang.jsx'
import { getLog, streakInfo, last7, resetLog, seedDemo } from '../lib/streak.js'
import { Link } from 'react-router-dom'

export default function Streak() {
  const { t, lang } = useLang()
  const [log, setLog] = useState(getLog)
  useEffect(() => {
    const f = () => setLog(getLog())
    window.addEventListener('whiff-log', f)
    return () => window.removeEventListener('whiff-log', f)
  }, [])
  const demo = new URLSearchParams(window.location.search).get('demo') === '1'
  const { current, best } = streakInfo(log)
  const week = last7(log)
  const loc = lang === 'hi' ? 'hi-IN' : 'en-IN'
  const hasDemo = Object.values(log).some(e => e.demo)
  return (
    <>
      <section className="hero-sec stack" style={{ gap: 4 }}>
        <span className="eyebrow">{t('streak_title')}</span>
        <div className="big-streak">🔥 {current}</div>
        <p className="text-soft text-sm">{t('streak_best', { n: best })}</p>
      </section>
      {hasDemo && <div className="banner stale">🧪 {t('streak_demo_note')}</div>}
      <section className="glass-card stack" style={{ gap: 10 }}>
        <span className="eyebrow">{t('streak_last7')}</span>
        <div className="week">
          {week.map((d, i) => (
            <div key={i} className="wk">
              <span className={'dot ' + d.status}>{d.status === 'ok' ? '✓' : ''}</span>
              <span className="text-soft" style={{ fontSize: '.65rem' }}>{d.date.toLocaleDateString(loc, { weekday: 'short' })}</span>
            </div>
          ))}
        </div>
        {Object.keys(log).length === 0 && <p className="text-soft text-sm">{t('streak_empty')}</p>}
      </section>
      <section className="glass-card stack" style={{ gap: 6 }}>
        <span className="eyebrow">{t('streak_rules_title')}</span>
        <ul className="dots">
          <li>{t('streak_rule1')}</li><li>{t('streak_rule2')}</li><li>{t('streak_rule3')}</li>
        </ul>
        <p className="text-soft text-sm">{t('honor_note')}</p>
      </section>
      {demo && (
        <div className="row" style={{ gap: 8 }}>
          <button className="btn ghost" style={{ flex: 1 }} onClick={seedDemo}>{t('streak_seed')}</button>
          <button className="btn ghost" style={{ flex: 1 }} onClick={resetLog}>{t('streak_reset')}</button>
        </div>
      )}
      {<Link className="btn" to="/wrapped">{t('streak_share')}</Link>}
    </>
  )
}