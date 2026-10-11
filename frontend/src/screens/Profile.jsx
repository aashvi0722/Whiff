import { useState } from 'react'
import { useLang } from '../i18n/useLang.jsx'
import { useProfile, saveProfile } from '../lib/profile.js'
import AudienceCards, { AUD } from '../components/AudienceCards.jsx'
import LocationCard from '../components/LocationCard.jsx'
import ThemeCard from '../components/ThemeCard.jsx'
import NotifyCard from '../components/NotifyCard.jsx'

export default function Profile() {
  const { t } = useLang()
  const p = useProfile()
  const [step, setStep] = useState('view') // view | confirm | edit
  const [name, setName] = useState('')
  const [aud, setAud] = useState('general')
  const icon = AUD.find(a => a.id === p.audience)?.icon
  const startEdit = () => { setName(p.name); setAud(p.audience); setStep('edit') }
  const save = () => { saveProfile({ name, audience: aud }); setStep('view') }
  return (
    <>
      <section className="hero-sec stack" style={{ gap: 4 }}>
        <span className="eyebrow">{t('personalize')}</span>
        <h1 className="hero-title">{t('profile_title')}</h1>
      </section>

      {step !== 'edit' && (
        <section className="glass-card stack" style={{ gap: 12 }}>
          <div className="prof-card">
            <div className="avatar">{(p.name || '·').trim()[0]?.toUpperCase()}</div>
            <div className="stack" style={{ gap: 6 }}>
              <h2>{p.name ? t('prof_hello', { name: p.name }) : t('prof_friend')}</h2>
              <span className="pill"><svg className="ni" style={{ width: 16, height: 16 }} viewBox="0 0 24 24" aria-hidden="true">{icon}</svg>{t('aud_' + p.audience)}</span>
            </div>
          </div>
          <p className="text-soft text-sm">{t('prof_for')}: {t('aud_' + p.audience + '_d')}</p>
          {step === 'view' && <button className="btn ghost" onClick={() => setStep('confirm')}>{t('prof_change')}</button>}
          {step === 'confirm' && (
            <div className="stack" style={{ gap: 8 }}>
              <h3>{t('prof_confirm_title')}</h3>
              <p className="text-soft text-sm">{t('prof_confirm_body')}</p>
              <div className="row" style={{ gap: 8 }}>
                <button className="btn" style={{ flex: 1 }} onClick={startEdit}>{t('prof_confirm_yes')}</button>
                <button className="btn ghost" style={{ flex: 1 }} onClick={() => setStep('view')}>{t('prof_cancel')}</button>
              </div>
            </div>
          )}
        </section>
      )}

      {step === 'edit' && (
        <>
          <section className="glass-card stack" style={{ gap: 8 }}>
            <label className="eyebrow" htmlFor="nm2">{t('ob_name_label')}</label>
            <input id="nm2" className="field" value={name} maxLength={30} placeholder={t('ob_name_ph')} onChange={e => setName(e.target.value)} />
          </section>
          <AudienceCards value={aud} onChange={setAud} />
          <div className="row" style={{ gap: 8 }}>
            <button className="btn" style={{ flex: 1 }} onClick={save}>{t('prof_save')}</button>
            <button className="btn ghost" style={{ flex: 1 }} onClick={() => setStep('view')}>{t('prof_cancel')}</button>
          </div>
        </>
      )}

      {step !== 'edit' && <><LocationCard /><NotifyCard /><ThemeCard /></>}
      <p className="text-soft text-sm" style={{ textAlign: 'center' }}>{t('disclaimer')}</p>
    </>
  )
}