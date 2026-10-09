import { useLang } from '../i18n/useLang.jsx'

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
  const { t } = useLang()
  const stale = data?._stale || data?.data_quality?.stale
  return (
    <>
      {data?.mode === 'replay' && (
        <div className="banner replay">
          ⏪ {t('replay_banner')}{data.replay?.label ? ` · ${data.replay.label}` : ''}
        </div>
      )}
      {stale && <div className="banner stale">⏱ {t('stale')}</div>}
    </>
  )
}