import { useState } from 'react'
import { useLang } from '../i18n/useLang.jsx'
import { saveProfile } from '../lib/profile.js'
import AudienceCards from '../components/AudienceCards.jsx'
export default function Onboarding() {
  const { t } = useLang()
  const [name, setName] = useState('')
  const [aud, setAud] = useState('general')
  return (
    <>
      <section className="hero-sec stack" style={{ gap: 6 }}>
        <h1 className="hero-title">{t('ob_title')}</h1>
        <p className="text-soft">{t('ob_sub')}</p>
      </section>
      <section className="glass-card stack" style={{ gap: 8 }}>
        <label className="eyebrow" htmlFor="nm">{t('ob_name_label')}</label>
        <input id="nm" className="field" value={name} maxLength={30} placeholder={t('ob_name_ph')}
               autoComplete="given-name" onChange={e => setName(e.target.value)} />
      </section>
      <span className="eyebrow">{t('who_for')}</span>
      <AudienceCards value={aud} onChange={setAud} />
      <button className="btn" onClick={() => saveProfile({ name, audience: aud })}>{t('ob_continue')}</button>
      <p className="text-soft text-sm" style={{ textAlign: 'center' }}>{t('ob_note')}</p>
      <p className="text-soft text-sm" style={{ textAlign: 'center' }}>{t('disclaimer')}</p>
    </>
  )
}