import { useLang } from '../i18n/useLang.jsx'
import { USE_MOCK } from '../lib/api.js'
import { replayLabelKey, isLimitation, clearReplay } from '../lib/replay.js'

export function ScreenSkeleton() {
  const { t } = useLang()
  return (
    <div className="stack" aria-busy="true" aria-label={t('loading')}>
      <div className="skeleton" style={{ minHeight: 70 }} />
      <div className="skeleton" style={{ minHeight: 300 }} />
      <div className="skeleton" />
      <div className="skeleton" />
    </div>
  )
}

export function ErrorCard({ onRetry }) {
  const { t } = useLang()
  return (
    <div className="glass-card stack" role="alert">
      <h3>{t('error_title')}</h3>
      <p className="text-soft">{t('error_body')}</p>
      <button className="btn" onClick={onRetry}>{t('retry')}</button>
    </div>
  )
}

export function Banners({ data }) {
  const { t, tryT, lang } = useLang()
  const stale = data?._stale || data?.data_quality?.stale
  const r = data?.replay
  const label = r ? tryT(replayLabelKey(r)) : null
  const asOf = r?.as_of
    ? new Date(r.as_of).toLocaleDateString(lang === 'hi' ? 'hi-IN' : 'en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    : ''
  return (
    <>
      {USE_MOCK && <div className="banner stale">🧪 {t('mock_banner')}</div>}
      {data?.mode === 'replay' && (
        <div className="banner replay" role="status">
          <div>
            <div>⏪ {t('replay_banner')}{label ? ` · ${label}` : ''}</div>
            {asOf && <div style={{ fontWeight: 500, fontSize: '.78rem' }}>{t('replay_as_of', { date: asOf })}</div>}
            {isLimitation(r?.event_id) && (
              <div style={{ fontWeight: 500, fontSize: '.78rem' }}>⚠ {t('replay_limit_tag')}: {t('replay_limit_note')}</div>
            )}
          </div>
          <button className="chip" style={{ marginLeft: 'auto' }} onClick={clearReplay}>{t('replay_exit')}</button>
        </div>
      )}
      {stale && <div className="banner stale">⏱ {t('stale')}</div>}
    </>
  )
}