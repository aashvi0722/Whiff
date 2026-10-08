const files = import.meta.glob('@contract/*.sample.json', {
  eager: true,
  import: 'default',
})

function sample(name) {
  const key = Object.keys(files).find((k) => k.endsWith(`/${name}.sample.json`))
  if (!key) throw new Error(`No sample named ${name}`)
  return files[key]
}

// Mock mode is ON unless VITE_USE_MOCK is exactly "false"
export const USE_MOCK = import.meta.env.VITE_USE_MOCK !== 'false'
const BASE = (import.meta.env.VITE_API_BASE_URL || '').replace(/\/$/, '')

export class ApiError extends Error {
  constructor(code, status) {
    super(code)
    this.code = code
    this.status = status
  }
}

// Mirrors how the stub API behaves, so mock and real feel the same
function mock(kind, defaultName, { scenario, replay }) {
  if (scenario === 'error') {
    const body = sample('error')
    throw new ApiError(body.error?.code ?? 'unknown', 503)
  }
  if (replay && kind === 'smoke') defaultName = 'smoke_replay'
  if (scenario && (scenario === kind || scenario.startsWith(`${kind}_`))) {
    try {
      return sample(scenario)
    } catch {
      /* unknown name: fall back to default */
    }
  }
  return sample(defaultName)
}

async function real(path, params) {
  if (!BASE) throw new ApiError('no_api_url', 0)
  const url = new URL(BASE + path)
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== '') url.searchParams.set(k, v)
  })
  let res
  try {
    res = await fetch(url)
  } catch {
    throw new ApiError('network', 0)
  }
  let body = null
  try {
    body = await res.json()
  } catch {
    /* no JSON body */
  }
  if (!res.ok) throw new ApiError(body?.error?.code ?? 'unknown', res.status)
  return body
}

async function call(kind, path, defaultName, params) {
  return USE_MOCK ? mock(kind, defaultName, params) : real(path, params)
}

export function getSmoke({ lat, lon, replay, scenario } = {}) {
  return call('smoke', '/smoke', 'smoke_high', { lat, lon, replay, scenario })
}

export function getDay({ lat, lon, audience, wake_h, replay, scenario } = {}) {
  return call('day', '/day', 'day_windows', { lat, lon, audience, wake_h, replay, scenario })
}

export function getHistory({ lat, lon, days = 7, scenario } = {}) {
  return call('history', '/history', 'history', { lat, lon, days, scenario })
}

export function getReplays({ scenario } = {}) {
  return call('replays', '/replays', 'replays', { scenario })
}