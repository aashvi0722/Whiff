import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import { getCity } from '../lib/api.js'

const Ctx = createContext(null)
const KEY = 'whiff_theme'
const RAD = Math.PI / 180

// Simplified NOAA sunrise/sunset (accurate to a few minutes, good enough for a theme switch)
function sunEvents(utcMidnightMs, lat, lon) {
  const d = new Date(utcMidnightMs)
  const doy = Math.floor((utcMidnightMs - Date.UTC(d.getUTCFullYear(), 0, 0)) / 86400000)
  const g = (2 * Math.PI / 365) * (doy - 1)
  const eq = 229.18 * (0.000075 + 0.001868 * Math.cos(g) - 0.032077 * Math.sin(g)
    - 0.014615 * Math.cos(2 * g) - 0.040849 * Math.sin(2 * g))
  const decl = 0.006918 - 0.399912 * Math.cos(g) + 0.070257 * Math.sin(g)
    - 0.006758 * Math.cos(2 * g) + 0.000907 * Math.sin(2 * g)
    - 0.002697 * Math.cos(3 * g) + 0.00148 * Math.sin(3 * g)
  const cosHa = Math.cos(90.833 * RAD) / (Math.cos(lat * RAD) * Math.cos(decl))
    - Math.tan(lat * RAD) * Math.tan(decl)
  if (cosHa > 1 || cosHa < -1) return null
  const ha = Math.acos(cosHa) / RAD
  return {
    rise: utcMidnightMs + (720 - 4 * (lon + ha) - eq) * 60000,
    set: utcMidnightMs + (720 - 4 * (lon - ha) - eq) * 60000,
  }
}

export function isDaylight(nowMs, lat, lon) {
  const d = new Date(nowMs)
  const base = Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate())
  for (const off of [-1, 0, 1]) {
    const ev = sunEvents(base + off * 86400000, lat, lon)
    if (ev && nowMs >= ev.rise && nowMs < ev.set) return true
  }
  return false
}

export function ThemeProvider({ children }) {
  const [mode, setModeState] = useState(() => {
    try { const m = localStorage.getItem(KEY); return ['auto', 'light', 'dark'].includes(m) ? m : 'auto' } catch { return 'auto' }
  })
  const [tick, setTick] = useState(0)
  useEffect(() => {
    const id = setInterval(() => setTick(x => x + 1), 60000)
    return () => clearInterval(id)
  }, [])

  const resolved = useMemo(() => {
    const url = new URLSearchParams(window.location.search).get('theme')
    if (url === 'light' || url === 'dark') return url
    if (mode !== 'auto') return mode
    const c = getCity()
    const h = new Date().getHours()
    const day = Number.isFinite(c.lat) && Number.isFinite(c.lon)
      ? isDaylight(Date.now(), c.lat, c.lon)
      : h >= 6 && h < 18
    return day ? 'light' : 'dark'
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [mode, tick])

  useEffect(() => {
    document.documentElement.dataset.theme = resolved
    const meta = document.querySelector('meta[name="theme-color"]')
    if (meta) meta.setAttribute('content', resolved === 'dark' ? '#090d1c' : '#dff7f2')
  }, [resolved])

  const setMode = useCallback(m => {
    setModeState(m)
    try { localStorage.setItem(KEY, m) } catch {}
  }, [])
  const cycle = useCallback(() => setMode(mode === 'auto' ? 'light' : mode === 'light' ? 'dark' : 'auto'), [mode, setMode])
  const value = useMemo(() => ({ mode, resolved, setMode, cycle }), [mode, resolved, setMode, cycle])
  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export function useTheme() {
  const v = useContext(Ctx)
  if (!v) throw new Error('useTheme must be used inside <ThemeProvider>')
  return v
}