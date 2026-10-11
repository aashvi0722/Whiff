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
  const opts = { body, icon: '/favicon.svg' }
  if (tag) { opts.tag = tag; opts.renotify = true }
  try {
    const reg = await navigator.serviceWorker?.getRegistration()
    if (reg) { await reg.showNotification(title, opts); return 'ok' }
  } catch { /* fall through to the page-level API */ }
  try { new Notification(title, opts); return 'ok' } catch { return 'failed' }
}