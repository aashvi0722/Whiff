import { useEffect } from 'react'
import { getDayPlan } from '../lib/api.js'
import { useLang } from '../i18n/useLang.jsx'
import { enabled, show } from '../lib/notify.js'
import { todayKey } from '../lib/streak.js'
import { fmtHour } from '../lib/time.js'

export default function NudgeWatcher() {
  const { t, lang } = useLang()
  useEffect(() => {
    let day = null, timer
    const once = type => {
      const k = `whiff_nudged_${todayKey()}_${type}`
      try { if (localStorage.getItem(k)) return false; localStorage.setItem(k, '1') } catch { /* blocked */ }
      return true
    }
    const check = () => {
      if (!day || !enabled()) return
      const h = new Date().getHours()
      const first = [...(day.windows || [])].sort((a, b) => a.start_h - b.start_h)[0]
      if (day.day_state === 'windows' && first && h >= first.start_h && h <= first.end_h + 1 && once('go'))
        show(t('nt_go_title'), t('nt_go_body', { time: fmtHour(first.start_h, lang) }), 'whiff-go')
      else if (day.day_state !== 'windows' && once('stay'))
        show(t('nt_stay_title'), t('nt_stay_body'), 'whiff-stay')
    }
    getDayPlan().then(d => { day = d; check(); timer = setInterval(check, 60000) }).catch(() => {})
    return () => clearInterval(timer)
  }, [t, lang])
  return null
}