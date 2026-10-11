import { useLang } from '../i18n/useLang.jsx'
export const AUD = [
  { id: 'general', icon: <><circle cx="12" cy="8" r="4" /><path d="M4 21c0-4 4-6 8-6s8 2 8 6" /></> },
  { id: 'sensitive', icon: <path d="M12 21s-8-5-8-11a4.5 4.5 0 0 1 8-2.5A4.5 4.5 0 0 1 20 10c0 6-8 11-8 11z" /> },
  { id: 'child', icon: <><circle cx="9" cy="8" r="3.5" /><circle cx="17" cy="10" r="2.5" /><path d="M2 20c0-4 3-6 7-6s7 2 7 6" /></> },
  { id: 'outdoor', icon: <><path d="M4 16a8 8 0 0 1 16 0z" /><path d="M2 19h20M12 8v4" /></> },
]
export default function AudienceCards({ value, onChange }) {
  const { t } = useLang()
  return (
    <div className="stack" role="radiogroup" aria-label={t('who_for')}>
      {AUD.map(o => {
        const on = value === o.id
        return (
          <button key={o.id} role="radio" aria-checked={on} className={'opt glass-card' + (on ? ' on' : '')} onClick={() => onChange(o.id)}>
            <span className="opt-ic"><svg className="ni" viewBox="0 0 24 24" aria-hidden="true">{o.icon}</svg></span>
            <span className="opt-tx"><strong>{t('aud_' + o.id)}</strong><span className="text-soft text-sm">{t('aud_' + o.id + '_d')}</span></span>
            <span className="opt-tick" aria-hidden="true"><svg className="ni" viewBox="0 0 24 24"><path d="M5 12l5 5 9-10" /></svg></span>
          </button>
        )
      })}
    </div>
  )
}