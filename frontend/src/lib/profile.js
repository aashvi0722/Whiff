import { useEffect, useState } from 'react'
const K = { name: 'whiff_name', aud: 'whiff_audience', ok: 'whiff_onboarded' }
const get = k => { try { return localStorage.getItem(k) } catch { return null } }
const set = (k, v) => { try { localStorage.setItem(k, v) } catch { /* blocked */ } }
let mem = null // fallback when storage is blocked
export const getProfile = () => mem || ({ name: get(K.name) || '', audience: get(K.aud) || 'general', onboarded: get(K.ok) === '1' })
export function saveProfile({ name = '', audience = 'general' }) {
  const n = name.trim().slice(0, 30)
  mem = { name: n, audience, onboarded: true }
  set(K.name, n); set(K.aud, audience); set(K.ok, '1')
  window.dispatchEvent(new Event('whiff-profile'))
}
export function useProfile() {
  const [p, setP] = useState(getProfile)
  useEffect(() => {
    const f = () => setP(getProfile())
    window.addEventListener('whiff-profile', f)
    return () => window.removeEventListener('whiff-profile', f)
  }, [])
  return p
}