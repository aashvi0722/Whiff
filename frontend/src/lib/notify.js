const K = 'whiff_notif'
export const supported = () => typeof Notification !== 'undefined'
export const enabled = () => { try { return supported() && Notification.permission === 'granted' && localStorage.getItem(K) === '1' } catch { return false } }
export async function enable() {
  if (!supported()) return 'unsupported'
  const p = await Notification.requestPermission()
  if (p !== 'granted') return 'denied'
  try { localStorage.setItem(K, '1') } catch { /* blocked */ }
  return 'on'
}
export const disable = () => { try { localStorage.removeItem(K) } catch { /* blocked */ } }
export async function show(title, body, tag) {
  try {
    const reg = await navigator.serviceWorker?.getRegistration()
    if (reg) return await reg.showNotification(title, { body, tag, icon: '/favicon.svg' })
  } catch { /* fall through */ }
  try { new Notification(title, { body, tag }) } catch { /* unsupported */ }
}