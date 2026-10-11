import { useState } from 'react'
import { useLang } from '../i18n/useLang.jsx'
import { enable, disable, enabled, show } from '../lib/notify.js'

export default function NotifyCard() {
  const { t } = useLang()
  const [on, setOn] = useState(enabled)
  const [msg, setMsg] = useState('')
  const toggle = async () => {
    if (on) { disable(); setOn(false); return }
    const r = await enable()
    setOn(r === 'on')
    setMsg(r === 'denied' ? t('nt_denied') : r === 'unsupported' ? t('nt_unsupported') : '')
  }
  const sendTest = async () => {
    const r = await show(t('nt_test'), t('nt_test_body'), `whiff-test-${Date.now()}`)
    setMsg(r === 'ok' ? t('nt_sent') : t('nt_fail'))
  }
  return (
    <section className="glass-card stack" style={{ gap: 10 }}>
      <span className="eyebrow">{t('nt_title')}</span>
      <p className="text-soft text-sm">{t('nt_hint')}</p>
      <button className={on ? 'btn ghost' : 'btn'} onClick={toggle}>{on ? t('nt_off') : t('nt_on')}</button>
      {on && <button className="btn ghost" onClick={sendTest}>{t('nt_test')}</button>}
      {msg && <p className="text-soft text-sm" role="alert">{msg}</p>}
      <p className="text-soft text-sm">{t('nt_note')}</p>
    </section>
  )
}