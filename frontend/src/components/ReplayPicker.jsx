import { getReplays } from '../lib/api.js'
import { useApi } from '../lib/useApi.js'
import { useLang } from '../i18n/useLang.jsx'
import { currentReplay, setReplay, clearReplay, isLimitation } from '../lib/replay.js'

export default function ReplayPicker() {
  const { t, tryT } = useLang()
  const { status, data } = useApi(getReplays)
  const events = data?.events || []
  if (status === 'loading' || events.length === 0) return null
  const active = currentReplay()
  return (
    <section className="glass-card stack" style={{ gap: 10 }}>
      <span className="eyebrow">{t('replay_pick_title')}</span>
      <p className="text-soft text-sm">{t('replay_pick_hint')}</p>
      <div className="chips">
        {events.map(e => (
          <button key={e.event_id} className={'chip' + (active === e.event_id ? ' on' : '')}
                  aria-pressed={active === e.event_id} onClick={() => setReplay(e.event_id)}>
            {tryT(e.label_key) || e.event_id}{isLimitation(e.event_id) ? ' *' : ''}
          </button>
        ))}
        {active && <button className="chip" onClick={clearReplay}>{t('replay_exit')}</button>}
      </div>
      {events.some(e => isLimitation(e.event_id)) && (
        <p className="text-soft text-sm">* {t('replay_limit_tag')}: {t('replay_limit_note')}</p>
      )}
    </section>
  )
}