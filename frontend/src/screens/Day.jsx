import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getDayPlan, getAudience } from '../lib/api.js'
import { useApi } from '../lib/useApi.js'
import { useLang } from '../i18n/useLang.jsx'
import HourBars from '../components/HourBars.jsx'
import { Banners, ErrorCard, ScreenSkeleton } from '../components/StateViews.jsx'
import { fmtHour, fmtRange } from '../lib/time.js'

const TINT = { windows: 'low', caution: 'medium', stay_in: 'high' }
const AUD = ['general', 'sensitive', 'child', 'outdoor']
const SWAPS = {
  general: ['yoga', 'stairs', 'dance'], sensitive: ['stretch', 'breathing'],
  child: ['games', 'dance'], outdoor: ['shade', 'shift'],
}

export default function Day() {
  const { t, tryT, lang } = useLang()
  const { status, data, reload } = useApi(getDayPlan)
  const state = data?.day_state

  useEffect(() => {
    if (!state) return
    document.body.dataset.risk = TINT[state] || 'low'
    return () => { delete document.body.dataset.risk }
  }, [state])

  if (status === 'loading') return <ScreenSkeleton />
  if (!data) return <ErrorCard onRetry={reload} />

  const aud = AUD.includes(data.audience) ? data.audience : AUD.includes(getAudience()) ? getAudience() : 'general'
  const windows = [...(data.windows || [])].sort((a, b) => (a.rank ?? 99) - (b.rank ?? 99))
  const top = windows[0]
  const others = windows.slice(1)
  const reasonsOf = w => (w.reason_codes || []).map(r => tryT(r.code, r.params)).filter(Boolean)
  const advice = (data.advice_codes || []).map(c => tryT(c)).filter(Boolean)
  const miss = data.data_quality?.missing_hours
  const nMiss = Array.isArray(miss) ? miss.length : Number(miss) || 0
  const cig = data.cigarette_equiv?.value
  const bestTime = data.best_hour != null ? fmtHour(data.best_hour, lang) : ''
  const swaps = SWAPS[aud]

  return (
    <>
      <Banners data={data} />

      <section className="hero-sec stack" style={{ gap: 6 }}>
        <div className="row between">
          <span className="pill">{t('aud_' + aud)}</span>
          <span className="pill">{t('state_' + state)}</span>
        </div>
        <h1 className="hero-title">{t('plan_title')}</h1>
      </section>

      <section className="glass-card">
        <div className="row between" style={{ marginBottom: 10 }}>
          <h3 className="card-title">{t('hourly_pm25')}</h3>
          <span className="text-soft text-sm">*{t('estimated')}</span>
        </div>
        <HourBars hours={data.hours} windows={windows} />
        {state === 'windows' && <p className="text-soft text-sm" style={{ marginTop: 8 }}>{t('legend_window')}</p>}
        {nMiss > 0 && <p className="text-soft text-sm" style={{ marginTop: 4 }}>{t('missing_note')}</p>}
      </section>

      {state === 'windows' && top && (
        <>
          <section className="glass-card stack" style={{ gap: 8 }}>
            <span className="eyebrow">{t('best_window')}</span>
            <div className="win-time">{fmtRange(top.start_h, top.end_h, lang)}</div>
            <ul className="dots">
              {reasonsOf(top).map((r, i) => <li key={i}>{r}</li>)}
              <li>{t('act_go_' + aud)}</li>
            </ul>
          </section>
          {others.length > 0 && (
            <section className="glass-card stack" style={{ gap: 10 }}>
              <span className="eyebrow">{t('other_windows')}</span>
              {others.map((w, i) => (
                <div key={i} className="win-row">
                  <div className="row between">
                    <strong>{fmtRange(w.start_h, w.end_h, lang)}</strong>
                    <span className="text-soft text-sm">{t('rank', { n: w.rank })}</span>
                  </div>
                  <p className="text-soft text-sm">{reasonsOf(w).join(' · ')}</p>
                </div>
              ))}
            </section>
          )}
        </>
      )}

      {state === 'caution' && (
        <section className="glass-card stack" style={{ gap: 8 }}>
          <h3>{t('caution_title')}</h3>
          <p className="text-soft">{t(aud === 'outdoor' ? 'caution_outdoor' : 'caution_body', { time: bestTime })}</p>
          <ul className="dots">{reasonsOf({ reason_codes: data.reason_codes }).map((r, i) => <li key={i}>{r}</li>)}</ul>
        </section>
      )}

      {state === 'stay_in' && (
        <section className="glass-card stack" style={{ gap: 8 }}>
          <h3>{t('stayin_title')}</h3>
          <p className="text-soft">{t('stayin_body')}</p>
        </section>
      )}

      {state !== 'windows' && (
        <section className="glass-card stack" style={{ gap: 10 }}>
          <span className="eyebrow">{t('swaps_title')}</span>
          <ul className="dots">{swaps.map(s => <li key={s}>{t('swap_' + s)}</li>)}</ul>
        </section>
      )}

      {advice.length > 0 && (
        <section className="glass-card stack" style={{ gap: 6 }}>
          <span className="eyebrow">{t('advice_title')}</span>
          <ul className="dots">{advice.map((a, i) => <li key={i}>{a}</li>)}</ul>
        </section>
      )}

      <div className="row stat-row">
        <div className="glass-card stat">
          <b>{data.exposure_avoided_hours ?? '–'}</b>
          <span className="text-soft text-sm">{t('avoided_long')}</span>
        </div>
        {cig != null && (
          <div className="glass-card stat">
            <b>≈ {cig}</b>
            <span className="text-soft text-sm">{t('cigarette_long')}</span>
          </div>
        )}
      </div>

      {state !== 'windows' && (
        <section className="glass-card stack" style={{ gap: 4 }}>
          <span className="eyebrow">{t('footprint_title')}</span>
          <p className="text-soft">{t('footprint_tip')}</p>
        </section>
      )}

      <Link className="btn ghost" to="/">← {t('nav_radar')}</Link>
      <p className="text-soft text-sm" style={{ textAlign: 'center' }}>{t('disclaimer')}</p>
    </>
  )
}