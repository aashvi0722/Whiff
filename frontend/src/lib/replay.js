export const LIMITATION_EVENTS = ['lucknow-2023-11']
export const isLimitation = id => LIMITATION_EVENTS.includes(id)
export const currentReplay = () => new URLSearchParams(window.location.search).get('replay')
// the query goes before the #, so use the URL API: the hash part is kept
function go(mutate) {
  const u = new URL(window.location.href)
  mutate(u.searchParams)
  window.location.href = u.toString()
}
export const setReplay = id => go(p => p.set('replay', id))
export const clearReplay = () => go(p => p.delete('replay'))
export const replayLabelKey = r =>
  r?.label_key || (r?.event_id ? 'replay_' + r.event_id.replace(/-/g, '_') : null)