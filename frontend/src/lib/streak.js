const KEY = 'whiff_log_v1'
const pad = n => String(n).padStart(2, '0')
const dkey = d => `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`
export const todayKey = () => dkey(new Date())
const daysBetween = (a, b) => Math.round((a - b) / 86400000)

export function getLog() { try { return JSON.parse(localStorage.getItem(KEY)) || {} } catch { return {} } }
function save(log) {
  try { localStorage.setItem(KEY, JSON.stringify(log)) } catch { /* storage blocked */ }
  window.dispatchEvent(new Event('whiff-log'))
}

// a day counts if you made the smart choice: out in a clean window, or staying in on a bad day
export const counts = e => !!e && ((e.day_state === 'windows' && e.action === 'went_out') ||
  (e.day_state !== 'windows' && e.action === 'stayed_in'))

export function logAction({ day_state, action, exposure_avoided_hours, best_start_h }) {
  const log = getLog()
  log[todayKey()] = { date: todayKey(), day_state, action, exposure_avoided_hours: exposure_avoided_hours ?? 0, best_start_h: best_start_h ?? null }
  save(log)
}
export const resetLog = () => save({})

export function streakInfo(log = getLog(), now = new Date()) {
  const dates = Object.keys(log).sort()
  if (!dates.length) return { current: 0, best: 0 }
  const first = new Date(dates[0] + 'T00:00:00')
  const d = new Date(now); d.setHours(0, 0, 0, 0)
  if (!counts(log[dkey(d)])) d.setDate(d.getDate() - 1) // today is still open
  let current = 0, lastGrace = null
  while (d >= first) {
    if (counts(log[dkey(d)])) current++
    else if (lastGrace === null || daysBetween(d, lastGrace) <= -7) lastGrace = new Date(d) // one grace day per 7 days
    else break
    d.setDate(d.getDate() - 1)
  }
  let best = 0, run = 0
  for (let c = new Date(first); c <= now; c.setDate(c.getDate() + 1)) {
    run = counts(log[dkey(c)]) ? run + 1 : 0
    best = Math.max(best, run)
  }
  return { current, best }
}

export function last7(log = getLog(), now = new Date()) {
  return Array.from({ length: 7 }, (_, i) => {
    const d = new Date(now); d.setDate(d.getDate() - (6 - i))
    const e = log[dkey(d)]
    return { date: new Date(d), status: counts(e) ? 'ok' : e ? 'miss' : i === 6 ? 'open' : 'none' }
  })
}

// demo helper for filming only: fills the last 6 days
export function seedDemo() {
  const log = {}
  for (let i = 6; i >= 1; i--) {
    const d = new Date(); d.setDate(d.getDate() - i)
    const go = i % 3 !== 0
    log[dkey(d)] = { date: dkey(d), day_state: go ? 'windows' : 'stay_in', action: go ? 'went_out' : 'stayed_in',
      exposure_avoided_hours: 6 + i, best_start_h: 6, demo: true }
  }
  save({ ...log, ...getLog() })
}