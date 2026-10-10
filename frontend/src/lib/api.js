const files = import.meta.glob('@contract/*.sample.json', { eager: true, import: 'default' })

function sample(name) {
  const key = Object.keys(files).find((k) => k.endsWith(`/${name}.sample.json`))
  if (!key) throw new Error(`No sample named ${name}`)
  return files[key]
}

// Mock mode is ON unless VITE_USE_MOCK is exactly "false"
export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'
const BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

export class ApiError extends Error {
  constructor(code, status) { super(code); this.code = code; this.status = status }
}

const store = {
  get(k) { try { return localStorage.getItem(k) } catch { return null } },
  set(k, v) { try { localStorage.setItem(k, v) } catch {} },
}
const urlQS = () => new URLSearchParams(window.location.search)

const DEFAULT_CITY = { lat: 28.61, lon: 77.21 }
export function getCity() {
  try { return JSON.parse(store.get('whiff_city')) || DEFAULT_CITY } catch { return DEFAULT_CITY }
}
export const getAudience = () => store.get('whiff_audience') || 'general'

function mock(kind, defaultName, { scenario, replay }) {
  if (scenario === 'error') {
    const body = sample('error')
    throw new ApiError(body.error?.code ?? 'unknown', 503)
  }
  if (replay && kind === 'smoke') defaultName = 'smoke_replay'
  if (scenario && (scenario === kind || scenario.startsWith(`${kind}_`))) {
    try { return sample(scenario) } catch { /* unknown name: use default */ }
  }
  return sample(defaultName)
}

async function real(path, params) {
  if (!BASE) throw new ApiError('no_api_url', 0)
  const url = new URL(BASE + path)
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, v)
  })
  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), 8000)
  let res
  try { res = await fetch(url, { signal: ctrl.signal }) }
  catch { throw new ApiError('network', 0) }
  finally { clearTimeout(timer) }
  let body = null
  try { body = await res.json() } catch { /* no JSON body */ }
  if (!res.ok) throw new ApiError(body?.error?.code ?? 'unknown', res.status)
  return body
}

async function call(kind, path, defaultName, params) {
  const p = { ...params }
  if (p.scenario == null) p.scenario = urlQS().get('scenario') || undefined
  if (p.replay == null) p.replay = urlQS().get('replay') || undefined
  if (USE_MOCK) return mock(kind, defaultName, p)
  const key = `whiff_cache_${path}_${JSON.stringify(p)}`
  try {
    const data = await real(path, p)
    store.set(key, JSON.stringify(data))
    return data
  } catch (err) {
    const cached = p.scenario === 'error' ? null : store.get(key)
    if (cached) return { ...JSON.parse(cached), _stale: true }
    throw err
  }
}

export function getSmoke({ lat, lon, replay, scenario } = {}) {
  const c = getCity()
  return call('smoke', '/smoke', 'smoke_high', { lat: lat ?? c.lat, lon: lon ?? c.lon, replay, scenario })
}
export function getDay({ lat, lon, audience, wake_h, replay, scenario } = {}) {
  const c = getCity()
  return call('day', '/day', 'day_windows', {
    lat: lat ?? c.lat, lon: lon ?? c.lon, audience: audience ?? getAudience(), wake_h, replay, scenario,
  })
}
export function getHistory({ lat, lon, days = 7, scenario } = {}) {
  const c = getCity()
  return call('history', '/history', 'history', { lat: lat ?? c.lat, lon: lon ?? c.lon, days, scenario })
}
export function getReplays({ scenario } = {}) {
  return call('replays', '/replays', 'replays', { scenario, replay: '' })
}

// no-argument versions that the screens call
export const getSmokeRadar = () => getSmoke()
export const getDayPlan = () => getDay()